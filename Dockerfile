# 使用 Node.js 22 官方镜像
FROM node:22-alpine

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制项目文件
COPY . .

# 暴露 Vite 开发服务器端口
EXPOSE 5173

# 默认命令
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

