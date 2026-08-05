#!/usr/bin/env python3
"""
Capture network traffic via the shared CDP agent browser at localhost:9222.

关键: Network.enable 在 Page.navigate 之前发, 所以登录态页面发出的全部
XHR/fetch 请求 (含 Authorization / Cookie / x-csrf-token 等 header, 以及 JSON
响应体) 都能完整抓到. 复用共享 CDP profile session, 适合提取需要登录态的内部 API / Token.

复用 fetch.py 的 raw-socket WS 机制 (绕过 Origin check); 发送端直接 import,
接收端本文件实现了带分片重组的 recv_message (getResponseBody 大响应体会被分成
多个 WS 帧, fetch.py 的单帧 ws_recv 处理不了).

用法:
  capture.py <URL> [--wait 15] [--filter <substr>] [--types xhr,fetch]
             [--body] [--headers] [--max 50] [--json]
"""
import argparse
import json
import os
import select
import struct
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import cdp_create_tab, cdp_close_tab, raw_ws_handshake, ws_send  # noqa: E402


def cdp_send(sock, msg_id, method, params=None):
    ws_send(sock, json.dumps({'id': msg_id, 'method': method, 'params': params or {}}))


def _recvn(sock, n):
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def _recv_frame(sock):
    """Read one WS frame -> (fin, opcode, payload) or None on EOF."""
    h = _recvn(sock, 2)
    if h is None:
        return None
    fin = (h[0] & 0x80) != 0
    opcode = h[0] & 0x0f
    L = h[1] & 0x7f
    if L == 126:
        ext = _recvn(sock, 2)
        L = struct.unpack('>H', ext)[0] if ext else 0
    elif L == 127:
        ext = _recvn(sock, 8)
        L = struct.unpack('>Q', ext)[0] if ext else 0
    payload = _recvn(sock, L) if L else b''
    return fin, opcode, (payload or b'')


def recv_message(sock):
    """Assemble one full WS text message (handles fragmentation). Returns str or None."""
    data = b''
    while True:
        frame = _recv_frame(sock)
        if frame is None:
            return None
        fin, opcode, payload = frame
        if opcode == 0x8:        # close
            return None
        if opcode in (0x9, 0xA):  # ping / pong -> ignore
            continue
        data += payload
        if fin:
            return data.decode('utf-8', errors='replace')


def wait_for_id(sock, msg_id, timeout=5.0):
    """Read frames until the response with matching id arrives (skips events)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        r, _, _ = select.select([sock], [], [], max(0.05, deadline - time.time()))
        if not r:
            return None
        raw = recv_message(sock)
        if raw is None:
            return None
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if msg.get('id') == msg_id:
            return msg
    return None


def main():
    p = argparse.ArgumentParser(description='Capture network traffic via the shared CDP agent browser')
    p.add_argument('url', help='URL to load and capture')
    p.add_argument('--wait', type=float, default=15.0, help='Seconds to collect events (default 15)')
    p.add_argument('--filter', default='', help='Only keep requests whose URL contains this substring')
    p.add_argument('--types', default='XHR,Fetch',
                   help='Comma resource types to keep, or "all" (default: XHR,Fetch)')
    p.add_argument('--body', action='store_true', help='Also fetch response bodies for matched requests')
    p.add_argument('--headers', action='store_true',
                   help='Include request/response headers (captures Authorization / Cookie / tokens)')
    p.add_argument('--max', type=int, default=50, help='Max requests to output (default 50)')
    p.add_argument('--json', action='store_true', help='Output JSON instead of text')
    p.add_argument('--keep-open', action='store_true',
                   help='抓完不关闭 tab, 在 stderr 打印 KEPT_TAB <id>; '
                        '连续抓多个页面时用, 全部完成后用 close_tabs.py 统一关闭')
    args = p.parse_args()

    types = None if args.types.lower() == 'all' else {t.strip().lower() for t in args.types.split(',')}

    try:
        urllib.request.urlopen('http://127.0.0.1:9222/json/version', timeout=3).read()
    except Exception as e:
        print(f'ERROR: shared CDP agent browser not reachable at localhost:9222 ({e})', file=sys.stderr)
        print('Start a Chromium browser with --remote-debugging-port=9222 and log in first.', file=sys.stderr)
        sys.exit(2)

    # Blank tab first so Network.enable lands BEFORE navigation -> capture everything.
    tab = cdp_create_tab('about:blank')
    tab_id = tab['id']
    sock = raw_ws_handshake(tab['webSocketDebuggerUrl'])

    requests, responses, order = {}, {}, []

    try:
        cdp_send(sock, 1, 'Network.enable')
        cdp_send(sock, 2, 'Page.enable')
        cdp_send(sock, 3, 'Page.navigate', {'url': args.url})

        deadline = time.time() + args.wait
        while time.time() < deadline:
            r, _, _ = select.select([sock], [], [], min(1.0, max(0.05, deadline - time.time())))
            if not r:
                continue
            raw = recv_message(sock)
            if raw is None:
                break
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue
            method, params = msg.get('method'), msg.get('params', {})
            if method == 'Network.requestWillBeSent':
                rid = params.get('requestId')
                req = params.get('request', {})
                if rid not in requests:
                    order.append(rid)
                requests[rid] = {
                    'method': req.get('method'),
                    'url': req.get('url', ''),
                    'type': params.get('type', ''),
                    'postData': req.get('postData'),
                    'reqHeaders': req.get('headers', {}),
                }
            elif method == 'Network.responseReceived':
                rid = params.get('requestId')
                resp = params.get('response', {})
                responses[rid] = {
                    'status': resp.get('status'),
                    'mimeType': resp.get('mimeType'),
                    'respHeaders': resp.get('headers', {}),
                }

        def keep(rid):
            req = requests.get(rid, {})
            url = req.get('url', '') or ''
            if url.startswith('data:'):
                return False
            if args.filter and args.filter not in url:
                return False
            if types is not None and (req.get('type', '') or '').lower() not in types:
                return False
            return True

        kept = [rid for rid in order if keep(rid)][:args.max]

        bodies = {}
        if args.body:
            mid = 100
            for rid in kept:
                cdp_send(sock, mid, 'Network.getResponseBody', {'requestId': rid})
                got = wait_for_id(sock, mid, timeout=5)
                if got and 'result' in got:
                    res = got['result']
                    body = res.get('body', '')
                    bodies[rid] = (f'<base64 {len(body)} bytes>'
                                   if res.get('base64Encoded') else body[:4000])
                mid += 1

        out = []
        for rid in kept:
            req, resp = requests.get(rid, {}), responses.get(rid, {})
            entry = {
                'method': req.get('method'),
                'status': resp.get('status'),
                'type': req.get('type'),
                'mimeType': resp.get('mimeType'),
                'url': req.get('url'),
            }
            if args.headers:
                entry['reqHeaders'] = req.get('reqHeaders', {})
                entry['respHeaders'] = resp.get('respHeaders', {})
            if req.get('postData'):
                entry['postData'] = req['postData'][:2000]
            if rid in bodies:
                entry['body'] = bodies[rid]
            out.append(entry)

        if args.json:
            print(json.dumps(out, ensure_ascii=False, indent=2))
            return

        if not out:
            print(f'NO_REQUESTS matched (filter={args.filter!r} types={args.types}). '
                  f'Try --wait 25, --types all, or a different --filter.')
            return
        for e in out:
            print(f"[{e.get('status') or '---'}] {e.get('method')} {e.get('type')} {e.get('url')}")
            if e.get('mimeType'):
                print(f"    mime: {e['mimeType']}")
            if args.headers:
                for k, v in (e.get('reqHeaders') or {}).items():
                    if k.lower() in ('authorization', 'cookie', 'x-csrf-token',
                                     'x-guest-token', 'x-api-key', 'x-xsrf-token'):
                        print(f"    req {k}: {v}")
            if e.get('postData'):
                print(f"    postData: {e['postData']}")
            if e.get('body') is not None:
                print(f"    body: {e['body']}")
            print()
    finally:
        try:
            sock.close()
        except Exception:
            pass
        if args.keep_open:
            print(f'KEPT_TAB {tab_id}', file=sys.stderr)
        else:
            cdp_close_tab(tab_id)


if __name__ == '__main__':
    main()
