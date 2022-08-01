# EDR test framework

This is a simple python script capable of performing the following tasks: 

- Process execution
- File creation, modification, deletion
- Network connection + data transmission

Upon executing any of the tasks, the script will log the following information in machine-readable format to a timestamped log file:

- Task name
- Timestamp 
- Username
- Process (executable) name
- Command line
- Process ID
- Files opened
- Connections opened

## Process execution

The config file for process executions can be laid out as follows

```
...
  "processes": [
    {
      "name": "process1", 
      "command": "sleep 500",
      "timeout": 2 
    },
    {
      "name": "process2", 
      "command": "./my-executable",
    }
  ],
...
```
The test script will fire off each given command sequentially, and will manually kill each process after the given timeout period. If no timeout is given, the process will run indefinitely.

The output log for a process execution will have the following format, printed to a line in a timestamped logfile: 
```
{"message": "process execution", "timestamp": "2022-07-31 19:09:26", "username": "cadenwestmoreland", "process_name": "sleep", "command_line": ["sleep", "500"], "process_id": 52673, "open_files": [], "connections": []}
```
If files or connections were opened at the beginning of the process execution, they would be listed under "open_files" and "connections".

## File creation +  modification

The config file for file creation, modification, and deletion is laid out as follows: 
```
  ...
  "files_to_create_or_modify": [
    {
      "path": "./tmp/file1.txt",
      "content": "hello world"
    }
  ],
  ...
```
`"path"` is the relative path of the file to create or modify. If the file exists, it will be overwritten with whatever is in `"content"`. If the file does not exist, it will be created and `"content"` will be written to it. This functionality uses built-in python functions to create/modify files, and will be reflected as such in the `"open_files"` section of the log.

The output for a file modification or creation will have the following format, printed to a line in a timestamped logfile: 

```
{"message": "create or modify file", "timestamp": "2022-07-31 19:09:26", "username": "cadenwestmoreland", "process_name": "Python", "command_line": ["/opt/homebrew/Cellar/python@3.9/3.9.13_1/Frameworks/Python.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python", "main.py"], "process_id": 52672, "open_files": [["/Users/cadenwestmoreland/Dev/EDR_Utils/log.2022-07-31 19:09:26.txt", 3], ["/Users/cadenwestmoreland/Dev/EDR_Utils/tmp/file1.txt", 5]], "connections": []}
```
`"open_files"` is given as a list of arrays, with each array containing the path to the file followed by its file descriptor. 


## File deletion

The config for file deletion is laid out as follows: 
```
  ...
  "files_to_delete": [
    {
      "path": "./tmp/file1.txt"
    }
  ]
  ...
  ```


This will simply use built-in python functions to delete the file listed. The output will look like the following: 

```
{"message": "delete file", "timestamp": "2022-07-31 19:20:12", "username": "cadenwestmoreland", "process_name": "Python", "command_line": ["/opt/homebrew/Cellar/python@3.9/3.9.13_1/Frameworks/Python.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python", "main.py"], "process_id": 53857, "open_files": [["/Users/cadenwestmoreland/Dev/EDR_Utils/log.2022-07-31 19:20:12.txt", 3], ["/Users/cadenwestmoreland/Dev/EDR_Utils/tmp/file1.txt", 5]], "connections": []}
```


## Network connection and data transmission

The config for network conection + data transmission is laid out as follows: 
```
...
  "network_connections": [
    {
      "host": "cadens-mbp.lan",
      "port": 9999,
      "data": "hello world"
    },
    ...
  ]
...

```
This tells the test script to connect to the given host and port, and send the given data. The output will look like the following: 

```
{"message": "network io", "timestamp": "2022-07-31 19:20:12", "username": "cadenwestmoreland", "process_name": "Python", "command_line": ["/opt/homebrew/Cellar/python@3.9/3.9.13_1/Frameworks/Python.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python", "main.py"], "process_id": 53857, "open_files": [["/Users/cadenwestmoreland/Dev/EDR_Utils/log.2022-07-31 19:20:12.txt", 3]], "connections": [[5, 2, 1, ["{REDACTED_IP_ADDRESS}", 55705], ["{REDACTED_IP_ADDRESS}", 9999], "ESTABLISHED"]], "protocol": "tcp", "size_of_data_sent": 60}
```
Each entry in `connections` is the output of psutils' `p.connections()` function. 

## Errors

Any errors that occur in the test script will be written to the standard output instead of the logfile. 

## Quick Start

An example config file can be found in the `config.json` file.

To get started, clone the repository and get into the directory: 

```
git clone git@github.com:cadenforrest/EDR_Utils.git
cd EDR_Utils
```

Create and activate a virtual environment (linux/macOS): 

```
python3 -m venv venv
source venv/bin/activate
```

Install the project dependencies:
  
```
pip install -r requirements.txt
```

In another terminal, you can fire up the simple server to facilitate the connection described in the example config file: 
  
```
cd EDR_Utils
python3 simpleserver.py
```

Note that you will need to edit the `config.json` file to point to the correct host and port, depending on your system.

Then, you can run the script: 

```
python3 main.py
```

If things were successful, you should see something like `log.2022-07-31 19:09:26.txt` dumped into the directory.
