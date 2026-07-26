# 1.VScode管理
## 以管理员身份运行vscode，解决python enve 不能运行脚本问题
1.进入TERMINAL
2. 执行：get-ExecutionPolicy，显示Restricted，表示状态是禁止的;
3. 执行：set-ExecutionPolicy RemoteSigned;
        或 Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
4. 这时再执行get-ExecutionPolicy，就显示RemoteSigned;

## 将TERMINIAL修改支持 GBK,解决TERMINIAL中文乱码问题
【设置】【时间和语言】【管理语言设置】【管理】【更改系统区域设置】 将 beta版挑勾，重启

## 装入显示运行图标
Code Runner
code runner [设置] defaultLanguage:设置为PYTHON

## F1 首选项：打开用户设置JSON 修改运行的虚拟环境
    "code-runner.executorMap": {
          "python": "D:/MyPrograms/数据建模/dproc/Scripts/python -u", ##修改设置为VENV的路径
    }   

<br>

# 2.安装python和创建虚拟环境

在windows app中安装Python3.13  https://www.python.org/downloads/windows/

在Python 3.3及以上版本中，可以使用内置的venv模块来创建虚拟环境。以下是创建虚拟环境的步骤：
创建环境： python -m venv gonghan-ISA 其中，ENV_DIR是存放环境的目录，一般使用venv作为目录名
激活环境： 在Windows上： .\ENV_DIR\Scripts\activate   .\gonghan-ISA\Scripts\activate 
退出环境： deactivate
删除环境： 直接删除整个环境的安装目录即可
使用虚拟环境

************
使用F1 - PYTHON 选择解释器  “Python: Select Interpreter”并选择该命令。
 选择当前的VENV


# 3.pip 管理

Python -m pip install --upgrade pip

pip install requests
pip install --upgrade requests
pip uninstall requests

pip list #列出所有包


# 4.管理环境

命令导出当前环境中的所有包
pip freeze > requirements.txt
命令导入所有包
pip install -r requirements.txt



# 5.编译成C++，再编译成exe Nuitka - 真正的编译器

安装
pip install nuitka

基本编译
python -m nuitka --standalone mian.py

单文件编译
python -m nuitka --onefile mian.py

无控制台窗口
python -m nuitka --onefile --windows-disable-console main.py


# 6.pyinstaller 打包


pip install pyinstaller
打包单个文件
pyinstaller -F your_script.py
 
打包多个py文件
pyinstaller [主文件] -p [其他文件1] -p [其他文件2]
 
打包时去除cmd框
pyinstaller -F XXX.py --noconsole
 
打包加入exe图标   picturename.ico是图片
pyinstaller -F -i picturename.ico -w XXX.py
 
打包去除控制台
pyinstaller -w xxx.py
 
打包方便查看报错，可看到控制台
pyinstaller -c xxx.py
"""
错误
class RegexFlag(enum.IntFlag):
AttributeError: module 'enum' has no attribute 'IntFlag'
查看是否安装enum34包
卸载enum34即可，python程序可正常运行
"""

# NiceGUI
pip install nicegui

# 安装Quarto 
- 安装 Quarto VS Code Extension
- py -m pip install jupyter matplotlib plotly pandas

# github
hozx2025/Gonghanzheng-ISA-SP
	git remote add origin https://github.com/hozx2025/Gonghanzheng-ISA-SP.git
https://github.com/hozx2025/Gonghanzheng-ISA-SP.git
	commit后git push -u origin main --force  #强制覆盖远端

https://hozx2025.github.io/Gonghanzheng-ISA-SP/
	
git add .
git commit -m "节点命名"
git push ##提交remote
	
git log  #察看版本
git reset --hard  #
