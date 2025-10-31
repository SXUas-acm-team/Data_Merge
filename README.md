# Data_Merge

本项目用于将多来源的提交记录合并输出为统一结构的 `result.csv`。

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
