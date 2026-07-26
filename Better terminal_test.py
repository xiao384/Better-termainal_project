import json
import os
import subprocess
import tkinter as tk
import sys
from tkinter import ttk
#系统检测
global system_name
system_name = os.name
#系统操作_新
global main_os
class main_os:
    def __init__(self,name,key,root_permission):
        self.root_permission = root_permission
        self.name = name
        self.key = key
    @property#用户信息
    def users(self):
        print('users:',self.name)
        print('password:',self.key)
        print('root:',self.root_permission)
    @property
    def turn_off_system(self):
        if system_name == 'nt':
            eval(__import__('os').system('shutdown /s /t 0'))
        elif system_name == 'posix':
            pass
        print(system_name)
    #文件打开[静态需加括号(文件路径)]
    #先read读取文件内容后修改复写
    @staticmethod
    def open_file(file_path):
        print(file_path)
        with open(file_path,'r',encoding='utf-8') as f:
            file_text = f.read()
            print(file_text)
        open_file_tk = tk.Toplevel(main_tk)
        text = tk.Text(open_file_tk,width=40,height=10,font=("Consolas", 10))
        text.insert("1.0",file_text)
        text.pack(pady=10)
    #输出可执行命令
    @property
    def help(self):
        pass
#程序主体_运行
def first():
    #验证初始化和账户名字与密码读取
    global true_false
    global root_permission
    root_permission = False
    true_false = False
    #初始化(变量)
    global file_path
    file_path = None
    path = os.getcwd()
    path_users_data = os.path.join(path,'users_data.json')
    #
    with open(path_users_data,'r',encoding="utf-8") as f:
        users_data = json.load(f)
        name_data = users_data["users_name"]
        key_data = users_data["users_password"]
        permission_data = users_data["users_root"]
        print(name_data,key_data,permission_data)#账户与密码_测试输出
    #判断账号
    users_input_name = tk_input_name.get()
    users_input_key = tk_input_key.get()
    for i in range(len(name_data)):
        if name_data[i] == users_input_name:
            if key_data[i] == users_input_key:
                true_false = True
                break
    else:
        true_false = False
    if permission_data[i] == "root":#用户权限root/...
        root_permission = True
    print(true_false,"root_permission:",root_permission)
    global root
    root = main_os(users_input_name,users_input_key,root_permission)#全局系统操作变量 root.[]
    #输入窗口
    def main_tk():
        def handle_input():#运行
            input_old = main_input_eval.get()
            input_list = list(input_old)
            for i in range(len(input_list)):
                if input_list[i] == '(':
                    break
                if input_list[i] == ' ':
                    input_list[i] = '.'
                input_old = ''.join(input_list)
            # if ' ' in input_old:#输入处理：空格改为点[对象.方法]#需优化
            #     input_old = input_old.replace(' ','.')
            #[               测试使用（输出处理后的结果)
            print(input_old)
            print(input_list)
            #]
            try:
                eval(input_old)
                ...
            except AttributeError:
                print('请检查语句是否正确，你可以输入root help来获取可执行命令')
            except:
                print('错误')
        if  true_false == True:
            first_root.destroy()
            global main_tk
            main_tk = tk.Tk()
            main_tk.geometry('300x300')
            main_tk.title(f'bash-{permission_data[i]}')
            main_input_eval = tk.Entry(main_tk)
            main_input_eval.pack(pady=10)
            eval_button = tk.Button(main_tk,text='run',command=handle_input)
            eval_button.pack()
            main_tk.mainloop()
    main_tk()
#登录窗口
first_root = tk.Tk()
first_root.title('shell_open')
first_root.geometry('300x400')
first_lable = tk.Label(first_root, text="name and users key: ")
first_lable.pack()
tk_input_name = tk.Entry(first_root)
tk_input_name.pack(pady=10)
tk_input_key = tk.Entry(first_root,show='*')
tk_input_key.pack(pady=10)
first_button = tk.Button(first_root,text='submit',command=first)
first_button.pack(pady=10)
first_root.mainloop()