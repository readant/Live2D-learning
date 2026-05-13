@echo off
chcp 65001 >nul
echo ================================================
echo 国内开发环境快速配置脚本
echo ================================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到 Python，请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

:: 检查 Python 版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PY_VERSION=%%i
echo [INFO] Python 版本: %PY_VERSION%

:: 配置 pip 镜像
echo.
echo [INFO] 配置 pip 国内镜像...
set PIP_CONFIG_DIR=%USERPROFILE%\pip
if not exist "%PIP_CONFIG_DIR%" mkdir "%PIP_CONFIG_DIR%"

echo [global] > "%PIP_CONFIG_DIR%\pip.ini"
echo index-url = https://pypi.tuna.tsinghua.edu.cn/simple >> "%PIP_CONFIG_DIR%\pip.ini"
echo timeout = 60 >> "%PIP_CONFIG_DIR%\pip.ini"
echo trusted-host = pypi.tuna.tsinghua.edu.cn >> "%PIP_CONFIG_DIR%\pip.ini"
echo [SUCCESS] pip 镜像配置完成

:: 创建虚拟环境
echo.
echo [INFO] 创建虚拟环境...
if exist "venv" (
    echo [WARNING] 虚拟环境已存在，跳过创建
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo [SUCCESS] 虚拟环境创建完成
)

:: 安装依赖
echo.
echo [INFO] 安装项目依赖...
venv\Scripts\pip.exe install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] 依赖安装失败
    pause
    exit /b 1
)
echo [SUCCESS] 依赖安装完成

:: 显示使用说明
echo.
echo ================================================
echo 开发环境配置完成！
echo ================================================
echo.
echo 1. 激活虚拟环境:
echo    venv\Scripts\activate.bat
echo.
echo 2. 运行项目:
echo    python main.py
echo.
echo 3. 学习资源:
echo    - 学习路径指南: learning_notes/00_学习路径指南.md
echo    - 国内工具配置: learning_notes/09_国内工具配置指南.md
echo    - 学习笔记模板: learning_notes/10_学习笔记模板.md
echo.
echo ================================================
echo 配置完成！祝您学习愉快！🎉
echo ================================================

pause
