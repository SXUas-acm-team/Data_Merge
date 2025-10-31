## Code 目录 — 开发文档

### 概览

`code/` 包含用于合并、转换比赛提交数据并生成 NDJSON 事件的脚本。常见工作流：

- 先运行合并：把报名表与提交记录合并成统一的 `output/result.csv`（由 `merge_submissions.py` 负责）
- 再运行转换：把 `result.csv`、报名表、题目表等转换为平台可消费的 `output/converted.ndjson`（由 `convert.py` 负责）
- `cli.py` 提供了统一的命令行入口（`all|merge|convert`）

### 文件清单与说明

- `buildEvent.py`
  - 作用：构造比赛事件（contest、languages、problems、teams、accounts、submissions、judgements 等）的 helper 函数集合，返回用于写入 NDJSON 的事件对象。
  - 关键函数：
    - `build_contest_info(...)`、`build_result_info(...)`、`build_language_info(...)`、`build_problem_info(...)`
    - `build_group_info(...)`、`build_school_info(...)`、`build_team_info(...)`、`build_user_info(...)`
    - `build_judge_info(...)`（把一次提交拆成 submissions/judgements/runs 等事件）
    - `build_update_info(...)`（构造比赛状态更新事件）
  - 用法：被 `convert.py` 导入并调用以构造 `events` 列表，最后由 `ndjson.dump` 写出。

- `cli.py`
  - 作用：统一的命令行入口，封装了常用子命令并复用已有脚本逻辑。
  - 子命令：
    - `all`：依次执行合并与转换（等同于先 `merge` 再 `convert`）
    - `merge`：只执行合并步骤（调用 `merge_submissions.py`）
    - `convert`：只执行转换步骤（直接运行 `convert.py`）
  - 特性：`run_merge` 使用环境变量 `MERGE_OVERWRITE` 和 `APPEND_OJ` 控制 `merge_submissions.py` 的行为，通过 `runpy.run_path` 动态加载脚本并调用其函数。
  - 示例：
    - `python3 code/cli.py all --overwrite --append-oj`

- `convert.py`
  - 作用：把报名表（`n_name.csv`）、题目表（`n_problem.csv`）以及合并生成的 `output/result.csv` 转换为比赛事件流 `output/converted.ndjson`。
  - 读取路径策略：优先从项目根 `src/` 读取文件（例如 `src/n_name.csv`），若不存在则回退到 `code/` 目录下同名文件，以保证向后兼容。
  - 注意点：
    - 从 `contest-info.yaml` 读取比赛时间、显示配置等。
    - 会自动构造学校集合、team/account 对应关系，并处理 `result.csv` 中没有报名信息的 fallback 场景（如 HOJ 导入）。
    - 最终输出为 `output/converted.ndjson`。

- `merge_submissions.py`
  - 作用：从 `src/n_sub.csv`（提交表）与 `src/n_name.csv`（报名表）合并并写入 `output/result.csv`，并提供把外部 OJ 导出的 `hoj_sub.csv` 追加到结果表的功能。
  - 主要函数：
    - `merge_and_append()`：主入口，返回 (appended, total, skipped_no_user)
    - `append_oj_sub()`：把 `hoj_sub.csv` 的行追加到 `output/result.csv`
  - 行为要点：
    - 支持覆盖式重建（通过设置环境变量 `MERGE_OVERWRITE=1`）。
    - 会跳过未在报名表中出现的提交（计入 skipped_no_user），并把编译错误（CE）排除在计罚之外。
    - 输出字段顺序固定为 `['id','uid','problem','school','username','realname','status','submit_time']`。

- `peek_oj.py`
  - 作用：简易调试脚本，打印 `code/oj_sub.csv` 的表头及前 3 行；若文件不存在或为空，输出 `EMPTY`。
  - 用法：用于快速验证 oj_sub 导出文件的结构。

- `peek_random.py`
  - 作用：从 `code/result.csv` 读取所有行，打印总条数，并分别输出首、中、尾三条的简要字段（用于抽检）。

- `peek_result.py`
  - 作用：打印 `code/result.csv` 的前 5 行（调试用），帮助快速查看合并结果是否符合预期。

### 运行顺序

1. 合并报名表与提交表：

   - 覆盖式重建（清空旧的 `output/result.csv` 并重建）：

     python3 code/cli.py merge --overwrite

   - 普通追加（仅新增未存在的提交）：

     python3 code/cli.py merge

   - 若要同时把外部 OJ 的记录也追加：

     python3 code/cli.py merge --append-oj

2. 转换为 NDJSON 事件文件：

   python3 code/cli.py convert

3. 一步完成（合并 + 转换）：

   python3 code/cli.py all --overwrite --append-oj

### 常见注意事项与调试建议

- 若脚本找不到 `src/` 下的 CSV，请检查文件是否位于 `src/`，或放到 `code/` 以作回退。
- `merge_submissions.py` 会跳过没有报名信息的提交；若你希望把 HOJ 导入的行也合并，请准备 `hoj_sub.csv` 并使用 `--append-oj` 或把其内容拷贝到 `src/hoj_sub.csv`。
- 时间解析在不同脚本中略有差异（`merge_submissions.py` 的 `normalize_time` 与 `convert.py` 的 `parse_submission_time`），遇到时间解析失败的行会被跳过或原样写出，排查时可用 `peek_result.py` / `peek_random.py` / `peek_oj.py` 快速查看样本。