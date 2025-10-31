# MergeResolver

将牛客、HOJ等比赛数据合并为统一格式 `output/result.csv`，并一键生成 DOMjudge 事件流 `output/converted.ndjson`，可直接导入ICPC Resolver进行滚榜。

可以直接访问[MergereSolver](https://mergeresolver.gwy.fun/)在线使用

## 快速开始 - Web 界面

网页端现已支持“直接填写比赛信息 + 上传必要 CSV”，一键导出 `.ndjson`

```bash
# 安装依赖（建议使用虚拟环境）
python3 -m pip install -U -r requirements.txt

# 启动本地服务
python web/app.py
```

打开浏览器访问 http://localhost:9999 即可。

## 进阶探索 - 命令行

### 安装依赖
通过以下命令安装需要的库:

```bash
# 安装依赖
python3 -m pip install -U ndjson pyyaml
```

### 配置竞赛信息
打开`src/contest-info.yaml`文件，根据格式将竞赛信息填入配置文件

若需要在滚榜时将学校名添加在队伍名前面，将`display_team_name_with_school`项置为`true`即可

### 使用命令行

```bash
# 一步到位：从零重建 + 追加 oj_sub + 转换为 NDJSON
python3 code/cli.py all --overwrite --append-oj
```

### 输出
- `output/result.csv`（合并后的统一提交数据）
- `output/converted.ndjson`（DOMjudge 事件流）

输出的`output/converted.ndjson`文件不包含奖项，需要用户使用ICPC resolver的`award.sh`(Windows下为`award.sh`)手动为比赛分配奖牌数量

之后就可以使用`resolver.sh`愉快的滚榜啦

## 放置输入文件（src/）

- `n_name.csv`：牛客榜单导出信息（含 用户ID/昵称/真实名称/学校）需要携带用户ID 请联系牛客平台管理员导出
- `n_problem.csv`：题目映射（`id,name`） 将牛客题目名称映射成题号，由用户自行构建，可参考`src`目录下的模板进行构建
- `n_sub.csv`：牛客提交记录（`提交id, 用户id, 题目名称, 提交状态, 提交时间, ...`）由竞赛管理员导出
- `hoj_sub.csv`（可选）：外部 HOJ 记录 （`display_id, status, submit_time, username, realname, ...`）
- `contest-info.yaml`：比赛配置

编码采用 `utf-8-sig`，兼容带 BOM 的 UTF-8。

## 开发指南

见本项目中的 [开发指南](https://github.com/SXUas-acm-team/MergeResolver/tree/main/code)。

欢迎继续开发，支持更多类型的 OJ 统一滚榜操作～

## 服务器部署

- Docker：

```bash
docker build -t data-merge-web .
docker run --rm -p 9999:9999 data-merge-web
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
