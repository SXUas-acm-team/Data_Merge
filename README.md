# Data_Merge

将多来源 CSV 合并为统一 `output/result.csv`，并一键生成 DOMjudge 事件流 `output/converted.ndjson`。

## 快速开始

```bash
# 安装依赖
python3 -m pip install -U ndjson pyyaml

# 一步到位：从零重建 + 追加 oj_sub + 转换为 NDJSON
python3 code/cli.py all --overwrite --append-oj
```

生成：
- `output/result.csv`（合并后的统一提交数据）
- `output/converted.ndjson`（DOMjudge 事件流）

## Web 界面（在线生成 NDJSON）

网页端现已支持“直接填写比赛信息 + 上传必要 CSV”，一键导出 `.ndjson`：

```bash
# 安装依赖（建议使用虚拟环境）
python3 -m pip install -U -r requirements.txt

# 启动本地服务
python web/app.py
```

打开浏览器访问 http://localhost:9999 即可。

页面会提示所需文件（不再需要 result.csv 与 contest-info.yaml）：
- n_name.csv（报名信息：uid 第2列，真实名称第7列，学校第11列）
- n_problem.csv（题目映射：推荐表头 `id,name`，或至少首列为题目标签）
- n_sub.csv（牛客提交：需含 `提交id, 用户id, 题目名称, 提交状态, 提交时间`）
- hoj_sub.csv（可选，外部 HOJ：`display_id, status, submit_time/gmt_create, username, realname`）

比赛信息在页面内直接输入（名称 + 5 个时间都用时间选择器），并提供一个开关：

```text
在队伍/账户显示名中带上学校（学校 - 姓名）
```

启用后导出的 NDJSON 中队伍名与账户展示名为“学校 - 姓名”；关闭则为“姓名”。

### 显示名格式（是否包含学校）

可在 `src/contest-info.yaml` 中配置队伍/账户的显示名是否包含学校：

```yaml
# true: 显示为 "学校 - 姓名"；false: 仅显示 "姓名"
display_team_name_with_school: false
```

当设置为 `true` 时，导出的 `output/converted.ndjson` 中队伍名与账户展示名将被拼接为 `学校 - 姓名`。

## 放置输入文件（src/）

- `n_name.csv`：牛客用户（含 用户ID/昵称/真实名称/学校）
- `n_problem.csv`：题目映射（`id,name`）
- `n_sub.csv`：牛客提交记录（`提交id, 用户id, 题目名称, 提交状态, 提交时间, ...`）
- `hoj_sub.csv`（可选）：外部 HOJ 记录 （`display_id, status, submit_time, username, realname, ...`）
- `contest-info.yaml`：比赛配置

编码采用 `utf-8-sig`，兼容带 BOM 的 UTF-8。

## 服务器部署

- Gunicorn：`gunicorn -w 2 -b 0.0.0.0:5000 web.app:app`
- Docker：

```bash
docker build -t data-merge-web .
docker run --rm -p 5000:5000 data-merge-web
```

## 常用命令

```bash
# only 合并：从零重建 result.csv
python3 code/cli.py merge --overwrite

# only 合并：在现有 result.csv 末尾追加 oj_sub
python3 code/cli.py merge --append-oj

# only 转换：基于 src/result.csv 和 contest-info.yaml 生成 converted.ndjson
python3 code/cli.py convert

# 查看帮助
python3 code/cli.py --help
```
