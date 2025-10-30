#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import csv
import os
from typing import Dict
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_CANDIDATES = [
    os.path.join(SCRIPT_DIR, '..', 'src'),
    os.path.join(SCRIPT_DIR, 'src'),
]
for _cand in SRC_CANDIDATES:
    if os.path.isdir(_cand):
        SRC_DIR = os.path.abspath(_cand)
        break
else:
    SRC_DIR = SCRIPT_DIR

PATH_NAME = os.path.join(SRC_DIR, 'n_name.csv')
PATH_PROB = os.path.join(SRC_DIR, 'n_problem.csv')
PATH_SUBM = os.path.join(SRC_DIR, 'n_sub.csv')
PATH_RESULT = os.path.join(SRC_DIR, 'result.csv')
PATH_OJ = os.path.join(SRC_DIR, 'oj_sub.csv')

# 目标表头
RESULT_FIELDS = ['id', 'uid' ,'problem', 'school', 'username', 'realname', 'status', 'submit_time']


def read_csv(path: str):
    # 兼容 UTF-8 与带 BOM
    with open(path, 'r', encoding='utf-8-sig', newline='') as f:
        # 自动方言较慢，但这里数据量不大
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def normalize_time(s: str) -> str:
    """将各种时间字符串规范为 'YYYY-MM-DD HH:MM:SS'；解析失败则原样返回。
    支持的示例：
    - 2025-10-18 13:00:51
    - 25/10/2025 12:40:28
    - 2025/10/18 13:00:51
    - 2025-10-18T13:00:51
    """
    if not s:
        return s
    s = s.strip().replace('\u200b', '')  # 清理零宽字符
    fmts = [
        '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y %H:%M:%S',
        '%Y/%m/%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            pass
    return s


def load_user_map() -> Dict[str, Dict[str, str]]:
    user_map: Dict[str, Dict[str, str]] = {}
    rows = read_csv(PATH_NAME)
    for r in rows:
        uid = (r.get('用户ID') or '').strip()
        if not uid:
            continue
        user_map[uid] = {
            '学校': (r.get('学校') or '').strip(),
            '昵称': (r.get('昵称') or '').strip(),
            '真实名称': (r.get('真实名称') or '').strip(),
        }
    return user_map


def load_problem_map() -> Dict[str, str]:
    prob_map: Dict[str, str] = {}
    rows = read_csv(PATH_PROB)
    # n_problem.csv: id,name
    for r in rows:
        pid = (r.get('id') or '').strip()
        name = (r.get('name') or '').strip()
        if name:
            prob_map[name] = pid
    return prob_map


def load_existing_ids(path_result: str) -> set[str]:
    if not os.path.exists(path_result) or os.path.getsize(path_result) == 0:
        return set()
    existing_ids: set[str] = set()
    with open(path_result, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        # 如果列名不匹配，依旧尝试按第一列读取 id
        if reader.fieldnames and 'id' in reader.fieldnames:
            for r in reader:
                sid = (r.get('id') or '').strip()
                if sid:
                    existing_ids.add(sid)
        else:
            # 退化处理：逐行读取首列
            f.seek(0)
            raw = list(csv.reader(f))
            if raw:
                for row in raw[1:]:
                    if row:
                        existing_ids.add(row[0].strip())
    return existing_ids


def ensure_result_header(path_result: str, overwrite: bool = False):
    write_header = False
    if overwrite:
        write_header = True
    elif not os.path.exists(path_result) or os.path.getsize(path_result) == 0:
        write_header = True
    else:
        # 检查首行是否匹配目标表头
        with open(path_result, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
            except StopIteration:
                write_header = True
            else:
                if header != RESULT_FIELDS:
                    pass
    if write_header:
        with open(path_result, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=RESULT_FIELDS)
            writer.writeheader()


def get_max_result_id(path_result: str) -> int:
    """读取 result.csv，返回可解析为 int 的最大 id；若没有则返回 0。"""
    if not os.path.exists(path_result) or os.path.getsize(path_result) == 0:
        return 0
    max_id = 0
    with open(path_result, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            sid = (r.get('id') or '').strip()
            if sid.isdigit():
                try:
                    max_id = max(max_id, int(sid))
                except ValueError:
                    continue
    return max_id


def merge_and_append():
    # 载入映射
    user_map = load_user_map()
    prob_map = load_problem_map()

    # 是否覆盖式重建
    overwrite = os.environ.get('MERGE_OVERWRITE') == '1'

    # 准备 result.csv
    ensure_result_header(PATH_RESULT, overwrite=overwrite)
    existing_ids = set() if overwrite else load_existing_ids(PATH_RESULT)

    # 读取提交记录
    submissions = read_csv(PATH_SUBM)

    appended = 0
    skipped_no_user = 0
    with open(PATH_RESULT, 'a', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_FIELDS)
        for r in submissions:
            sid = (r.get('提交id') or '').strip()
            if not sid:
                continue
            if sid in existing_ids:
                # 已存在，跳过
                continue

            uid = (r.get('用户id') or '').strip()
            prob_name = (r.get('题目名称') or '').strip()
            submit_time = (r.get('提交时间') or '').strip()
            submit_status = (r.get('提交状态') or '').strip()

            # 用户信息：若找不到用户，整条记录跳过
            if uid not in user_map:
                skipped_no_user += 1
                continue
            uinfo = user_map.get(uid, {})
            school = uinfo.get('学校', '')
            # 字段严格对应：username=昵称，realname=真实名称
            username = uinfo.get('昵称', '')
            realname = uinfo.get('真实名称', '')

            # 题目编号
            prob_id = prob_map.get(prob_name, '')

            # 状态
            status = '1' if submit_status == '答案正确' else '0'

            out = {
                'id': sid,
                'uid': uid,
                'problem': prob_id,
                'school': school,
                'username': username,
                'realname': realname,
                'status': status,
                'submit_time': normalize_time(submit_time),
            }
            writer.writerow(out)
            appended += 1

    return appended, len(submissions), skipped_no_user


def append_oj_sub():
    if not os.path.exists(PATH_OJ) or os.path.getsize(PATH_OJ) == 0:
        return 0, 0

    with open(PATH_OJ, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        return 0, 0

    base_id = get_max_result_id(PATH_RESULT)
    appended = 0
    with open(PATH_RESULT, 'a', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_FIELDS)
        for idx, r in enumerate(rows, start=1):
            problem = (r.get('display_id') or '').strip()
            school = '山西大学'
            username = (r.get('username') or '').strip()
            realname = (r.get('realname') or '').strip()
            st_raw = (r.get('status') or '').strip()
            status = '1' if st_raw in {'1', 'Accepted', 'AC', '答案正确'} else '0'
            submit_time = (r.get('submit_time') or r.get('gmt_create') or '').strip()

            out = {
                'id': str(base_id + idx),
                'problem': problem,
                'school': school,
                'username': username,
                'realname': realname,
                'status': status,
                'submit_time': normalize_time(submit_time),
            }
            writer.writerow(out)
            appended += 1

    return appended, len(rows)


if __name__ == '__main__':
    appended, total, skipped_no_user = merge_and_append()
    mode = 'overwrite' if os.environ.get('MERGE_OVERWRITE') == '1' else 'append'
    print(f"Processed {total} submissions, mode={mode}, wrote {appended} rows to result.csv, skipped_no_user={skipped_no_user}")

    # 可选：追加 oj_sub.csv（通过环境变量 APPEND_OJ 控制）
    if os.environ.get('APPEND_OJ') == '1':
        oj_appended, oj_total = append_oj_sub()
        print(f"Appended oj_sub: total={oj_total}, appended={oj_appended}")
