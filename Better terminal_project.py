#用于测试项目
import json
import os
import platform
# import subprocess
import tkinter as tk
# import sys
# from email import message
# from tkinter import ttk
from tkinter import messagebox
#系统检测
'''以下变量不可修改'''
__system_name__ = os.name
__run_path__ = os.path.dirname(__file__)
root_permission = False
users_permission = False
#系统操作
class SYSTEM_OS:
    def __init__(self,__system_name__):
        self.system_name = __system_name__
    @property
    def help(self):
        system_name = f'{platform.system()}{platform.release()}-{platform.version()}\n{platform.machine()}'
        return system_name
root = SYSTEM_OS(__system_name__)
def sign_in():
    #账户与密码读取
    global users_permission
    global root_permission
    i = 0
    with open(__run_path__+'/users_data.json', 'r', encoding='utf-8') as f:
        list_data = json.load(f)
        list_name = list_data['users_name']
        list_password = list_data['users_password']
        list_root = list_data['users_root']
        print(list_name,list_password,list_root)
    input_name = tk_input_name.get()
    input_password = tk_input_key.get()
    if input_name in list_name and input_password in list_password:
        for i in range(len(input_name)):
            if list_name[i] == input_name:
                if list_password[i] == input_password:
                    users_permission = True
                    break
        else:
            users_permission = False
        if list_root[i] == "root" and users_permission:
            root_permission = True
    else:
        messagebox.showerror('错误','用户不存在')
    main()
def run_cmd_text(text_input):
    agree_run = ['1','2','3','help']
    if text_input in agree_run:
        if text_input == 'help':
            return root.help
        return text_input
    else:
        return '错误，未存在命令\n你可以输入root.help来查询可用命令'
def main():
    global users_permission
    global root_permission
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
sign_tk.geometry('300x400')
first_label = tk.Label(sign_tk, text="name and users key: ")
first_label.pack()
tk_input_name = tk.Entry(sign_tk)
tk_input_name.pack(pady=10)
tk_input_key = tk.Entry(sign_tk,show='*')
tk_input_key.pack(pady=10)
first_button = tk.Button(sign_tk,text='submit',command=sign_in)
first_button.pack(pady=10)
sign_tk.mainloop()