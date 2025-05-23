# pybioos 用户指南

pybioos 是 Bio-OS 平台的 Python SDK，提供了丰富的功能来管理和操作 Bio-OS 平台上的工作流、数据和资源。

## 目录

- [pybioos 用户指南](#pybioos-用户指南)
  - [目录](#目录)
  - [安装](#安装)
    - [从 PyPI 安装](#从-pypi-安装)
    - [从源码安装](#从源码安装)
  - [命令行工具](#命令行工具)
    - [bw\_import](#bw_import)
      - [用法](#用法)
      - [参数说明](#参数说明)
      - [工作模式](#工作模式)
      - [返回值](#返回值)
    - [bw\_import\_status\_check](#bw_import_status_check)
      - [用法](#用法-1)
      - [参数说明](#参数说明-1)
    - [bw](#bw)
      - [用法](#用法-2)
      - [参数说明](#参数说明-2)
    - [bw_status_check](#bw_status_check)
      - [用法](#用法-3)
      - [参数说明](#参数说明-3)
  - [Python API](#python-api)
    - [基础功能](#基础功能)
      - [登录和状态检查](#登录和状态检查)
    - [工作空间管理](#工作空间管理)
    - [工作流管理](#工作流管理)
    - [文件管理](#文件管理)
  - [高级功能](#高级功能)
    - [工作流运行监控](#工作流运行监控)
    - [数据模型操作](#数据模型操作)
  - [错误处理](#错误处理)
  - [最佳实践](#最佳实践)
  - [注意事项](#注意事项)

## 安装

### 从 PyPI 安装

```bash
pip install pybioos
```

### 从源码安装

```bash
git clone https://github.com/GBA-BI/pybioos.git
cd pybioos
python setup.py install
```

## 命令行工具

pybioos 提供了两个主要的命令行工具：`bw_import` 和 `bw`。

### bw_import

`bw_import` 用于导入工作流到 Bio-OS 平台。支持两种工作模式：快速导入和监控模式。

#### 用法

```bash
bw_import --ak <access_key> \
         --sk <secret_key> \
         --workspace_name <workspace_name> \
         --workflow_name <workflow_name> \
         --workflow_source <workflow_source> \
         [--workflow_desc <description>] \
         [--main_path <main_workflow_path>] \
         [--monitor] \
         [--monitor_interval <interval>]
```

#### 参数说明

必需参数：
- `--ak`: Bio-OS 平台的访问密钥
- `--sk`: Bio-OS 平台的密钥
- `--workspace_name`: 目标工作空间名称
- `--workflow_name`: 要导入的工作流名称
- `--workflow_source`: 工作流源文件路径或 Git 仓库 URL

可选参数：
- `--workflow_desc`: 工作流描述
- `--main_path`: 主工作流文件路径（对于 Git 仓库必需）
- `--monitor`: 启用监控模式，监控工作流验证状态直到完成
- `--monitor_interval`: 状态检查间隔时间（秒），默认为 30 秒

#### 工作模式

1. 快速导入模式（默认）：
   - 工作流上传后立即返回
   - 适合批量导入或脚本集成
   - 示例：
     ```bash
     bw_import --ak <ak> --sk <sk> --workspace_name <ws> \
               --workflow_name <wf> --workflow_source <source>
     ```

2. 监控模式：
   - 工作流上传后进入监控状态
   - 定期检查验证进度
   - 等待验证完成才退出
   - 适合交互式使用
   - 示例：
     ```bash
     bw_import --ak <ak> --sk <sk> --workspace_name <ws> \
               --workflow_name <wf> --workflow_source <source> \
               --monitor --monitor_interval 60
     ```

#### 返回值
- 成功：返回 0
- 失败：返回 1（包括验证失败和超时）

### bw_import_status_check

`bw_import_status_check` 用于异步查询工作流导入验证状态。当使用 `bw_import` 的快速导入模式时，可以使用此命令来检查工作流的验证状态。

#### 用法

```bash
bw_import_status_check --ak <access_key> \
                      --sk <secret_key> \
                      --workspace_name <workspace_name> \
                      --workflow_id <workflow_id>
```

#### 参数说明

必需参数：
- `--ak`: Bio-OS 平台的访问密钥
- `--sk`: Bio-OS 平台的密钥
- `--workspace_name`: 目标工作空间名称
- `--workflow_id`: 要检查的工作流 ID

#### 输出格式
```
Status: <status>
Message: <message>  # 如果有错误消息
```

可能的状态值：
- Succeeded: 验证成功
- Failed: 验证失败
- Importing: 正在导入
- 其他状态

### bw

`bw` 用于提交和管理工作流运行。

#### 用法

```bash
bw --endpoint <endpoint> \
   --ak <access_key> \
   --sk <secret_key> \
   --workspace_name <workspace_name> \
   --workflow_name <workflow_name> \
   --input_json <input_json> \
   [--data_model_name <data_model_name>] \
   [--call_caching] \
   [--submission_desc <description>] \
   [--force_reupload] \
   [--monitor] \
   [--monitor_interval <interval>] \
   [--download_results]
```

#### 参数说明

必需参数：
- `--ak`: Bio-OS 平台的访问密钥
- `--sk`: Bio-OS 平台的密钥
- `--workspace_name`: 工作空间名称
- `--workflow_name`: 工作流名称
- `--input_json`: 输入参数 JSON 文件

可选参数：
- `--endpoint`: Bio-OS 平台的 API 端点
- `--data_model_name`: 数据模型名称
- `--call_caching`: 启用调用缓存
- `--submission_desc`: 提交描述
- `--force_reupload`: 强制重新上传已存在的文件
- `--monitor`: 监控提交运行状态直到完成
- `--monitor_interval`: 状态查询间隔时间（秒）
- `--download_results`: 下载运行结果到本地

### bw_status_check

`bw_status_check` 用于查询工作流运行状态。当使用 `bw` 命令提交工作流后，可以使用此命令来检查所有运行的状态。

#### 用法

```bash
bw_status_check --ak <access_key> \
                --sk <secret_key> \
                --workspace_name <workspace_name> \
                --submission_id <submission_id>
```

#### 参数说明

必需参数：
- `--ak`: Bio-OS 平台的访问密钥
- `--sk`: Bio-OS 平台的密钥
- `--workspace_name`: 目标工作空间名称
- `--submission_id`: 要检查的提交 ID

#### 输出格式
```
Submission ID: <submission_id>
Runs Status:
------------------------------------------------------------
Run ID                                   Status     Message
------------------------------------------------------------
<run_id>                                <status>   <message>
...
```

可能的状态值：
- Succeeded: 运行成功
- Failed: 运行失败
- Running: 正在运行
- Pending: 等待运行
- Unknown: 未知状态

## Python API

### 基础功能

#### 登录和状态检查

```python
from bioos import bioos

# 登录
bioos.login(endpoint="https://bio-top.miracle.ac.cn", 
           access_key="your_access_key",
           secret_key="your_secret_key")

# 检查登录状态
status = bioos.status()
```

### 工作空间管理

```python
# 列出所有工作空间
workspaces = bioos.list_workspaces()

# 获取特定工作空间
ws = bioos.workspace(workspace_id)
```

### 工作流管理

```python
# 获取工作流资源
workflow_resource = ws.workflows

# 导入工作流
result = workflow_resource.import_workflow(
    source="path/to/workflow.wdl",
    name="workflow_name",
    description="workflow description",
    language="WDL"
)

# 获取特定工作流
workflow = ws.workflow(name="workflow_name")

# 提交工作流运行
runs = workflow.submit(
    inputs=input_json,
    outputs=output_json,
    submission_desc="submission description",
    call_caching=True
)
```

### 文件管理

```python
# 获取文件资源
files = ws.files

# 列出文件
file_list = files.list()

# 上传文件
files.upload("local_file.txt", "target_path/")

# 下载文件
files.download(["remote_file.txt"], "local_path/")

# 获取文件 S3 URL
urls = files.s3_urls("file_path")
```

## 高级功能

### 工作流运行监控

```python
from bioos.resource.workflows import Run

# 获取运行状态
run = Run(workspace_id, run_id, submission_id)
status = run.status

# 获取运行日志
log = run.log

# 获取运行输出
outputs = run.outputs

# 同步运行状态
run.sync()
```

### 数据模型操作

```python
# 获取数据模型资源
data_models = ws.data_models

# 列出数据模型
models = data_models.list()
```

## 错误处理

pybioos 定义了多种异常类型来处理不同的错误情况：

- `ConfigurationError`: 配置错误
- `ParameterError`: 参数错误
- `NotFoundError`: 资源未找到
- `ConflictError`: 资源冲突

建议使用 try-except 块来处理这些异常：

```python
try:
    workflow_resource.import_workflow(...)
except NotFoundError as e:
    print(f"资源未找到: {e}")
except ConflictError as e:
    print(f"资源冲突: {e}")
except Exception as e:
    print(f"发生错误: {e}")
```

## 最佳实践

1. 始终在使用其他功能之前先调用 `bioos.login()`
2. 使用 `with` 语句处理文件操作
3. 定期同步运行状态以获取最新信息
4. 使用适当的异常处理来增强程序的健壮性
5. 合理使用缓存功能来提高性能

## 注意事项

1. 确保网络连接稳定
2. 妥善保管访问密钥和密钥
3. 大文件操作时注意内存使用
4. 遵循 Bio-OS 平台的使用限制和配额
5. 定期备份重要数据 