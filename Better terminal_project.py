#用于测试项目
import json
import os
import platform
import subprocess
import tkinter as tk
# import sys
# from email import message
# from tkinter import ttk
from tkinter import messagebox
#import time
#系统检测
'''以下变量不可修改'''
__system_name__ = os.name
__run_path__ = os.path.dirname(__file__)
root_permission = False
users_permission = False

#系统操作
class SYSTEM_OS:
    def __init__(self,__system_name__,users_name,users_permission_detailed):
        self.system_name = __system_name__
        self.users_name = users_name
        self.users_permission_detailed = users_permission_detailed
    @property
    def message(self):
        cpu_info = platform.processor() or platform.machine()
        result_message = (f'系统:{platform.platform()}\nCPU:{platform.machine()}--{cpu_info}\n'
                          f'用户:{self.users_name}\n权限:{self.users_permission_detailed}')
        return result_message
    @property
    def help(self):
        cmd_list = [
            'help: 帮助界面',
            'message: 系统信息',
            'turn_off_system: 关机',
            'open <路径>: 打开并编辑文件',
            'users: 查看当前用户信息',
            'users list: 列出所有用户',
            'users modify <用户名>: 修改用户密码/权限 (root)',
            'users add: 添加新用户 (root)',
            'users delete <用户名>: 删除用户 (root)',
        ]
        return '\n'.join(cmd_list)
    @property
    def turn_off_system(self):
        if __system_name__ != "nt":
            return "当前系统暂不支持关机命令"
        # 使用列表在闭包中传递用户确认结果
        confirmed = [False]
        def finally_turn_off():
            confirmed[0] = True
            turn_off_confirm.destroy()
            subprocess.run(["shutdown", "/s", "/t", "1"], check=True)
        def cancel_turn_off():
            turn_off_confirm.destroy()
        turn_off_confirm = tk.Toplevel(main_tk)
        turn_off_confirm.title('确认关机')
        turn_off_confirm.geometry('250x120')
        turn_off_confirm.resizable(False, False)
        tk.Label(turn_off_confirm, text='确认要关机吗？', font=('', 10)).pack(pady=10)
        btn_frame = tk.Frame(turn_off_confirm)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text='确认关机', command=finally_turn_off,
                  bg='red', fg='white').pack(side='left', padx=10)
        tk.Button(btn_frame, text='取消', command=cancel_turn_off).pack(side='left', padx=10)
        # 阻塞等待用户确认
        turn_off_confirm.grab_set()
        main_tk.wait_window(turn_off_confirm)
        if confirmed[0]:
            return '系统正在关机...'
        else:
            return '已取消关机'
    def open_file(self, file_path):
        if not os.path.exists(file_path):
            return f'文件不存在: {file_path}'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return f'读取文件失败: {e}'
        # 创建文件编辑窗口
        open_file_tk = tk.Toplevel(main_tk)
        open_file_tk.title(file_path)
        open_file_tk.geometry('500x400')
        # 菜单栏
        menubar = tk.Menu(open_file_tk)
        file_menu = tk.Menu(menubar, tearoff=0)
        def save_file():
            try:
                new_content = text_widget.get("1.0", "end-1c")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                messagebox.showinfo('提示', f'文件已保存: {file_path}')
            except Exception as e:
                messagebox.showerror('保存失败', str(e))
        def close_window():
            open_file_tk.destroy()
        file_menu.add_command(label='保存 (Ctrl+S)', command=save_file)
        file_menu.add_separator()
        file_menu.add_command(label='关闭', command=close_window)
        menubar.add_cascade(label='文件', menu=file_menu)
        open_file_tk.config(menu=menubar)
        # 文本编辑区
        text_widget = tk.Text(open_file_tk, wrap='word', font=('Consolas', 10))
        text_widget.insert('1.0', content)
        text_widget.pack(fill='both', expand=True, padx=5, pady=5)
        # Ctrl+S 快捷键
        open_file_tk.bind('<Control-s>', lambda e: save_file())
        return f'已打开文件: {file_path}'
    # ==================== 用户管理 ====================
    def _load_users_data(self):
        """加载 users_data.json 数据"""
        with open(os.path.join(__run_path__, 'users_data.json'), 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_users_data(self, data):
        """保存数据到 users_data.json"""
        with open(os.path.join(__run_path__, 'users_data.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def users(self, args_str):
        """用户管理入口
        用法:
          users                 → 查看当前用户信息
          users list            → 列出所有用户
          users modify <用户名>  → 修改用户密码/权限 (需 root)
          users add             → 添加新用户 (需 root)
          users delete <用户名>  → 删除用户 (需 root)
        """
        args = args_str.split() if args_str.strip() else []

        # ---- 无参数: 当前用户信息 ----
        if not args:
            return (f'当前用户: {self.users_name}\n'
                    f'权限: {self.users_permission_detailed}')

        sub_cmd = args[0]

        # ---- list: 列出所有用户 ----
        if sub_cmd == 'list':
            try:
                data = self._load_users_data()
            except Exception as e:
                return f'读取用户数据失败: {e}'
            lines = ['=== 用户列表 ===']
            for i in range(len(data['users_name'])):
                marker = ' ← 当前' if data['users_name'][i] == self.users_name else ''
                lines.append(f"  {data['users_name'][i]:12s}  权限: {data['users_root'][i]}{marker}")
            return '\n'.join(lines)

        # ---- 需要 root 的操作 ----
        if not root_permission:
            return '权限不足：修改用户信息需要 root 权限'

        if sub_cmd == 'modify':
            target = args[1] if len(args) > 1 else ''
            if not target:
                return '用法: users modify <用户名>'
            return self._modify_user_gui(target)

        elif sub_cmd == 'add':
            return self._add_user_gui()

        elif sub_cmd == 'delete':
            target = args[1] if len(args) > 1 else ''
            if not target:
                return '用法: users delete <用户名>'
            return self._delete_user(target)

        return (f'未知子命令: {sub_cmd}\n'
                f'可用: list | modify <用户名> | add | delete <用户名>')

    def _modify_user_gui(self, target):
        """GUI: 修改用户密码和权限"""
        try:
            data = self._load_users_data()
        except Exception as e:
            return f'读取用户数据失败: {e}'

        if target not in data['users_name']:
            return f'用户 "{target}" 不存在'

        idx = data['users_name'].index(target)

        # ---- 创建修改窗口 ----
        win = tk.Toplevel(main_tk)
        win.title(f'修改用户: {target}')
        win.geometry('340x280')
        win.resizable(False, False)

        # 标题
        title_frame = tk.Frame(win)
        title_frame.pack(fill='x', pady=10)
        tk.Label(title_frame, text=f'正在修改用户: ',
                 font=('', 10)).pack(side='left')
        tk.Label(title_frame, text=target,
                 font=('', 10, 'bold'), fg='#2196F3').pack(side='left')

        # 新密码
        tk.Label(win, text='新密码 (留空则不修改):').pack(anchor='w', padx=20)
        pwd_entry = tk.Entry(win, show='*', width=35)
        pwd_entry.pack(pady=5)

        # 确认密码
        tk.Label(win, text='确认新密码:').pack(anchor='w', padx=20)
        pwd_confirm_entry = tk.Entry(win, show='*', width=35)
        pwd_confirm_entry.pack(pady=5)

        # 权限选择
        tk.Label(win, text='用户权限:').pack(anchor='w', padx=20, pady=(10, 0))
        perm_var = tk.StringVar(value=data['users_root'][idx])
        perm_frame = tk.Frame(win)
        perm_frame.pack(pady=5)
        tk.Radiobutton(perm_frame, text='root  (管理员)',
                       variable=perm_var, value='root',
                       font=('', 9)).pack(side='left', padx=15)
        tk.Radiobutton(perm_frame, text='users (普通用户)',
                       variable=perm_var, value='users',
                       font=('', 9)).pack(side='left', padx=15)

        # 提示当前权限
        tk.Label(win, text=f'当前密码: {data["users_password"][idx]}',
                 fg='#888', font=('', 8)).pack(pady=(5, 0))

        def do_save():
            new_pwd = pwd_entry.get()
            pwd_confirm = pwd_confirm_entry.get()

            # 密码校验
            if new_pwd:
                if new_pwd != pwd_confirm:
                    messagebox.showerror('错误', '两次输入的密码不一致')
                    return
                data['users_password'][idx] = new_pwd

            data['users_root'][idx] = perm_var.get()

            try:
                self._save_users_data(data)
            except Exception as e:
                messagebox.showerror('保存失败', str(e))
                return

            # 如果修改了当前登录用户, 同步更新运行时状态
            if target == self.users_name:
                global root_permission
                self.users_permission_detailed = perm_var.get()
                root_permission = (perm_var.get() == 'root')

            messagebox.showinfo('成功', f'用户 "{target}" 已更新')
            win.destroy()

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text='保存修改', command=do_save, width=12,
                  bg='#4CAF50', fg='white').pack(side='left', padx=10)
        tk.Button(btn_frame, text='取消', command=win.destroy, width=12).pack(side='left', padx=10)

        win.grab_set()
        main_tk.wait_window(win)
        return f'用户 "{target}" 修改完成'

    def _add_user_gui(self):
        """GUI: 添加新用户"""
        win = tk.Toplevel(main_tk)
        win.title('添加新用户')
        win.geometry('340x400')
        win.resizable(False, False)

        tk.Label(win, text='创建新用户', font=('', 11, 'bold')).pack(pady=10)

        # 用户名
        tk.Label(win, text='用户名:').pack(anchor='w', padx=20)
        name_entry = tk.Entry(win, width=35)
        name_entry.pack(pady=5)

        # 密码
        tk.Label(win, text='密码:').pack(anchor='w', padx=20)
        pwd_entry = tk.Entry(win, show='*', width=35)
        pwd_entry.pack(pady=5)

        # 确认密码
        tk.Label(win, text='确认密码:').pack(anchor='w', padx=20)
        pwd_confirm_entry = tk.Entry(win, show='*', width=35)
        pwd_confirm_entry.pack(pady=5)
        

        # 权限
        tk.Label(win, text='用户权限:').pack(anchor='w', padx=20, pady=(10, 0))
        perm_var = tk.StringVar(value='users')
        perm_frame = tk.Frame(win)
        perm_frame.pack(pady=5)
        tk.Radiobutton(perm_frame, text='root  (管理员)',
                       variable=perm_var, value='root',
                       font=('', 9)).pack(side='left', padx=15)
        tk.Radiobutton(perm_frame, text='users (普通用户)',
                       variable=perm_var, value='users',
                       font=('', 9)).pack(side='left', padx=15)

        def do_add():
            new_name = name_entry.get().strip()
            new_pwd = pwd_entry.get()
            pwd_confirm = pwd_confirm_entry.get()

            if not new_name:
                messagebox.showerror('错误', '用户名不能为空')
                return
            if not new_pwd:
                messagebox.showerror('错误', '密码不能为空')
                return
            if new_pwd != pwd_confirm:
                messagebox.showerror('错误', '两次输入的密码不一致')
                return
            try:
                data = self._load_users_data()
            except Exception as e:
                messagebox.showerror('错误', f'读取用户数据失败: {e}')
                return

            if new_name in data['users_name']:
                messagebox.showerror('错误', f'用户 "{new_name}" 已存在')
                return

            data['users_name'].append(new_name)
            data['users_password'].append(new_pwd)
            data['users_root'].append(perm_var.get())

            try:
                self._save_users_data(data)
            except Exception as e:
                messagebox.showerror('保存失败', str(e))
                return

            messagebox.showinfo('成功', f'用户 "{new_name}" 已创建')
            win.destroy()

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text='添加用户', command=do_add, width=12,
                  bg='#4CAF50', fg='white').pack(side='left', padx=10)
        tk.Button(btn_frame, text='取消', command=win.destroy, width=12).pack(side='left', padx=10)

        win.grab_set()
        main_tk.wait_window(win)
        return '用户添加操作已完成'

    def _delete_user(self, target):
        """删除用户"""
        try:
            data = self._load_users_data()
        except Exception as e:
            return f'读取用户数据失败: {e}'

        if target not in data['users_name']:
            return f'用户 "{target}" 不存在'

        if target == self.users_name:
            return '不能删除当前登录的用户'

        idx = data['users_name'].index(target)

        # 确认对话框
        confirmed = [False]
        win = tk.Toplevel(main_tk)
        win.title('确认删除')
        win.geometry('300x130')
        win.resizable(False, False)
        tk.Label(win, text=f'确认要删除用户 "{target}" 吗？',
                 font=('', 10)).pack(pady=15)
        tk.Label(win, text='此操作不可撤销！', fg='red').pack()

        def do_delete():
            confirmed[0] = True
            win.destroy()

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text='确认删除', command=do_delete, width=12,
                  bg='#f44336', fg='white').pack(side='left', padx=10)
        tk.Button(btn_frame, text='取消', command=win.destroy, width=12).pack(side='left', padx=10)

        win.grab_set()
        main_tk.wait_window(win)

        if not confirmed[0]:
            return '已取消删除'

        del data['users_name'][idx]
        del data['users_password'][idx]
        del data['users_root'][idx]

        try:
            self._save_users_data(data)
        except Exception as e:
            return f'保存失败: {e}'

        return f'用户 "{target}" 已删除'
def sign_in():
    #账户与密码读取
    global users_permission, root_permission
    with open(os.path.join(__run_path__, 'users_data.json'), 'r', encoding='utf-8') as f:
        list_data = json.load(f)
        list_name = list_data['users_name']
        list_password = list_data['users_password']
        list_root = list_data['users_root']
    input_name = tk_input_name.get()
    input_password = tk_input_key.get()

    # 逐用户匹配用户名与密码，避免认证绕过
    users_permission = False
    users_permission_detailed = ''
    for i in range(len(list_name)):
        if list_name[i] == input_name and list_password[i] == input_password:
            users_permission = True
            users_permission_detailed = list_root[i]
            if list_root[i] == 'root':
                root_permission = True
            break

    if users_permission:
        global root
        root = SYSTEM_OS(__system_name__, input_name, users_permission_detailed)
    else:
        messagebox.showerror('错误', '用户名或密码错误')
    main()

def run_cmd_text(text_input):
    # 分割命令和参数（如 "open_file test.txt" → cmd="open_file", args="test.txt"）
    parts = text_input.split(maxsplit=1)
    cmd = parts[0]
    args = parts[1] if len(parts) > 1 else ''
    agree_run = ['turn_off_system', 'message', 'help', 'open','users']
    if cmd in agree_run:
        if cmd == 'help':
            return root.help
        elif cmd == 'turn_off_system':
            return root.turn_off_system
        elif cmd == 'message':
            return root.message
        elif cmd == 'open':
            if not args:
                return '用法: open <文件路径>'
            return root.open_file(args)
        elif cmd == 'users':
            return root.users(args)
        return f'命令 "{cmd}" 暂未实现'
    else:
        return ('错误，未存在命令\n'
                '你可以输入help来查询可用命令')

def main():
    global users_permission
    global root_permission
    global main_tk
    print(users_permission,root_permission)
    if users_permission:
        sign_tk.destroy()
        main_tk = tk.Tk()
        main_tk.title(f'bash_root:{root_permission}')
        main_tk.geometry('500x500')
        return_text_tk = tk.Text(main_tk,wrap='word',font=('Consolas',10))
        return_text_tk.pack(fill='both',expand=True,padx=5,pady=5)
        Entry_cmd = tk.Entry(main_tk,font=('Consolas',10))
        Entry_cmd.pack(side='left',fill='x',expand=True)
        def return_set_cmd():
            text_input = Entry_cmd.get()
            return_text = run_cmd_text(text_input)
            # test = '测试输出'
            return_text_tk.insert('end', f">>> {text_input}\n")
            return_text_tk.insert('end',return_text + '\n')
            return_text_tk.see('end')
            Entry_cmd.delete(0, 'end')
        Entry_cmd.bind('<Return>',lambda e:return_set_cmd())
        main_tk.mainloop()

#登录窗口
sign_tk = tk.Tk()
sign_tk.title('shell_open')
sign_tk.geometry('300x200')
first_label = tk.Label(sign_tk, text="name and users key: ")
first_label.pack()
tk_input_name = tk.Entry(sign_tk)
tk_input_name.pack(pady=10)
tk_input_key = tk.Entry(sign_tk,show='*')
tk_input_key.pack(pady=10)
first_button = tk.Button(sign_tk,text='submit',command=sign_in)
first_button.pack(pady=10)
sign_tk.mainloop()