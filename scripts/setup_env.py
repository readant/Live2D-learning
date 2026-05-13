#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国内开发环境快速配置脚本
适用于 Windows/Linux/Mac 系统
自动配置国内镜像源，加速依赖安装
"""

import os
import sys
import platform
import subprocess
import shutil

# 国内镜像地址
PYPI_MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple"
GITHUB_MIRROR = "https://hub.fastgit.org"

def print_info(msg):
    """打印信息"""
    print(f"\033[94m[INFO] {msg}\033[0m")

def print_success(msg):
    """打印成功信息"""
    print(f"\033[92m[SUCCESS] {msg}\033[0m")

def print_error(msg):
    """打印错误信息"""
    print(f"\033[91m[ERROR] {msg}\033[0m")

def print_warning(msg):
    """打印警告信息"""
    print(f"\033[93m[WARNING] {msg}\033[0m")

def get_os_type():
    """获取操作系统类型"""
    os_name = platform.system()
    if os_name == "Windows":
        return "windows"
    elif os_name == "Linux":
        return "linux"
    elif os_name == "Darwin":
        return "mac"
    else:
        return "unknown"

def check_python_version():
    """检查 Python 版本"""
    try:
        version = sys.version_info
        if version >= (3, 10):
            print_success(f"Python 版本: {version.major}.{version.minor}.{version.micro} ✓")
            return True
        else:
            print_error(f"Python 版本过低: {version.major}.{version.minor}.{version.micro}")
            print_error("请安装 Python 3.10 或更高版本")
            return False
    except Exception as e:
        print_error(f"检查 Python 版本失败: {e}")
        return False

def configure_pip_mirror():
    """配置 pip 国内镜像"""
    os_type = get_os_type()
    if os_type == "windows":
        pip_config_dir = os.path.join(os.path.expanduser("~"), "pip")
        pip_config_file = os.path.join(pip_config_dir, "pip.ini")
    else:
        pip_config_dir = os.path.join(os.path.expanduser("~"), ".pip")
        pip_config_file = os.path.join(pip_config_dir, "pip.conf")
    
    config_content = f"""[global]
index-url = {PYPI_MIRROR}
timeout = 60
trusted-host = pypi.tuna.tsinghua.edu.cn
"""
    
    try:
        os.makedirs(pip_config_dir, exist_ok=True)
        with open(pip_config_file, "w", encoding="utf-8") as f:
            f.write(config_content)
        print_success(f"已配置 pip 镜像: {pip_config_file}")
        return True
    except Exception as e:
        print_error(f"配置 pip 镜像失败: {e}")
        return False

def create_virtualenv():
    """创建虚拟环境"""
    venv_dir = "venv"
    if os.path.exists(venv_dir):
        print_warning(f"虚拟环境已存在: {venv_dir}")
        return True
    
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", venv_dir],
            check=True,
            capture_output=True,
            text=True
        )
        print_success(f"已创建虚拟环境: {venv_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"创建虚拟环境失败: {e.stderr}")
        return False

def install_dependencies():
    """安装项目依赖"""
    os_type = get_os_type()
    
    # 确定 pip 路径
    if os_type == "windows":
        pip_path = os.path.join("venv", "Scripts", "pip.exe")
        activate_path = os.path.join("venv", "Scripts", "activate.bat")
    else:
        pip_path = os.path.join("venv", "bin", "pip")
        activate_path = os.path.join("venv", "bin", "activate")
    
    if not os.path.exists(pip_path):
        print_error(f"pip 路径不存在: {pip_path}")
        return False
    
    try:
        print_info("正在安装依赖（使用国内镜像）...")
        result = subprocess.run(
            [pip_path, "install", "-r", "requirements.txt"],
            check=True,
            capture_output=True,
            text=True
        )
        print_success("依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"依赖安装失败: {e.stderr}")
        return False

def show_usage():
    """显示使用说明"""
    os_type = get_os_type()
    
    print("\n" + "="*60)
    print("开发环境配置完成！")
    print("="*60)
    
    if os_type == "windows":
        activate_cmd = "venv\\Scripts\\activate.bat"
    else:
        activate_cmd = "source venv/bin/activate"
    
    print(f"\n1. 激活虚拟环境:")
    print(f"   {activate_cmd}")
    
    print(f"\n2. 运行项目:")
    print(f"   python main.py")
    
    print(f"\n3. 项目结构:")
    print("   Live2D-learning/")
    print("   ├── src/          # 源代码")
    print("   ├── examples/     # 示例代码")
    print("   ├── exercises/    # 实践练习")
    print("   ├── learning_notes/ # 学习笔记")
    print("   └── main.py       # 程序入口")
    
    print(f"\n4. 学习资源:")
    print("   - 学习路径指南: learning_notes/00_学习路径指南.md")
    print("   - 国内工具配置: learning_notes/09_国内工具配置指南.md")
    print("   - 学习笔记模板: learning_notes/10_学习笔记模板.md")
    
    print("\n" + "="*60)

def main():
    """主函数"""
    print("\n" + "="*60)
    print("国内开发环境快速配置脚本")
    print("="*60)
    
    # 检查 Python 版本
    if not check_python_version():
        sys.exit(1)
    
    # 配置 pip 镜像
    if not configure_pip_mirror():
        sys.exit(1)
    
    # 创建虚拟环境
    if not create_virtualenv():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 显示使用说明
    show_usage()
    
    print_success("\n配置完成！祝您学习愉快！🎉")

if __name__ == "__main__":
    main()
