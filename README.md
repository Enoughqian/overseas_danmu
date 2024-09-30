# overseas_danmu

## 启动命令
- 启动sever
    - streamlit run sever.py
- 启动monitor
    - python loop_monitor.py
- 说明
    - 记得之前的配置文件先拷出来，不要直接覆盖

## tmux基本操作
- tmux ls：查看当前正在运行进程
- tmux a -t 进程名：进入到当前进程中
- tmux new -s ccc：新建会话命名为ccc
- tmux new -s ccc -d：在后台新建会话
- tmux kill-session -t ccc：销毁会话
- tmux rename -t ccc ddd：重命名会话
- 基本快捷键：
    - Ctrl+b：激活控制台
    - d：脱离当前会话（离开回到会话外，会话继续运行）
    - s：选择并进入会话