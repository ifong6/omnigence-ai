/**
 * API配置文件
 * 集中管理所有API相关的配置
 */

// 从环境变量读取配置
const getEnvConfig = () => ({
  // AI模型API配置
  AI_API_ENDPOINT: 'https://www.chatgtp.cn/v1/messages',
  AI_API_KEY: 'sk-MMWb8B4jvJ0SPV68RhwKIE04xPcv3fzM5ZUCYONwaxBXcbtD',
  AI_MODEL: 'gpt-4o-mini',
  
  // 后端API配置（Main Flow）
  BACKEND_API_URL: 'http://localhost:8000',
  
  // 其他API配置
  TIMEOUT: 30000, // 30秒超时
})

// API配置对象
export const apiConfig = {
  // AI模型配置
  ai: {
    endpoint: getEnvConfig().AI_API_ENDPOINT,
    apiKey: getEnvConfig().AI_API_KEY,
    model: getEnvConfig().AI_MODEL,
    timeout: getEnvConfig().TIMEOUT,
    
    // 可选配置
    temperature: 0.7,
    maxTokens: 2000,
  },
  
  // 后端API配置
  backend: {
    baseURL: getEnvConfig().BACKEND_API_URL,
    timeout: getEnvConfig().TIMEOUT,
    
    // API端点
    endpoints: {
      callMainFlow: '/call-main-flow',        // 主工作流
      humanFeedback: '/human-in-loop/feedback', // 人工反馈
      quotations: '/quotations',
      search: '/quotations/search',
      save: '/quotations/save',
      delete: '/quotations/delete',
    }
  },
  
  // 请求头配置
  headers: {
    'Content-Type': 'application/json',
  }
}

export default apiConfig

