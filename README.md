# Data_Merge

本项目用于将多来源的提交记录合并输出为统一结构的 `result.csv`。

## 输入文件 目录/src

- `n_name.csv`：牛客用户信息（包含 用户ID、昵称、真实名称、学校 等）
- `n_problem.csv`：牛客题目映射表（`id,name`）
- `n_sub.csv`：牛客提交记录（`提交id, 用户id, 题目名称, 提交状态, 提交时间, ...`）
- `oj_sub.csv`（可选）：额外平台HOJ的提交记录（`display_id, status, submit_time, username, realname, ...`）

## 规则说明

- 基础合并（来自 `n_sub.csv`）：
  - `id`：使用 `n_sub.csv` 的 `提交id`
  - `problem`：用 `题目名称` 在 `n_problem.csv` 中查到的 `id`（A..I）
  - `school/username/realname`：用 `用户id` 在 `n_name.csv`（字段名：`用户ID`）中查到对应字段；若查不到，整条记录跳过
  - `status`：当 `提交状态` 为“答案正确”时为 1，否则 0
  - `submit_time`：沿用 `n_sub.csv` 的 `提交时间`

- 追加合并（来自 `oj_sub.csv`）：
  - `id`：从当前 `result.csv` 的最大 id 开始，自增 +1（不与 `n_sub` 去重）
  - `problem`：取 `display_id`
  - `school`：固定填充为 “山西大学”
  - `username`：取 `username`
  - `realname`：取 `realname`
  - `status`：当 `status` ∈ {`1`, `Accepted`, `AC`, `答案正确`} 时为 1，否则 0
  - `submit_time`：优先取 `submit_time`，若空则回退 `gmt_create`

## 使用说明

- 情况 A：仅合并 n_ 三表（n_sub + n_name + n_problem）

```bash
# 从零重建（覆盖写入）
MERGE_OVERWRITE=1 python3 code/merge_submissions.py
```

- 情况 B：在 A 的基础上，同时导入外部 oj_sub 数据

```bash
# 追加 oj_sub 到表尾，id 从当前最大值自增，school 固定“山西大学”
APPEND_OJ=1 python3 code/merge_submissions.py

# 从零重建并导入 oj_sub（推荐用于全量统一时间格式与字段）
MERGE_OVERWRITE=1 APPEND_OJ=1 python3 code/merge_submissions.py
```
