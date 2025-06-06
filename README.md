# pybioos

Python SDK for Bio-OS.

[![Documentation Status](https://readthedocs.org/projects/pybioos/badge/?version=latest)](https://pybioos.readthedocs.io/en/latest/?badge=latest)

# Installation
From PYPI.
```
$ pip install pybioos
```

From source code.
```
$ git clone https://github.com/GBA-BI/pybioos.git
$ cd pybioos
$ python setup.py install
```

# Documentation

The full documentation is available at [https://pybioos.readthedocs.io/](https://pybioos.readthedocs.io/).

# Example usage
See Example_usage.ipynb


Or use as CLI command.
Use bw to submit a workflow run.
```
$ bw -h
usage: bw [-h] [--endpoint ENDPOINT] [--ak AK] [--sk SK] [--workspace_name WORKSPACE_NAME] [--workflow_name WORKFLOW_NAME] [--input_json INPUT_JSON]
          [--data_model_name DATA_MODEL_NAME] [--call_caching] [--submission_desc SUBMISSION_DESC] [--force_reupload] [--monitor]
          [--monitor_interval MONITOR_INTERVAL] [--download_results]

Bio-OS instance platform workflow submitter program.

options:
  -h, --help            show this help message and exit
  --endpoint ENDPOINT   Bio-OS instance platform endpoint
  --ak AK               Access_key for your Bio-OS instance platform account.
  --sk SK               Secret_key for your Bio-OS instance platform account.
  --workspace_name WORKSPACE_NAME
                        Target workspace name.
  --workflow_name WORKFLOW_NAME
                        Target workflow name.
  --input_json INPUT_JSON
                        The input_json file in Cromwell Womtools format.
  --data_model_name DATA_MODEL_NAME
                        Intended name for the generated data_model on the Bio-OS instance platform workspace page.
  --call_caching        Call_caching for the submission run.
  --submission_desc SUBMISSION_DESC
                        Description for the submission run.
  --force_reupload      Force reupolad tos existed files.
  --monitor             Moniter the status of submission run until finishment.
  --monitor_interval MONITOR_INTERVAL
                        Time interval for query the status for the submission runs.
  --download_results    Download the submission run result files to local current path.
```

Use bw_import to import a workflow to Bio-OS instance platform.
```
$ bw_import -h
usage: bw_import [-h] --ak AK --sk SK --workspace_name WORKSPACE_NAME --workflow_name WORKFLOW_NAME --workflow_source WORKFLOW_SOURCE [--workflow_desc WORKFLOW_DESC] [--main_path MAIN_PATH]

This tool allows users to import workflows into a Bio-OS instance platform. It supports importing workflows from local WDL files, local directories containing WDL files, or Git repositories.

Bio-OS Workflow Import Tool

optional arguments:
  -h, --help            show this help message and exit
  --ak AK               Access key for your Bio-OS instance platform account
  --sk SK               Secret key for your Bio-OS instance platform account
  --workspace_name WORKSPACE_NAME
                        Target workspace name
  --workflow_name WORKFLOW_NAME
                        Name for the workflow to be imported
  --workflow_source WORKFLOW_SOURCE
                        Path to a local WDL file, or a local directory containing WDL file(s). It can also be a Git repository URL.
  --workflow_desc WORKFLOW_DESC
                        Description for the workflow
  --main_path MAIN_PATH
                        Path to the main WDL workflow file. This is required when --workflow_source is a local directory. If --workflow_source is a single WDL file, this argument is optional and defaults to the path provided in --workflow_source. This is also required when --workflow_source is a Git repository URL pointing to a directory.
```

Use bw_import_status_check to check the workflow import status.
```
$ bw_import_status_check -h
usage: bw_import_status_check [-h] --ak AK --sk SK --workspace_name WORKSPACE_NAME --workflow_id WORKFLOW_ID

Bio-OS Workflow Import Status Check Tool

options:
  -h, --help            show this help message and exit
  --ak AK              Access key for your Bio-OS instance platform account
  --sk SK              Secret key for your Bio-OS instance platform account
  --workspace_name WORKSPACE_NAME
                        Target workspace name
  --workflow_id WORKFLOW_ID
                        ID of the workflow to check
```

Use bw_status_check to check the status of workflow runs.
```
$ bw_status_check -h
usage: bw_status_check [-h] --ak AK --sk SK --workspace_name WORKSPACE_NAME --submission_id SUBMISSION_ID

Bio-OS Workflow Run Status Check Tool

options:
  -h, --help            show this help message and exit
  --ak AK              Access key for your Bio-OS instance platform account
  --sk SK              Secret key for your Bio-OS instance platform account
  --workspace_name WORKSPACE_NAME
                        Target workspace name
  --submission_id SUBMISSION_ID
                        ID of the submission to check
```

Use get_submission_logs to download workflow submission logs.
```
$ get_submission_logs -h
usage: get_submission_logs [-h] --ak AK --sk SK --workspace_name WORKSPACE_NAME --submission_id SUBMISSION_ID [--output_dir OUTPUT_DIR]

Bio-OS Workflow Submission Logs Download Tool

options:
  -h, --help            show this help message and exit
  --ak AK              Access key for your Bio-OS instance platform account
  --sk SK              Secret key for your Bio-OS instance platform account
  --workspace_name WORKSPACE_NAME
                        Target workspace name
  --submission_id SUBMISSION_ID
                        ID of the submission to download logs
  --output_dir OUTPUT_DIR
                        Local directory to save the logs (default: current directory)
```