#!/bin/bash

# Omnigence.ai 开发服务器启动脚本
# 自动使用 Node.js 22

echo "🚀 启动 Omnigence.ai 开发服务器..."
echo "📦 使用 Node.js 22.21.0"

# 设置 Node.js 22 路径
export PATH="/opt/homebrew/opt/node@22/bin:$PATH"

# 检查 Node 版本
echo "✓ Node 版本: $(node --version)"
echo "✓ npm 版本: $(npm --version)"
echo ""

# 启动开发服务器
npm run dev

