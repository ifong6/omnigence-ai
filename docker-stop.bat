@echo off
echo ========================================
echo   Omnigence.ai Docker 停止脚本
echo ========================================
echo.

echo [1/2] 停止所有容器...
docker-compose down

echo.
echo [2/2] 清理完成
echo.
echo ========================================
echo   所有服务已停止
echo ========================================
echo.

pause

