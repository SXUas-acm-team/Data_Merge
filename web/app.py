from __future__ import annotations

import io
import sys
import subprocess
from pathlib import Path
from typing import Optional

from flask import Flask, render_template, request, send_file, abort
import yaml
import csv
import datetime as dt
import tempfile
import shutil
import os

# 仅提供最小工具函数：时间格式规整
def normalize_time(s: str) -> str:
    if not s:
        return s
    s = s.strip().replace('\u200b', '')
    fmts = [
        '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y %H:%M:%S',
        '%Y/%m/%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
    ]
    for fmt in fmts:
        try:
            t = dt.datetime.strptime(s, fmt)
            return t.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            pass
    # 处理 datetime-local 可能没有秒（兼容带 T 或空格）
    if len(s) == 16:
        for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M'):
            try:
                t = dt.datetime.strptime(s, fmt)
                return t.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                continue
    return s


app = Flask(__name__, template_folder="templates", static_folder="static")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/convert")
def convert_endpoint():
    # 读取比赛信息（来自表单），不再要求上传 YAML
    contest_name = (request.form.get('contest_name') or '').strip()
    t_start_both = (request.form.get('contest_start_both') or '').strip()
    t_frozen = (request.form.get('contest_frozen_time') or '').strip()
    t_end_both = (request.form.get('contest_end_both') or '').strip()
    display_with_school = request.form.get('display_team_name_with_school') is not None

    if not contest_name or not t_start_both or not t_frozen or not t_end_both:
        abort(400, description="比赛名称与开始/冻结/结束时间为必填项")

    cfg = {
        'contest-name': contest_name,
        'contest-init-time': normalize_time(t_start_both),
        'contest-start-time': normalize_time(t_start_both),
        'contest-frozen-time': normalize_time(t_frozen.replace('T', ' ')),
        'contest-end-time': normalize_time(t_end_both),
        'contest-finalize-time': normalize_time(t_end_both),
        'display_team_name_with_school': display_with_school,
    }

    # 读取文本或文件的原始内容（直接落盘给脚本使用）
    def pick_text(name: str) -> Optional[str]:
        text = request.form.get(name + "_text", "")
        if text and text.strip():
            return text
        file = request.files.get(name)
        if file and file.filename:
            content = file.read()
            try:
                return content.decode('utf-8-sig')
            except Exception:
                return content.decode('utf-8', errors='ignore')
        return None

    n_problem_txt = pick_text('n_problem')
    n_name_txt = pick_text('n_name')
    n_sub_txt = pick_text('n_sub')
    hoj_txt = pick_text('hoj_sub')

    if not n_problem_txt or not n_name_txt or not n_sub_txt:
        abort(400, description="n_name.csv、n_problem.csv、n_sub.csv 为必填；hoj_sub.csv 可选")

    # 创建临时工作区，将上传/粘贴的文件放入 src/，复制 code/ 目录后调用成熟的 CLI（严格按 README）
    tmp_root = tempfile.mkdtemp(prefix='data_merge_')
    tmp_code = Path(tmp_root) / 'code'
    tmp_src = Path(tmp_root) / 'src'
    tmp_out = Path(tmp_root) / 'output'
    tmp_src.mkdir(parents=True, exist_ok=True)
    tmp_out.mkdir(parents=True, exist_ok=True)
    # 从仓库复制 code 目录（直接后端调用，不做逻辑改写）
    repo_root = Path(__file__).resolve().parents[1]
    shutil.copytree(repo_root / 'code', tmp_code)

    # 写 contest-info.yaml（包含显示名开关）
    contest_yaml = {
        'contest-name': contest_name,
        'contest-init-time': normalize_time(t_start_both),
        'contest-start-time': normalize_time(t_start_both),
        'contest-frozen-time': normalize_time(t_frozen),
        'contest-end-time': normalize_time(t_end_both),
        'contest-finalize-time': normalize_time(t_end_both),
        'display_team_name_with_school': display_with_school,
    }
    (tmp_src / 'contest-info.yaml').write_text(yaml.dump(contest_yaml, allow_unicode=True), encoding='utf-8')

    # 写 CSV 输入
    (tmp_src / 'n_problem.csv').write_text(n_problem_txt, encoding='utf-8')
    (tmp_src / 'n_name.csv').write_text(n_name_txt, encoding='utf-8')
    (tmp_src / 'n_sub.csv').write_text(n_sub_txt, encoding='utf-8')
    if hoj_txt:
        (tmp_src / 'hoj_sub.csv').write_text(hoj_txt, encoding='utf-8')

    # 调用原有 CLI 脚本：先合并（覆盖+可选追加 HOJ），再转换
    try:
        # 与命令行完全一致：在临时工作区以子进程运行 CLI
        cmd = [sys.executable, str(tmp_code / 'cli.py'), 'all', '--overwrite']
        if hoj_txt:
            cmd.append('--append-oj')
        proc = subprocess.run(
            cmd,
            cwd=str(Path(tmp_root)),
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"CLI 失败(exit={proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}")
        ndjson_bytes = (tmp_out / 'converted.ndjson').read_bytes()
    except Exception as e:
        # 将 tmp 目录路径也返回便于排查
        abort(400, description=f"转换失败: {e}")
    finally:
        try:
            shutil.rmtree(tmp_root)
        except Exception:
            pass

    filename = f"converted_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.ndjson"
    return send_file(
        io.BytesIO(ndjson_bytes),
        mimetype="application/x-ndjson; charset=utf-8",
        as_attachment=True,
        download_name=filename,
    )


if __name__ == "__main__":
    # 本地开发启动：FLASK_ENV=development 可自动重载
    app.run(host="0.0.0.0", port=9999, debug=True)
