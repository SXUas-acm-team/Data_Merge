from pathlib import Path
import buildEvent as be
from datetime import datetime
import datetime as dt
import ndjson
import yaml
import csv

# 统一的数据读取目录：优先从 /src 读取，兼容性回退到 /code
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
CODE_DIR = PROJECT_ROOT / "code"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
output_path = OUTPUT_DIR / "converted.ndjson"
event_file = open(output_path, 'a', encoding='utf-8')
with open(output_path, 'w', encoding='utf-8') as f:
    pass
print(f"Wrote NDJSON to: {output_path}")
def input_path(name: str) -> Path:
    p = SRC_DIR / name
    if p.exists():
        return p
    # fallback for backward compatibility
    return (CODE_DIR / name)

def parse_submission_time(s: str) -> dt.datetime:
    s = (s or "").strip()
    fmts = [
        '%Y-%m-%d %H:%M:%S',
        '%Y/%m/%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y/%m/%d %H:%M',
        '%Y-%m-%dT%H:%M:%S',
    ]
    for fmt in fmts:
        try:
            return dt.datetime.strptime(s, fmt)
        except Exception:
            pass
    # 尝试补齐秒
    if len(s) == 16:
        try:
            return dt.datetime.strptime(s + ':00', '%Y-%m-%d %H:%M:%S')
        except Exception:
            pass
    raise ValueError(f"Unrecognized time format: {s}")

# 读取配置文件
with open(input_path('contest-info.yaml'), encoding='utf-8') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

# 是否在队伍显示名中包含学校（"学校 - 姓名"），默认 False 仅显示姓名
# 支持多种配置键名以兼容不同写法
display_with_school = bool(
    cfg.get(
        'display_team_name_with_school',
        cfg.get('display-team-name-with-school', cfg.get('display-team-name-with school', False))
    )
)

# 首先格式化配置文件中的时间
contest_name = str(cfg["contest-name"])
contest_init_time = dt.datetime.strptime(str(cfg["contest-init-time"]), '%Y-%m-%d %H:%M:%S')
contest_start_time = dt.datetime.strptime(str(cfg["contest-start-time"]), '%Y-%m-%d %H:%M:%S')
contest_frozen_time = dt.datetime.strptime(str(cfg["contest-frozen-time"]), '%Y-%m-%d %H:%M:%S')
contest_end_time = dt.datetime.strptime(str(cfg["contest-end-time"]), '%Y-%m-%d %H:%M:%S')
contest_finalize_time = dt.datetime.strptime(str(cfg["contest-finalize-time"]), '%Y-%m-%d %H:%M:%S')

# 开始处理event：固定头
events = []
token_cnt = [0]
be.build_contest_info(token_cnt, contest_name, contest_start_time, contest_end_time, contest_frozen_time, contest_init_time, events)

# 判题类型
be.build_result_info(token_cnt, "AC", contest_init_time, "correct", False, True, events)
be.build_result_info(token_cnt, "CE", contest_init_time, "compiler error", False, False, events)
be.build_result_info(token_cnt, "MLE", contest_init_time, "memory limit", True, False, events)
be.build_result_info(token_cnt, "NO", contest_init_time, "no output", True, False, events)
be.build_result_info(token_cnt, "OLE", contest_init_time, "output limit", True, False, events)
be.build_result_info(token_cnt, "RTE", contest_init_time, "run error", True, False, events)
be.build_result_info(token_cnt, "TLE", contest_init_time, "timelimit", True, False, events)
be.build_result_info(token_cnt, "WA", contest_init_time, "wrong answer", True, False, events)

# 允许的语言
be.build_language_info(token_cnt, "c", "ac6b2c3be82211958c91cde21f27fd26", "gcc --version", "C", ["c"], 1.0, contest_init_time, events)
be.build_language_info(token_cnt, "cpp", "62531e780378bb346939d18aacdfff1c", "g++ --version", "C++", ["cpp","cc","cxx","c++"], 1.0, contest_init_time, events)
be.build_language_info_with_runner(token_cnt, "java", "86ba56cb70a79a32c0382214beda8faa", "javac -version","java -version", "Java", ["java"], 1.0, "Main class", contest_init_time, events)
be.build_language_info_with_runner(token_cnt, "python3", "4e301e4bc46ab73673e209ee3437707d", "pypy3 --version","pypy3 --version", "Python 3", ["py"], 1.0, "Main file", contest_init_time, events)

result_csv_path = OUTPUT_DIR / "result.csv"
if not result_csv_path.exists() or result_csv_path.stat().st_size == 0:
    raise SystemExit(f"result.csv not found or empty at {result_csv_path}")

result_rows = []
with open(result_csv_path, "r", encoding="utf-8-sig", newline='') as result_csv:
    reader = csv.reader(result_csv)
    try:
        header = next(reader)
    except StopIteration:
        header = None
    for row in reader:
        if row:
            result_rows.append(row)

# 题目集合：直接从 result.csv 的第 3 列(problem)收集，按字母排序
problem_ids = []
seen = set()
for row in result_rows:
    pid = (row[2] or "").strip()
    if not pid:
        continue
    if pid not in seen:
        seen.add(pid)
        problem_ids.append(pid)
problem_ids.sort()

# 输出题目事件
for i, pid in enumerate(problem_ids, start=1):
    be.build_problem_info(token_cnt, pid, i, 1.0, contest_init_time, events)

# 校验集合
valid_problem_ids = set(problem_ids)


# 用户组（参赛选手）
be.build_group_info(token_cnt, "participants", False, 1, contest_init_time, events)

# 学校信息：仅从 result.csv 去重统计
school_info_set = set()
for row in result_rows:
    if len(row) > 3:
        school = (row[3] or "").strip()
        if school:
            school_info_set.add(school)

# 直接以学校名作为 organization 的 id
created_schools = set()
for name in sorted(school_info_set):
    be.build_school_info(token_cnt, name, name, name, "CHN", contest_init_time, events)
    created_schools.add(name)

"""
仅从 result.csv 构建：
- uid: 第2列
- school: 第4列
- username: 第5列
- realname: 第6列
"""
team_info_id = {}  # key=(source, uid) -> (school, name, team_id_int)
used_team_ids = set()
auto_team_id_base = 2000000000  # 非牛客来源的自增起点
next_auto_id = auto_team_id_base
for row in result_rows:
    if not row:
        continue

    uid = (row[1] or '').strip()
    if not uid:
        continue
    source = (row[8] if len(row) > 8 else '').strip().lower()
    key = (source or 'nowcoder', uid)
    if key in team_info_id:
        continue
    school_r = (row[3] or '').strip()
    username_r = (row[4] or '').strip()
    realname_r = (row[5] or '').strip()
    if school_r and school_r not in created_schools:
        be.build_school_info(token_cnt, school_r, school_r, school_r, "CHN", contest_init_time, events)
        created_schools.add(school_r)
    name_r = realname_r or username_r or uid
    # 分配队伍 ID：nowcoder 且 uid 为纯数字时使用 uid；否则使用高位段自增
    team_id_int = None
    if (source == 'nowcoder' or source == '') and uid.isdigit():
        team_id_int = int(uid)
        # 冲突保护
        if team_id_int in used_team_ids:
            # 极少出现：允许改用自增段
            while next_auto_id in used_team_ids:
                next_auto_id += 1
            team_id_int = next_auto_id
            used_team_ids.add(team_id_int)
            next_auto_id += 1
        else:
            used_team_ids.add(team_id_int)
    else:
        while next_auto_id in used_team_ids:
            next_auto_id += 1
        team_id_int = next_auto_id
        used_team_ids.add(team_id_int)
        next_auto_id += 1
    team_info_id[key] = [school_r, name_r, team_id_int]

for (_source, _uid), (school_name, name, team_id) in team_info_id.items():
    # 根据配置决定队伍显示名：学校 - 姓名 或 仅姓名
    display_name = f"{school_name} - {name}" if display_with_school and str(school_name).strip() else str(name)
    org_id = school_name if school_name else ""
    if org_id and org_id not in created_schools:
        be.build_school_info(token_cnt, org_id, org_id, org_id, "CHN", contest_init_time, events)
        created_schools.add(org_id)
    be.build_team_info(token_cnt, team_id, org_id, False, "participants", school_name, "CHN", display_name, contest_init_time, events)

# 账户（过滤占位名）
for (_source, _uid), (school_name, name, team_id) in team_info_id.items():
    if name == "真实名称":
        continue
    # 账户展示同队伍名策略
    display_name = f"{school_name} - {name}" if display_with_school and str(school_name).strip() else str(name)
    be.build_user_info(token_cnt, team_id, team_id, display_name, contest_init_time, events)

# 添加比赛开始信息
be.build_update_info(token_cnt, contest_start_time, None, None, None, contest_init_time, events)

# 处理提交信息：直接使用内存里的 result_rows
status_idx = 6
submit_seq = 0
for row in result_rows:
    if not row:
        continue
    submit_seq += 1
    uid = (row[1] or '').strip()
    source = (row[8] if len(row) > 8 else '').strip().lower()
    raw_problem = (row[2] or '').strip()
    team_entry = team_info_id.get((source or 'nowcoder', uid))
    if not team_entry:
        # 未在名单中的提交（极少数），跳过
        continue
    submission_time_unformatted = row[7]
    # 将 result.csv 的状态规范化（避免 '1'/'0' 被当作 WA）
    raw_status = (row[status_idx] or '').strip()
    upper_status = raw_status.upper()
    if raw_status in {'1', 'True', 'true'} or upper_status in {'AC', 'ACCEPTED', 'OK', '答案正确'}:
        status = 'AC'
    elif raw_status in {'0', 'False', 'false'} or upper_status in {'WA', 'WRONG ANSWER', '答案错误'}:
        status = 'WA'
    else:
        status = upper_status if upper_status in {'AC','CE','MLE','NO','OLE','RTE','TLE','WA'} else 'WA'
    if not submission_time_unformatted or not str(submission_time_unformatted).strip():
        continue
    try:
        submission_time = parse_submission_time(submission_time_unformatted)
    except Exception:
        # 无法解析时间格式：跳过该条
        continue
    # 直接使用 problem 列值作为题目 ID，并校验存在
    pid = raw_problem
    if not pid or (valid_problem_ids and pid not in valid_problem_ids):
        print(f"[warn] skip submission #{submit_seq} invalid problem_id='{raw_problem}'")
        continue
    be.build_judge_info(token_cnt, submit_seq, "cpp", submission_time, contest_start_time, team_entry[2], pid, status, submission_time, events)
    if len(events) > 100:
        ndjson.dump(events, event_file, ensure_ascii=False)
        events.clear()

# 比赛结束与 finalize 信息
be.build_update_info(token_cnt, contest_start_time, contest_end_time, contest_frozen_time, None, contest_init_time, events)
be.build_update_info(token_cnt, contest_start_time, contest_end_time, contest_frozen_time, contest_finalize_time, contest_init_time, events)
ndjson.dump(events, event_file, ensure_ascii=False)