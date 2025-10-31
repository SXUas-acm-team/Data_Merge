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

# 读取配置文件（默认从 /src/contest-info.yaml）
with open(input_path('contest-info.yaml'), encoding='utf-8') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

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

# 处理题目：从 /src/n_problem.csv 读取首列为题目标签
problem_info = []
with open(input_path("n_problem.csv"), "r", encoding="utf-8-sig", newline='') as problem_csv:
    reader = csv.reader(problem_csv)
    # 不确定是否有表头，尝试读取全部后在下面从索引1开始
    for row in reader:
        if not row:
            continue
        problem_info.append(row[0])

for i in range(1, len(problem_info)):
    be.build_problem_info(token_cnt, problem_info[i], i, 1.0, contest_init_time, events)

# 用户组（参赛选手）
be.build_group_info(token_cnt, "participants", False, 1, contest_init_time, events)

# 学校信息：从 /src/n_name.csv 获取
school_info_set = set()
with open(input_path("n_name.csv"), "r", encoding="utf-8-sig", newline='') as name_csv:
    reader = csv.reader(name_csv)
    # 跳过表头
    try:
        header = next(reader)
    except StopIteration:
        header = None
    for row in reader:
        if not row:
            continue
        # 学校名位于第 11 列（索引 10）
        school_info_set.add(row[10])

school_info = {}
school_info_inverse = {}
sid = 0
for name in school_info_set:
    school_info[name] = sid
    school_info_inverse[sid] = name
    sid += 1

# 注意包含 0 在内的所有学校 id
for i in sorted(school_info_inverse.keys()):
    be.build_school_info(token_cnt, i, school_info_inverse[i], school_info_inverse[i], "CHN", contest_init_time, events)

# 团队与账户信息（个人赛：team 与 user 一一对应）
team_info_id = {}
tid = 0
with open(input_path("n_name.csv"), "r", encoding="utf-8-sig", newline='') as name_csv:
    reader = csv.reader(name_csv)
    # 跳过表头
    try:
        header = next(reader)
    except StopIteration:
        header = None
    for row in reader:
        if not row:
            continue
        # uid: 第2列（索引1），队名：第7列（索引6），学校名：第11列（索引10）
        uid = row[1]
        team_name = row[6]
        school_name = row[10]
        # 防止学校未出现在集合时出错
        if school_name not in school_info:
            school_info[school_name] = sid
            school_info_inverse[sid] = school_name
            be.build_school_info(token_cnt, sid, school_name, school_name, "CHN", contest_init_time, events)
            sid += 1
        team_info_id[uid] = [school_name, team_name, tid]
        tid += 1

for uid, (school_name, name, team_id) in team_info_id.items():
    be.build_team_info(token_cnt, team_id, school_info[school_name], False, "participants", school_name, "CHN", name, contest_init_time, events)

# 账户（过滤占位名）
for uid, (school_name, name, team_id) in team_info_id.items():
    if name == "真实名称":
        continue
    be.build_user_info(token_cnt, team_id, team_id, name, contest_init_time, events)

# 添加比赛开始信息
be.build_update_info(token_cnt, contest_start_time, None, None, None, contest_init_time, events)

# 处理提交信息：从 /output/result.csv 读取
status_idx = 6
result_csv_path = OUTPUT_DIR / "result.csv"
with open(result_csv_path, "r", encoding="utf-8-sig", newline='') as result_csv:
    reader = csv.reader(result_csv)
    # 跳过表头
    try:
        header = next(reader)
    except StopIteration:
        header = None
    submit_seq = 0
    for row in reader:
        if not row:
            continue
        submit_seq += 1
        uid = row[1]
        problem = row[2]
        # school_name = row[3]  # 如需使用
        team_entry = team_info_id.get(uid)
        if not team_entry:
            # 未在报名名单中的提交，跳过
            continue
        submission_time_unformatted = row[7]
        status = row[status_idx]
        submission_time = parse_submission_time(submission_time_unformatted)
        be.build_judge_info(token_cnt, submit_seq, "cpp", submission_time, contest_start_time, team_entry[2], problem, status, submission_time, events)

# 比赛结束与 finalize 信息
be.build_update_info(token_cnt, contest_start_time, contest_end_time, contest_frozen_time, None, contest_init_time, events)
be.build_update_info(token_cnt, contest_start_time, contest_end_time, contest_frozen_time, contest_finalize_time, contest_init_time, events)

# 仅在最后一次性写出
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
output_path = OUTPUT_DIR / "converted.ndjson"
with open(output_path, 'w', encoding='utf-8') as f:
    ndjson.dump(events, f, ensure_ascii=False)
print(f"Wrote NDJSON to: {output_path}")