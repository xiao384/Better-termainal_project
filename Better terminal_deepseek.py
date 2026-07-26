import json
import os
import tkinter as tk
from tkinter import messagebox

class main_os:
    def __init__(self, name, key, root_permission):
        self.name = name
        self.key = key
        self.root_permission = root_permission

    @property
    def users(self):
        """显示当前用户信息"""
        info = f"name: {self.name}\nroot: {self.root_permission}\npassword: {self.key}"
        return info

    def open_file(self, file_path):
        """安全打开文件并返回内容"""
        if not os.path.isfile(file_path):
            return f"文件不存在: {file_path}"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_text = f.read()
                return file_text
        except Exception as e:
            return f"读取失败: {e}"

    def turn_off_system(self):
        """关机（示例，Windows 下执行）"""
        if not self.root_permission:
            return "权限不足，需要 root 权限"
        if os.name == 'nt':
            # 实际关机命令（测试时请谨慎）
            # os.system('shutdown /s /t 0')
            return "关机命令已发出（演示模式：未真正执行）"
        else:
            return "当前系统暂不支持关机命令"

    @property
    def help(self):
        """返回可用命令列表"""
        cmds = [
            "root.users              - 查看当前用户信息",
            "root.open_file <路径>   - 查看文件内容",
            "root.turn_off_system    - 关机（需要 root）",
            "root.help               - 显示本帮助",
        ]
        return "\n".join(cmds)

    @property
    def su(self):
        """占位功能：提升权限（未实现）"""
        return "请输入 root 密码（功能未实现）"


# 命令白名单
ALLOWED_METHODS = ['users', 'open_file', 'turn_off_system', 'help', 'su']


def run_command(root_instance, command_str):
    """解析命令并执行，返回结果字符串"""
    if not command_str.startswith('root.'):
        return "命令必须以 'root.' 开头"

    parts = command_str.split(maxsplit=1)
    method_part = parts[0][5:]          # 去掉 'root.'
    args = parts[1] if len(parts) > 1 else ''

    if method_part not in ALLOWED_METHODS:
        return f"未知命令: {method_part}，输入 root.help 查看帮助"

    try:
        if method_part == 'users':
            return root_instance.users
        elif method_part == 'open_file':        # ✅ 已修正为 'open_file'
            if not args:
                return "用法: root.open_file <文件路径>"
            return root_instance.open_file(args)
        elif method_part == 'turn_off_system':
            return root_instance.turn_off_system()
        elif method_part == 'help':
            return root_instance.help
        elif method_part == 'su':
            return root_instance.su
    except Exception as e:
        return f"执行出错: {e}"


# -------------------- GUI 部分 --------------------
def launch_main_window(root_instance):
    global main_tk
    main_tk = tk.Tk()
    main_tk.title(f"终端 - {root_instance.name}")
    main_tk.geometry('600x400')

    output_text = tk.Text(main_tk, wrap='word', font=('Consolas', 10))
    output_text.pack(fill='both', expand=True, padx=5, pady=5)

    input_frame = tk.Frame(main_tk)
    input_frame.pack(fill='x', padx=5, pady=5)

    cmd_entry = tk.Entry(input_frame, font=('Consolas', 10))
    cmd_entry.pack(side='left', fill='x', expand=True)
    cmd_entry.bind('<Return>', lambda e: on_run())

    def on_run():
        cmd = cmd_entry.get().strip()
        if not cmd:
            return
        output_text.insert('end', f">>> {cmd}\n")
        result = run_command(root_instance, cmd)
        output_text.insert('end', result + '\n')
        output_text.see('end')
        cmd_entry.delete(0, 'end')

    run_btn = tk.Button(input_frame, text='执行', command=on_run)
    run_btn.pack(side='right')

    output_text.insert('end', "输入 'root.help' 查看可用命令\n")
    main_tk.mainloop()


# -------------------- 登录验证 --------------------
def login():
    username = tk_input_name.get().strip()
    password = tk_input_key.get().strip()

    # 示例数据文件 users_data.json（首次运行需手动创建）
    try:
        with open('users_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        messagebox.showerror('错误', '用户数据文件 users_data.json 不存在')
        return

    names = data.get('users_name', [])
    keys = data.get('users_password', [])
    permissions = data.get('users_root', [])

    found = False
    user_permission = None
    for i in range(len(names)):
        if names[i] == username and keys[i] == password:
            found = True
            user_permission = permissions[i]
            break

    if not found:
        messagebox.showerror('登录失败', '用户名或密码错误')
        return

    is_root = (user_permission == 'root')
    root_instance = main_os(username, password, is_root)

    first_root.destroy()
    launch_main_window(root_instance)


# -------------------- 登录界面 --------------------
first_root = tk.Tk()
first_root.title('登录')
first_root.geometry('300x200')

tk.Label(first_root, text="用户名:").pack()
tk_input_name = tk.Entry(first_root)
tk_input_name.pack(pady=5)

tk.Label(first_root, text="密码:").pack()
tk_input_key = tk.Entry(first_root, show='*')
tk_input_key.pack(pady=5)

tk.Button(first_root, text='登录', command=login).pack(pady=10)

first_root.mainloop()