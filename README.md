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

## 放置输入文件（src/）

- `n_name.csv`：牛客用户（含 用户ID/昵称/真实名称/学校）
- `n_problem.csv`：题目映射（`id,name`）
- `n_sub.csv`：牛客提交记录（`提交id, 用户id, 题目名称, 提交状态, 提交时间, ...`）
- `hoj_sub.csv`（可选）：外部 HOJ 记录 （`display_id, status, submit_time, username, realname, ...`）
- `contest-info.yaml`：比赛配置

编码采用 `utf-8-sig`，兼容带 BOM 的 UTF-8。

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
