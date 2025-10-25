# Omnigence.ai - AI报价单生成系统

一个基于AI对话的智能报价单生成系统，通过与AI模型对话来自动生成专业的项目报价单。

## 🌟 功能特性

- **AI对话生成**：通过自然语言对话收集项目信息
- **智能报价单填充**：AI自动生成并填充报价单字段
- **实时预览**：右侧实时显示报价单内容
- **搜索功能**：快速检索历史报价单
- **PDF导出**：一键导出专业PDF格式报价单
- **本地存储**：自动保存历史报价单记录

## 🚀 快速开始

### 前置要求

- **Node.js >= 22.12.0** (推荐 22.21.0)
  - 由于使用了 Vite 7，需要 Node.js 22 以上版本
  - 如果您的系统是 Node.js 16，请查看 [Node版本管理指南](./NODE_VERSION_GUIDE.md)
- npm 或 yarn

### 安装

```bash
# 克隆项目
git clone <repository-url>

# 进入项目目录
cd Omnigence.ai

# 安装依赖（使用 Node.js 22）
npm install
```

### 开发

**最简单的方式（推荐）：**

```bash
# 方式 1：使用启动脚本
./start-dev.sh

# 方式 2：使用 npm 脚本
npm run dev:node22
```

**标准方式：**

```bash
# 如果已配置 Node.js 22 环境
npm run dev

# 项目将在 http://localhost:5173 运行
```

**Docker 方式（完全隔离）：**

```bash
# 使用 Docker（无需安装 Node.js）
docker-compose up
```

> 💡 **提示**：更多启动方式请查看 [快速开始指南](./QUICK_START.md)

### 构建

```bash
# 构建生产版本（使用 Node.js 22）
npm run build:node22

# 预览生产构建
npm run preview:node22

# 或使用标准命令（需先配置 Node 22 环境）
npm run build
npm run preview
```

## 📁 项目结构

```
Omnigence.ai/
├── src/
│   ├── components/          # React组件
│   │   ├── ChatBox/        # 对话框组件
│   │   ├── SearchBar/      # 搜索栏组件
│   │   └── QuotationSheet/ # 报价单组件
│   ├── services/           # API服务
│   │   └── aiService.js    # AI模型接口
│   ├── utils/              # 工具函数
│   │   ├── pdfExport.js    # PDF导出工具
│   │   └── storage.js      # 本地存储工具
│   ├── App.jsx             # 主应用组件
│   ├── App.css             # 全局样式
│   ├── main.jsx            # 应用入口
│   └── index.css           # Tailwind样式
├── public/                 # 静态资源
├── index.html              # HTML模板
├── package.json            # 项目配置
├── vite.config.js          # Vite配置
├── tailwind.config.js      # Tailwind配置
└── README.md              # 项目说明
```

## 🔧 技术栈

- **前端框架**：React 18
- **构建工具**：Vite
- **样式**：Tailwind CSS
- **状态管理**：React Hooks
- **存储**：LocalStorage
- **PDF导出**：浏览器打印API

## 📝 使用说明

### 1. 创建报价单

1. 在左侧对话框中与AI交流
2. 提供以下信息：
   - 客户公司名称
   - 项目名称
   - 预算范围
   - 联系方式
   - 地址
3. AI会自动生成报价单并在右侧显示
4. 可以手动编辑报价单内容
5. 点击"Download PDF"导出

### 2. 搜索历史报价单

1. 在右上角搜索框输入：
   - 报价单编号
   - 客户名称
   - 项目名称
2. 系统会自动搜索并显示匹配结果

### 3. 配置AI模型

编辑 `src/services/aiService.js` 文件：

```javascript
const API_CONFIG = {
  endpoint: 'YOUR_API_ENDPOINT',  // 您的AI模型API地址
  apiKey: 'YOUR_API_KEY',         // API密钥
  model: 'gpt-4',                 // 使用的模型
}
```

支持的AI模型：
- OpenAI GPT-4 / GPT-3.5
- Anthropic Claude
- 其他兼容OpenAI格式的模型

## 🎨 自定义样式

项目使用Tailwind CSS，可以通过以下方式自定义：

1. 编辑 `tailwind.config.js` 修改主题
2. 在组件中使用Tailwind类名
3. 在 `src/index.css` 中添加全局样式

## 📦 部署

### Vercel

```bash
npm run build
# 将 dist 目录部署到 Vercel
```

### Netlify

```bash
npm run build
# 将 dist 目录部署到 Netlify
```

## 🔐 环境变量

创建 `.env` 文件：

```env
VITE_AI_API_ENDPOINT=your_api_endpoint
VITE_AI_API_KEY=your_api_key
VITE_AI_MODEL=gpt-4
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 联系方式

如有问题或建议，请联系项目维护者。

---

**注意**：这是前端应用，需要配置AI模型API才能使用完整功能。目前使用模拟数据进行演示。
