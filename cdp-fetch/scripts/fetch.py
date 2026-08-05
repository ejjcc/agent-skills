#!/usr/bin/env python3
"""
Fetch URL via the shared CDP agent browser (localhost:9222).

绕过 Chromium CDP 的 Origin check (没有 --remote-allow-origins=*), 用 raw socket
手写 WebSocket handshake, 不发 Origin header.

复用用户登录态: 适合抓 X / Twitter / Lark / 内部站等需要 session 的内容.

用法:
  fetch.py <URL> [--selector <css>] [--wait <seconds>]
"""
import argparse
import base64
import json
import os
import socket
import struct
import sys
import time
import urllib.parse
import urllib.request


def cdp_create_tab(url: str) -> dict:
    """Create new tab via /json/new endpoint. Returns tab dict with id, webSocketDebuggerUrl."""
    req_url = f'http://127.0.0.1:9222/json/new?{urllib.parse.quote(url, safe="")}'
    resp = urllib.request.urlopen(
        urllib.request.Request(req_url, method='PUT'),
        timeout=10,
    ).read()
    return json.loads(resp)


def cdp_close_tab(tab_id: str):
    """Close tab via /json/close endpoint."""
    try:
        urllib.request.urlopen(f'http://127.0.0.1:9222/json/close/{tab_id}', timeout=5).read()
    except Exception:
        pass


def raw_ws_handshake(ws_url: str) -> socket.socket:
    """Manual WebSocket handshake WITHOUT Origin header (bypasses CDP origin checks)."""
    # Parse path from ws://127.0.0.1:9222/devtools/page/<id>
    if '9222' not in ws_url:
        raise ValueError(f'Unexpected ws_url: {ws_url}')
    path = ws_url.split('9222', 1)[1]
    sock = socket.socket()
    sock.settimeout(15)
    sock.connect(('127.0.0.1', 9222))
    key = base64.b64encode(os.urandom(16)).decode()
    hs = (
        f'GET {path} HTTP/1.1\r\n'
        f'Host: 127.0.0.1:9222\r\n'
        f'Upgrade: websocket\r\n'
        f'Connection: Upgrade\r\n'
        f'Sec-WebSocket-Key: {key}\r\n'
        f'Sec-WebSocket-Version: 13\r\n'
        f'\r\n'
    )
    sock.send(hs.encode())
    buf = b''
    while b'\r\n\r\n' not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            raise RuntimeError('WS handshake: connection closed')
        buf += chunk
    status_line = buf.split(b'\r\n', 1)[0].decode(errors='replace')
    if '101' not in status_line:
        raise RuntimeError(f'WS handshake failed: {status_line}')
    return sock


def ws_send(sock: socket.socket, data: str):
    """Send text frame with masking."""
    payload = data.encode('utf-8')
    mask = os.urandom(4)
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    frame = b'\x81'  # FIN + opcode=text
    L = len(payload)
    if L < 126:
        frame += bytes([0x80 | L])
    elif L < 65536:
        frame += b'\xfe' + struct.pack('>H', L)
    else:
        frame += b'\xff' + struct.pack('>Q', L)
    frame += mask + masked
    sock.send(frame)


def ws_recv(sock: socket.socket):
    """Receive one text frame. Returns None on EOF."""
    h = sock.recv(2)
    if len(h) < 2:
        return None
    L = h[1] & 0x7f
    if L == 126:
        L = struct.unpack('>H', sock.recv(2))[0]
    elif L == 127:
        L = struct.unpack('>Q', sock.recv(8))[0]
    buf = b''
    while len(buf) < L:
        chunk = sock.recv(min(65536, L - len(buf)))
        if not chunk:
            break
        buf += chunk
    return buf.decode('utf-8', errors='replace')


def cdp_evaluate(sock: socket.socket, expression: str, msg_id: int = 1, timeout_ms: int = 30000) -> str:
    """Send Runtime.evaluate and return the result value as string."""
    msg = json.dumps({
        'id': msg_id,
        'method': 'Runtime.evaluate',
        'params': {'expression': expression, 'returnByValue': True, 'timeout': timeout_ms},
    })
    ws_send(sock, msg)
    for _ in range(50):
        raw = ws_recv(sock)
        if raw is None:
            return ''
        try:
            j = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if j.get('id') == msg_id:
            return j.get('result', {}).get('result', {}).get('value', '')
    return ''


def main():
    parser = argparse.ArgumentParser(description='Fetch URL via the shared CDP agent browser')
    parser.add_argument('url', help='URL to fetch')
    parser.add_argument('--selector', default='article',
                        help='CSS selector to extract text from (default: article)')
    parser.add_argument('--wait', type=float, default=10.0,
                        help='Seconds to wait for page load (default: 10)')
    parser.add_argument('--max-chars', type=int, default=10000,
                        help='Max chars per element (default: 10000)')
    parser.add_argument('--max-elements', type=int, default=10,
                        help='Max elements to extract (default: 10)')
    parser.add_argument('--keep-open', action='store_true',
                        help='抓完不关闭 tab, 在 stderr 打印 KEPT_TAB <id>; '
                             '连续抓多个页面时用, 全部完成后用 close_tabs.py 统一关闭')
    args = parser.parse_args()

    # Test the shared CDP endpoint
    try:
        urllib.request.urlopen('http://127.0.0.1:9222/json/version', timeout=3).read()
    except Exception as e:
        print(f'ERROR: shared CDP agent browser not reachable at localhost:9222 ({e})', file=sys.stderr)
        print('Start a Chromium browser with --remote-debugging-port=9222 and log in first.', file=sys.stderr)
        sys.exit(2)

    tab = cdp_create_tab(args.url)
    tab_id = tab['id']
    ws_url = tab['webSocketDebuggerUrl']

    try:
        sock = raw_ws_handshake(ws_url)
        try:
            time.sleep(args.wait)
            # JS to extract elements
            js = f'''
                (() => {{
                    const els = document.querySelectorAll({json.dumps(args.selector)});
                    if (els.length === 0) {{
                        return 'NO_MATCH selector={json.dumps(args.selector)} title=' +
                               document.title +
                               ' body_len=' + (document.body.innerText.length || 0);
                    }}
                    const out = [];
                    els.forEach((e, i) => {{
                        if (i >= {args.max_elements}) return;
                        out.push('=== Element ' + (i + 1) + ' ===\\n' +
                                 e.innerText.substring(0, {args.max_chars}));
                    }});
                    return out.join('\\n\\n---\\n\\n');
                }})()
            '''
            result = cdp_evaluate(sock, js)
            print(result)
        finally:
            try:
                sock.close()
            except Exception:
                pass
    finally:
        if args.keep_open:
            print(f'KEPT_TAB {tab_id}', file=sys.stderr)
        else:
            cdp_close_tab(tab_id)


if __name__ == '__main__':
    main()
