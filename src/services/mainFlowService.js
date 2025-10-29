/**
 * Main Flow API 服务
 * 用于与 FastAPI 后端的 Multi-Agent 系统通信
 */

import { apiConfig } from '../config'

// 使用后端配置
const BACKEND_CONFIG = apiConfig.backend

// 生成唯一的 session ID
const generateSessionId = () => {
  return `session-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
}

// 存储当前 session ID
let currentSessionId = generateSessionId()

/**
 * 重置 session（开始新对话）
 */
export const resetSession = () => {
  currentSessionId = generateSessionId()
  console.log('🔄 新会话已创建:', currentSessionId)
  return currentSessionId
}

/**
 * 获取当前 session ID
 */
export const getSessionId = () => {
  return currentSessionId
}

/**
 * 调用 Main Flow（主工作流）
 * @param {string} message - 用户消息
 * @returns {Promise} Main Flow 的响应
 */
export const callMainFlow = async (message) => {
  try {
    const endpoint = `${BACKEND_CONFIG.baseURL}${BACKEND_CONFIG.endpoints.callMainFlow}`
    
    console.log('🚀 调用 Main Flow API:', endpoint)
    console.log('📝 Session ID:', currentSessionId)
    console.log('💬 Message:', message)

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        message: message,
        session_id: currentSessionId
      }),
      signal: AbortSignal.timeout(BACKEND_CONFIG.timeout)
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`❌ Main Flow API 请求失败: ${response.status} ${response.statusText}\n详情: ${errorText}`)
    }
    
    const data = await response.json()
    
    console.log('📦 Main Flow 响应:', data)
    
    // 处理不同的响应状态
    if (data.status === 'success') {
      return {
        success: true,
        message: data.result?.message || data.result,
        data: data.result,
        needsHumanFeedback: false
      }
    } else if (data.status === 'interrupt') {
      // Human-in-the-Loop 中断
      return {
        success: true,
        message: data.result?.message || '需要您的确认',
        data: data.result,
        needsHumanFeedback: true,
        showQuoteForm: data.result?.show_quote_form,
        quotationData: data.result?.quotation_data
      }
    } else if (data.status === 'fail') {
      throw new Error(data.result || 'Main Flow 执行失败')
    } else {
      throw new Error(`未知的响应状态: ${data.status}`)
    }
    
  } catch (error) {
    console.error('❌ Main Flow API 调用失败:', error)
    
    // 友好的错误提示
    if (error.name === 'AbortError') {
      throw new Error('请求超时，请检查后端服务是否正常运行')
    } else if (error.message.includes('Failed to fetch')) {
      throw new Error('无法连接到后端服务，请确保 FastAPI 服务已启动（http://localhost:8000）')
    } else {
      throw error
    }
  }
}

/**
 * 发送人工反馈（用于 Human-in-the-Loop）
 * @param {string} feedback - 用户反馈内容
 * @returns {Promise} 反馈响应
 */
export const sendHumanFeedback = async (feedback) => {
  try {
    const endpoint = `${BACKEND_CONFIG.baseURL}${BACKEND_CONFIG.endpoints.humanFeedback}`
    
    console.log('🤝 发送人工反馈:', feedback)

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        message: feedback,
        session_id: currentSessionId
      }),
      signal: AbortSignal.timeout(BACKEND_CONFIG.timeout)
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`❌ 人工反馈请求失败: ${response.status} ${response.statusText}\n详情: ${errorText}`)
    }
    
    const data = await response.json()
    
    console.log('📦 反馈响应:', data)
    
    return {
      success: true,
      message: data.result?.message || '反馈已接收',
      data: data.result
    }
    
  } catch (error) {
    console.error('❌ 人工反馈失败:', error)
    throw error
  }
}

/**
 * 健康检查
 * @returns {Promise<boolean>} 后端是否可用
 */
export const checkBackendHealth = async () => {
  try {
    const response = await fetch(`${BACKEND_CONFIG.baseURL}/docs`, {
      method: 'HEAD',
      signal: AbortSignal.timeout(5000)
    })
    return response.ok
  } catch (error) {
    console.warn('⚠️ 后端健康检查失败:', error)
    return false
  }
}

/**
 * 从对话中提取项目信息（用于报价单生成）
 * @param {Array} messages - 对话历史
 * @returns {Object} 提取的项目信息
 */
export const extractProjectInfoFromMessages = (messages) => {
  const userMessages = messages
    .filter(msg => msg.role === 'user')
    .map(msg => msg.content)
    .join(' ')

  // 简单的关键词匹配（Main Flow 会做更智能的提取）
  const info = {
    companyName: '',
    projectName: '',
    budget: ''
  }

  // 提取公司名称
  const companyMatch = userMessages.match(/([^\n]+(?:公司|工程|建筑))/i)
  if (companyMatch) {
    info.companyName = companyMatch[1].trim()
  }

  // 提取项目名称
  const projectMatch = userMessages.match(/([^\n]+(?:项目|工程|计算))/i)
  if (projectMatch) {
    info.projectName = projectMatch[1].trim()
  }

  // 提取预算
  const budgetMatch = userMessages.match(/(\d+)\s*(?:MOP|澳门元|元)/i)
  if (budgetMatch) {
    info.budget = budgetMatch[1]
  }

  return info
}

export default {
  callMainFlow,
  sendHumanFeedback,
  resetSession,
  getSessionId,
  checkBackendHealth,
  extractProjectInfoFromMessages
}

