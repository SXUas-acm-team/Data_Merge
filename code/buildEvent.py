import csv
import ndjson
from datetime import datetime
data = []
# 构建竞赛信息
def build_contest_info(token_id, contest_name, start_time, end_time,freeze_time, time, data):
    iso_start_time = start_time.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    iso_end_time = end_time.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    iso_time = time.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    duration_delta = end_time - start_time
    freeze_duration_delta = end_time - freeze_time
    # Use total_seconds to include days in duration math
    duration_secs = int(duration_delta.total_seconds())
    freeze_secs = int(freeze_duration_delta.total_seconds())
    duration = "{:02d}:{:02d}:{:02d}.000".format(duration_secs // 3600,(duration_secs % 3600) // 60, duration_secs % 60)
    freeze_duration = "{:02d}:{:02d}:{:02d}.000".format(freeze_secs // 3600,(freeze_secs % 3600) // 60, freeze_secs % 60)
    x = {
        "token":str(token_id[0]),
        "id":None,
        "type":"contest",
        "data":
            {
                "formal_name": str(contest_name),
                "scoreboard_type": "pass-fail",
                "start_time": iso_start_time,
                "end_time": iso_end_time,
                "scoreboard_thaw_time": None,
                "duration": str(duration),
                "scoreboard_freeze_duration": str(freeze_duration),
                "cid": 1,
                "id": str(contest_name),
                "name": str(contest_name),
                "shortname": str(contest_name),
                "allow_submit": True,
                "runtime_as_score_tiebreaker": None,
                "warning_message": None,
                "penalty_time": 20
            },
        "time": iso_time
    }
    token_id[0] += 1
    data.append(x)
    return x
# 构建提交后的判题信息
# @Parma:token编号，判题状态("AC","WA")，构造时间，全程("correct", "wrong answer"), 是否叠罚时，是否算通过
def build_result_info(token_id, id, time, name, penalty, solved, data):
    iso_time = time.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    x = {
        "token": str(token_id[0]),
        "id": id,
        "type": "judgement-types",
        "data":{
            "id": id,
            "name": name,
            "penalty":penalty,
            "solved":solved
        },
        "time": iso_time
    }
    token_id[0] += 1
    data.append(x)
    return x
# 构建允许的语言信息
# @parma token编号，语言id，语言哈希，编译指令，语言名，支持的语言后缀，时间倍数，构造时间
def build_language_info(token_id, id, hash, command, name, extension, time_factor, time, data):
    iso_time = time.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    x = {
        "token": str(token_id[0]),
        "id": id,
        "type": "languages",
        "data":{
            "compile_executable_hash":hash,
            "compiler":{
                "version_command":command
            },
            "id": id,
            "name": name,
            "extensions":extension,
            "filter_compiler_files": True,
            "allow_judge": True,
            "time_factor": time_factor,
            "entry_point_required": False,
            "entry_point_name": None
        },
        "time": iso_time
    }
    token_id[0] += 1
    data.append(x)
    return x
def build_language_info_with_runner(token_id, id, hash, command, runner, name, extension, time_factor, entry_point, time, data):
    iso_time = time.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    x = {
        "token": str(token_id[0]),
        "id": id,
        "type": "languages",
        "data":{
            "compile_executable_hash":hash,
            "compiler":{
                "version_command":command
            },
            "runner":{
                "version_command":runner
            },
            "id": id,
            "name": name,
            "extensions":extension,
            "filter_compiler_files": True,
            "allow_judge": True,
            "time_factor": time_factor,
            "entry_point_required": False,
            "entry_point_name": entry_point
        },
        "time": iso_time
    }
    token_id[0] += 1
    data.append(x)
    return x

# 构建初始化题目信息
# @Parma:token编号，题目题号(通常为大写单字母)，题目编号，题目时限，构建时间
def build_problem_info(token_id, id, problem_cnt, time_limit, time, data):
    iso_time = time.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    x = {
        "token": str(token_id[0]),
        "id": id,
        "type": "problems",
        "data":{
            "ordinal": problem_cnt,
            "probid": problem_cnt,
            "shortname": id,
            "rgb": None,
            "color": None,
            "label": id,
            "time_limit": time_limit,
            "statement":[],
            "attachments":[],
            "id": id,
            "name": id,
            "test_data_count": 1
        },
        "time": iso_time
    }
    token_id[0] += 1
    data.append(x)
    return x

# 构建用户组信息
# @parma token编号，用户组名， 是否在滚榜时隐藏，用户组编号， 构建时间
def build_group_info(token_id, id, hidden, categoryid, time, data):
    iso_time = time.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    x = {
        "token": str(token_id[0]),
        "id": id,
        "type": "groups",
        "data":{
            "hidden":hidden,
            "categoryid": categoryid,
            "id": id,
            "icpc_id": None,
            "name": id,
            "sortorder": 0,
            "color": None,
            "allow_self_registration": False
        },
        "time": iso_time
    }
    token_id[0] += 1
    data.append(x)
    return x

# 构建学校信息
# @parma token编号，学校编号，学校全程，学校简称，学校所属国家，构建时间
def build_school_info(token_id, id, name, short_name, country, time, data):
    iso_time = time.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    x = {
        "token": str(token_id[0]),
        "id": str(id),
        "type": "organizations",
        "data":{
            "shortname": short_name,
            "affilid": id,
            "id": str(id),
            "icpc_id": str(id),
            "name": short_name,
            "formal_name": name,
            "country": country,
            "country_flag":
                [

                    {
                        "href": "country-flags/" + country +"/4x3",
                        "mime": "image/svg+xml",
                        "filename": "country-flag-4x3.svg",
                        "width": 640,
                        "height": 480
                    },
                    {
                        "href": "country-flags/"+country+"/1x1",
                        "mime": "image/svg+xml",
                        "filename": "country-flag-1x1.svg",
                        "width": 512,
                        "height": 512
                    }
                ]
        },
        "time": iso_time
    }
    token_id[0] += 1
    data.append(x)
    return x
# 添加团队信息
# @parma: token编号，队伍编号，所属学校id，是否隐藏，所属用户组id，学校全程，学校名，国家，团队名，初始化时间
def build_team_info(token_id, id, organization_id, hidden, group_id, school, country, team_name, time, data):
    iso_time = time.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    x = {
        "token": str(token_id[0]),
        "id": str(id),
        "type": "teams",
        "data": {
            "location": None,
            "organization_id": str(organization_id),
            "hidden": hidden,
            "group_ids":
            [
                group_id
            ],
            "affiliation": school,
            "nationality": country,
            "teamid": int(id),
            "id": str(id),
            "icpc_id": str(id),
            "label": str(id),
            "name": str(team_name),
            "display_name": None,
            "public_description": None
        },
        "time": iso_time
    }
    token_id[0] += 1
    data.append(x)
    return x
# 添加用户信息
# token编号，用户id，队伍id,队伍名，时间，data
# 用户信息id用于登录系统，用户属于队伍，实际显示为队伍名
def build_user_info(token_id, user_id, team_id, team_name, time, data):
    iso_time = time.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    x = {
        "token": str(token_id[0]),
        "id": str(user_id),
        "type": "accounts",
        "data":{
            "last_login_time": None,
            "last_api_login_time": None,
            "first_login_time": None,
            "team": str(team_name),
            "team_id": str(team_id),
            "roles":["team"],
            "type": "team",
            "userid": int(user_id),
            "id": str(user_id),
            "username": str(user_id),
            "name": str(user_id),
            "email": None,
            "last_ip": None,
            "ip": None,
            "enabled": True
        },
        "time": iso_time
    }
    token_id[0] += 1
    data.append(x)
    return x
# 添加提交判题信息
# @parma token编号，提交记录编号，语言id，提交时间，竞赛开始时间，提交队伍id，提交问题id，提交结果(1代表AC,0代表WA)，初始化时间, 输出对象
def build_judge_info(token_id, submission_id, language_id, submission_time, start_time, team_id, problem_id, result, time, data):
    iso_time = time.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    sub_time = submission_time.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    contest_time = submission_time - start_time
    # Include days when formatting contest time
    contest_total_secs = int(contest_time.total_seconds())
    con_time = "{:02d}:{:02d}:{:02d}.000".format(contest_total_secs // 3600, (contest_total_secs % 3600) // 60,contest_total_secs % 60)
    #con_time = contest_time.strftime("%H:%M:%S.000")
    # Guard and normalize problem id
    pid = None if problem_id is None else str(problem_id).strip()
    if not pid:
        # skip invalid submission if problem id is missing
        return ""
    # Normalize judgement result
    valid_types = {"AC","CE","MLE","NO","OLE","RTE","TLE","WA"}
    if isinstance(result, str):
        r = result.strip().upper()
        # Common aliases
        aliases = {"RE":"RTE","RUNTIME ERROR":"RTE","TIME LIMIT EXCEEDED":"TLE","MEMORY LIMIT EXCEEDED":"MLE","OUTPUT LIMIT EXCEEDED":"OLE","NO OUTPUT":"NO","OK":"AC","ACCEPTED":"AC","WRONG ANSWER":"WA"}
        r = aliases.get(r, r)
        judgement_result = r if r in valid_types else "WA"
    else:
        judgement_result = "AC" if result else "WA"
    a1 = {
        "token": str(token_id[0]),
        "id": str(submission_id),
        "type": "submissions",
        "data":{
            "language_id": str(language_id),
            "time":str(sub_time),
            "contest_time":con_time,
            "team_id": str(team_id),
            "problem_id": pid,
            "files":[
                {
                    "href": "contests/external-id-submit-demo/submissions/" + str(submission_id) +"/files",
                    "mime": "application/zip", "filename": "submission.zip"
                }
            ],
            "submitid": int(submission_id),
            "id": str(submission_id),
            "entry_point": None,
            "import_error": None
        },
        "time": sub_time
    }
    token_id[0] += 1
    a2 = {
        "token": str(token_id[0]),
        "id": str(submission_id),
        "type": "judgements",
        "data":{
            "start_time": sub_time,
            "start_contest_time": con_time,
            "end_time": None,
            "end_contest_time": None,
            "max_run_time": None,
            "submission_id": str(submission_id),
            "id": str(submission_id),
            "valid": True,
            "judgement_type_id": None
        },
        "time": sub_time
    }
    token_id[0] += 1
    a3 = {
        "token": str(token_id[0]),
        "id": str(submission_id),
        "type": "runs",
        "data":{
            "run_time":0.001,
            "time": sub_time,
            "contest_time": con_time,
            "judgement_id": str(submission_id),
            "ordinal": 1,
            "id": str(submission_id),
            "judgement_type_id": judgement_result
        },
        "time": sub_time
    }
    token_id[0] += 1
    a4 = {
        "token": str(token_id[0]),
        "id": str(submission_id),
        "type": "judgements",
        "data":{
            "start_time": sub_time,
            "start_contest_time": con_time,
            "end_time": sub_time,
            "end_contest_time": con_time,
            "max_run_time": 0.001,
            "submission_id": str(submission_id),
            "id": str(submission_id),
            "valid": True,
            "judgement_type_id": judgement_result
        },
        "time": sub_time
    }
    token_id[0] += 1
    data.append(a1)
    data.append(a2)
    data.append(a3)
    data.append(a4)
    return ""
# 构建竞赛状态更新信息:
def build_update_info(token_cnt, start, end, frozen, finalized, time, data):
    start_time = None
    end_time = None
    frozen_time = None
    finalized_time = None
    iso_time = None
    if start is not None:
        start_time = start.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    if end is not None:
        end_time = end.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    if frozen is not None:
        frozen_time = frozen.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    if finalized is not None:
        finalized_time = finalized.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    if time is not None:
        iso_time = time.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")

    x = {
        "token": str(token_cnt[0]),
        "id": None,
        "type": "state",
        "data":{
            "started": start_time,
            "ended": end_time,
            "frozen": frozen_time,
            "thawed": None,
            "finalized": finalized_time,
            "end_of_updates": None
        },
        "time": iso_time
    }
    token_cnt[0] += 1
    data.append(x)
    return x