from re import T
import socket
import psutil
import os
import json
import datetime
from subprocess import PIPE
import shlex
import logging
from pythonjsonlogger import jsonlogger


class Logger:
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_file_path)
        formatter = jsonlogger.JsonFormatter()
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log(self, message: str, extras: dict = None):
        self.logger.info(message, extra=extras)


def send_data_to_server(network_io_config: dict):
    # create a socket object
    p = psutil.Process()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = network_io_config["host"]
    port = 9999
    s.connect((host, port))
    with p.oneshot():
        log_dict = {}
        log_dict["timestamp"] = datetime.datetime.fromtimestamp(
            p.create_time()
        ).strftime("%Y-%m-%d %H:%M:%S")
        log_dict["username"] = p.username()
        log_dict["process_name"] = p.name()
        log_dict["command_line"] = p.cmdline()
        log_dict["process_id"] = p.pid
        log_dict["open_files"] = p.open_files()
        log_dict["connections"] = p.connections()
        log_dict["protocol"] = "tcp"
        log_dict["size_of_data_sent"] = network_io_config["data"].__sizeof__()
    s.send(network_io_config["data"].encode("ascii"))
    s.close()
    print(f"sent {network_io_config['data']} to {host}")
    logger.log("network io", log_dict)


def delete_file(file_config: dict):
    p = psutil.Process()
    try:
        f = open(file_config["path"])
    except FileNotFoundError:
        print("File not found at {}".format(file_config["path"]))
        return
    with p.oneshot():
        log_dict = {}
        log_dict["timestamp"] = datetime.datetime.fromtimestamp(
            p.create_time()
        ).strftime("%Y-%m-%d %H:%M:%S")
        log_dict["username"] = p.username()
        log_dict["process_name"] = p.name()
        log_dict["command_line"] = p.cmdline()
        log_dict["process_id"] = p.pid
        log_dict["open_files"] = p.open_files()
        log_dict["connections"] = p.connections()
    os.remove(f.name)
    logger.log("delete file", log_dict)


def create_or_modify_file(file_config: dict):
    p = psutil.Process()
    try:
        f = open(file_config["path"], "w")
    except FileNotFoundError:
        os.makedirs(os.path.dirname(file_config["path"]))
        f = open(file_config["path"], "w")
        print(f.fileno())
    # use psutil's process context manager to avoid race condition shenanigans when grabbing the data we're interested in
    with p.oneshot():
        log_dict = {}
        log_dict["timestamp"] = datetime.datetime.fromtimestamp(
            p.create_time()
        ).strftime("%Y-%m-%d %H:%M:%S")
        log_dict["username"] = p.username()
        log_dict["process_name"] = p.name()
        log_dict["command_line"] = p.cmdline()
        log_dict["process_id"] = p.pid
        log_dict["open_files"] = p.open_files()
        log_dict["connections"] = p.connections()
    logger.log("create or modify file", log_dict)
    f.write(file_config["content"])
    f.close()


def run_process(process: dict):
    # parse command into a format psutil can understand
    args = shlex.split(process["command"])
    # start the process
    p = psutil.Popen(args, stdout=PIPE, stderr=PIPE)
    # use psutil's process context manager to avoid race condition shenanigans when grabbing the data we're interested in
    with p.oneshot():
        log_dict = {}
        log_dict["timestamp"] = datetime.datetime.fromtimestamp(
            p.create_time()
        ).strftime("%Y-%m-%d %H:%M:%S")
        log_dict["username"] = p.username()
        log_dict["process_name"] = p.name()
        log_dict["command_line"] = p.cmdline()
        log_dict["process_id"] = p.pid
        log_dict["open_files"] = p.open_files()
        log_dict["connections"] = p.connections()
    logger.log("process execution", log_dict)
    try:
        p.wait(timeout=process["timeout"])
    except psutil.TimeoutExpired:
        print("Process timed out after {} seconds".format(process["timeout"]))
        p.kill()
        print("Process killed")


# init logger
start_time = datetime.datetime.now()
logger = Logger("log.{}.txt".format(start_time.strftime("%Y-%m-%d %H:%M:%S")))

if __name__ == "__main__":
    f = open("config.json")
    config = json.load(f)
    f.close()
    for process in config["processes"]:
        run_process(process)
    for file_config in config["files_to_create_or_modify"]:
        create_or_modify_file(file_config)
    for file_config in config["files_to_delete"]:
        delete_file(file_config)
    for network_io_config in config["network_connections"]:
        send_data_to_server(network_io_config)
    print("Finished")
    print("Wrote log to log.{}.txt".format(start_time.strftime("%Y-%m-%d %H:%M:%S")))
