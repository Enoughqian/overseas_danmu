import subprocess
import time
import os
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 配置文件路径
config_file = "config/commands.txt"
# 存储当前正在执行的进程对象
processes = []

# 执行命令函数
def execute_command(command):
    process = subprocess.Popen(command, shell=True)
    processes.append(process)
    print(f"Command '{command}' started with PID {process.pid}")

# 清除所有进程
def kill_all_processes():
    for process in processes:
        try:
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
        except psutil.NoSuchProcess:
            pass

    # 等待一段时间，确保进程终止
    time.sleep(1)

    processes.clear()

# 读取配置文件中的命令
def read_commands_from_config():
    with open(config_file, "r") as file:
        lines = file.readlines()
        commands = [line.strip() for line in lines if line.strip()]
        return commands

# 监控配置文件变化
class ConfigFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f"Config file '{config_file}' modified. Restarting commands...")
        kill_all_processes()
        commands = read_commands_from_config()
        for command in commands:
            execute_command(command)

# 启动命令执行
def start_commands():
    commands = read_commands_from_config()
    for command in commands:
        execute_command(command)

# 监控配置文件
if __name__ == "__main__":
    start_commands()

    event_handler = ConfigFileHandler()
    observer = Observer()
    observer.schedule(event_handler, os.path.dirname(os.path.abspath(config_file)), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
