#!/usr/bin/env python3
"""统一关闭 cdp-fetch --keep-open 留下的共享 CDP 浏览器 tab.

配合 fetch.py / capture.py 的 --keep-open: 连续抓多个页面时每次都加 --keep-open
保留 tab (stderr 打印 KEPT_TAB <id>), 所有任务完成后把收集到的 id 一次性传进来
统一关闭, 避免每读一页就开关一次 tab.

用法:
  close_tabs.py <tab_id> [<tab_id> ...]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import cdp_close_tab  # noqa: E402


def main():
    tab_ids = sys.argv[1:]
    if not tab_ids:
        print('用法: close_tabs.py <tab_id> [<tab_id> ...]', file=sys.stderr)
        sys.exit(1)
    for tab_id in tab_ids:
        cdp_close_tab(tab_id)
        print(f'CLOSED {tab_id}')


if __name__ == '__main__':
    main()
