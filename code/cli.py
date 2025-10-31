#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from __future__ import annotations
import argparse
import os
import runpy
import sys
from pathlib import Path


PROJ_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = PROJ_ROOT / 'code'


def run_merge(overwrite: bool, append_oj: bool) -> None:
    # 为复用 merge_submissions.py 中现有逻辑，这里用环境变量控制覆盖/追加
    old_overwrite = os.environ.get('MERGE_OVERWRITE')
    old_append_oj = os.environ.get('APPEND_OJ')
    try:
        os.environ['MERGE_OVERWRITE'] = '1' if overwrite else ''
        os.environ['APPEND_OJ'] = '1' if append_oj else ''

        # 通过 runpy 按路径加载（避免包导入需求），并调用返回的函数对象
        import runpy
        ns = runpy.run_path(str(CODE_DIR / 'merge_submissions.py'), run_name='__not_main__')

        appended, total, skipped_no_user = ns['merge_and_append']()
        mode = 'overwrite' if overwrite else 'append'
        print(f"[merge] Processed {total} submissions, mode={mode}, wrote {appended} rows, skipped_no_user={skipped_no_user}")

        if append_oj:
            oj_appended, oj_total = ns['append_oj_sub']()
            print(f"[merge] Appended oj_sub: total={oj_total}, appended={oj_appended}")
    finally:
        # 还原环境变量
        if old_overwrite is None:
            os.environ.pop('MERGE_OVERWRITE', None)
        else:
            os.environ['MERGE_OVERWRITE'] = old_overwrite
        if old_append_oj is None:
            os.environ.pop('APPEND_OJ', None)
        else:
            os.environ['APPEND_OJ'] = old_append_oj


def run_convert() -> None:
    # 直接执行 convert.py 文件（其内部会写 converted.ndjson 到项目根）
    convert_path = CODE_DIR / 'convert.py'
    if not convert_path.exists():
        print(f"[convert] convert.py not found at {convert_path}", file=sys.stderr)
        sys.exit(1)
    runpy.run_path(str(convert_path), run_name='__main__')


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Data Merge & Convert CLI')
    sub = p.add_subparsers(dest='command')

    # all
    sp_all = sub.add_parser('all', help='先合并再转换（默认）')
    sp_all.add_argument('--overwrite', action='store_true', help='覆盖式重建 result.csv')
    sp_all.add_argument('--append-oj', action='store_true', help='追加导入 oj_sub.csv')

    # merge only
    sp_merge = sub.add_parser('merge', help='仅执行合并（步骤一）')
    sp_merge.add_argument('--overwrite', action='store_true', help='覆盖式重建 result.csv')
    sp_merge.add_argument('--append-oj', action='store_true', help='追加导入 oj_sub.csv')

    # convert only
    sub.add_parser('convert', help='仅执行转换（步骤二）')

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # 无子命令时显示帮助而不是默认执行 all
    if args.command is None:
        parser.print_help()
        return 0
    cmd = args.command
    if cmd == 'merge':
        run_merge(overwrite=getattr(args, 'overwrite', False), append_oj=getattr(args, 'append_oj', False))
        return 0
    elif cmd == 'convert':
        run_convert()
        return 0
    elif cmd == 'all':
        run_merge(overwrite=getattr(args, 'overwrite', False), append_oj=getattr(args, 'append_oj', False))
        run_convert()
        return 0
    else:
        parser.print_help()
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
