@echo off
echo ========================================
echo   Omnigence.ai Docker 启动脚本
echo ========================================
echo.

REM 检查 Docker 是否安装
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未检测到 Docker，请先安装 Docker Desktop
    echo 下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM 检查 Docker 是否运行
docker info >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] Docker 未运行，请启动 Docker Desktop
    pause
    exit /b 1
)

REM 检查 .env 文件
if not exist .env (
    echo [警告] .env 文件不存在
    echo [提示] 请确保已配置 Google API Key
    echo.
)

echo [1/3] 停止现有容器...
docker-compose down

echo.
echo [2/3] 构建镜像...
docker-compose build

echo.
echo [3/3] 启动服务...
docker-compose up -d

echo.
echo ========================================
echo   服务已启动！
echo ========================================
echo.
echo   前端地址: http://localhost:5173
echo   后端地址: http://localhost:8000
echo.
echo   查看日志: docker-compose logs -f
echo   停止服务: docker-compose down
echo.
echo ========================================

REM 等待5秒后打开浏览器
timeout /t 5 /nobreak >nul
start http://localhost:5173

pause

