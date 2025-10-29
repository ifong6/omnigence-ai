# 🐳 Docker 使用指南

本项目支持使用 Docker 进行容器化部署，无需在本地安装 Node.js 或 Python 环境。

## 📋 前置要求

- **Docker Desktop**（Windows/Mac）或 **Docker Engine**（Linux）
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

### 安装 Docker Desktop

**Windows/Mac：**
1. 访问 [Docker Desktop 官网](https://www.docker.com/products/docker-desktop)
2. 下载并安装 Docker Desktop
3. 启动 Docker Desktop
4. 确认 Docker 正在运行（系统托盘图标）

**Linux：**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
```

---

## 🚀 快速启动

### Windows 用户（推荐）

**方式 1：使用批处理脚本**
```cmd
# 启动项目
docker-start.bat

# 查看日志
docker-logs.bat

# 停止项目
docker-stop.bat
```

**方式 2：使用命令行**
```cmd
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### Linux/Mac 用户

```bash
# 启动项目
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 🌐 访问地址

服务启动后，访问：

- **前端**：http://localhost:5173
- **后端API**：http://localhost:8000
- **后端健康检查**：http://localhost:8000/docs（FastAPI自动生成的API文档）

---

## 📂 项目结构

```
docker-compose.yml      # Docker 编排配置
Dockerfile              # 前端镜像配置
Dockerfile.backend      # 后端镜像配置
.dockerignore          # Docker 忽略文件
docker-start.bat       # Windows 启动脚本
docker-stop.bat        # Windows 停止脚本
docker-logs.bat        # Windows 日志脚本
```

---

## ⚙️ 环境变量配置

确保项目根目录有 `.env` 文件：

```env
GOOGLE_API_KEY=your_google_api_key_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=omnigence
POSTGRES_USER=admin
POSTGRES_PASSWORD=your_password_here
```

---

## 🛠️ Docker 常用命令

### 查看运行状态
```bash
docker-compose ps
```

### 查看实时日志
```bash
# 所有服务
docker-compose logs -f

# 仅前端
docker-compose logs -f frontend

# 仅后端
docker-compose logs -f backend
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启前端
docker-compose restart frontend

# 重启后端
docker-compose restart backend
```

### 重新构建镜像
```bash
# 重新构建所有镜像
docker-compose build

# 重新构建并启动
docker-compose up -d --build

# 仅重新构建前端
docker-compose build frontend

# 仅重新构建后端
docker-compose build backend
```

### 进入容器
```bash
# 进入前端容器
docker exec -it omnigence-frontend sh

# 进入后端容器
docker exec -it omnigence-backend bash
```

### 清理资源
```bash
# 停止并删除容器
docker-compose down

# 停止并删除容器、网络、卷
docker-compose down -v

# 清理未使用的镜像
docker image prune -a
```

---

## 🔧 故障排查

### 1. 端口被占用

**错误信息：**
```
Error: bind: address already in use
```

**解决方案：**
```bash
# Windows - 查看端口占用
netstat -ano | findstr :5173
netstat -ano | findstr :8000

# 停止占用端口的进程
taskkill /PID <进程ID> /F
```

### 2. Docker 磁盘空间不足

**解决方案：**
```bash
# 清理未使用的镜像和容器
docker system prune -a

# 查看磁盘使用情况
docker system df
```

### 3. 构建失败

**解决方案：**
```bash
# 清理缓存重新构建
docker-compose build --no-cache

# 删除所有容器后重新启动
docker-compose down -v
docker-compose up -d --build
```

### 4. 无法访问服务

**检查步骤：**
```bash
# 1. 确认容器正在运行
docker-compose ps

# 2. 查看容器日志
docker-compose logs frontend
docker-compose logs backend

# 3. 确认网络连接
docker network ls
docker network inspect omnigence_omnigence-network
```

---

## 🆚 Docker vs 本地开发对比

| 特性 | Docker | 本地开发 |
|------|--------|---------|
| 环境隔离 | ✅ 完全隔离 | ❌ 依赖本地环境 |
| 安装依赖 | ✅ 自动安装 | ❌ 手动安装 |
| 跨平台 | ✅ 一致性高 | ⚠️ 可能有差异 |
| 启动速度 | ⚠️ 稍慢（首次） | ✅ 快速 |
| 资源占用 | ⚠️ 较高 | ✅ 较低 |
| 热更新 | ✅ 支持（通过卷挂载） | ✅ 支持 |
| 调试便利性 | ⚠️ 需进入容器 | ✅ 直接调试 |

---

## 📝 开发模式 vs 生产模式

### 当前配置（开发模式）
- 启用热更新（HMR）
- 挂载源代码卷
- 暴露调试端口
- 详细日志输出

### 生产模式配置（待优化）
```yaml
# 生产环境需要修改 docker-compose.yml
environment:
  - NODE_ENV=production
# 并使用构建好的静态文件
```

---

## 🎯 最佳实践

1. **开发阶段**：使用本地开发（`npm run dev` + `python main_server.py`）
2. **测试阶段**：使用 Docker 确保环境一致性
3. **部署阶段**：使用 Docker 容器化部署到云服务

---

## 📞 需要帮助？

如遇问题，请检查：
1. Docker Desktop 是否正在运行
2. `.env` 文件是否正确配置
3. 端口 5173 和 8000 是否被占用
4. 查看容器日志：`docker-compose logs -f`

---

**提示**：首次构建可能需要 5-10 分钟下载依赖，请耐心等待。后续启动会很快！🚀

