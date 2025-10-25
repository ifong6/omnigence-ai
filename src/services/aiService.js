/**
 * AI模型API服务
 * 用于与AI模型进行对话和生成报价单数据
 */

import { apiConfig } from '../config'

// 使用统一配置
const API_CONFIG = apiConfig.ai

/**
 * 发送消息到AI模型
 * @param {Array} messages - 对话历史
 * @returns {Promise} AI的回复
 */
export const sendMessageToAI = async (messages) => {
  try {
    // 验证API配置
    if (!API_CONFIG.apiKey) {
      throw new Error('❌ AI API Key 未配置！请在 src/config/api.config.js 中配置 API_KEY')
    }
    
    if (!API_CONFIG.endpoint) {
      throw new Error('❌ AI API Endpoint 未配置！请在 src/config/api.config.js 中配置 API_ENDPOINT')
    }

    console.log('🚀 发送API请求到:', API_CONFIG.endpoint)
    console.log('📝 使用模型:', API_CONFIG.model)

    // 实际的API调用
    const response = await fetch(API_CONFIG.endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_CONFIG.apiKey}`
      },
      body: JSON.stringify({
        model: API_CONFIG.model,
        messages: messages,
        temperature: API_CONFIG.temperature,
        max_tokens: API_CONFIG.maxTokens,
      }),
      signal: AbortSignal.timeout(API_CONFIG.timeout)
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`❌ API请求失败: ${response.status} ${response.statusText}\n详情: ${errorText}`)
    }
    
    const data = await response.json()
    
    // 打印完整的返回数据，用于调试
    console.log('📦 API原始返回数据:', JSON.stringify(data, null, 2))
    
    // 尝试不同的API格式解析
    
    // 格式1: OpenAI格式
    if (data.choices && data.choices[0] && data.choices[0].message) {
      console.log('✅ 检测到OpenAI格式')
      return data.choices[0].message
    }
    
    // 格式2: Claude格式
    if (data.content && Array.isArray(data.content)) {
      console.log('✅ 检测到Claude格式')
      return {
        role: 'assistant',
        content: data.content.map(item => item.text).join('\n')
      }
    }
    
    // 格式3: 简单的直接返回
    if (data.message) {
      console.log('✅ 检测到简单格式')
      return data.message
    }
    
    // 格式4: 直接返回content字段
    if (data.content && typeof data.content === 'string') {
      console.log('✅ 检测到直接content格式')
      return {
        role: 'assistant',
        content: data.content
      }
    }
    
    // 如果都不匹配，抛出错误并显示返回数据
    console.error('❌ 未知的API返回格式:', data)
    throw new Error(`❌ API返回数据格式错误。返回数据: ${JSON.stringify(data)}`)
  } catch (error) {
    console.error('❌ AI API调用失败:', error.message)
    throw error
  }
}

/**
 * 请求AI生成报价单数据
 * @param {Object} projectInfo - 项目信息
 * @param {Array} conversationHistory - 对话历史（可选）
 * @returns {Promise} 报价单JSON数据
 */
export const generateQuotation = async (projectInfo, conversationHistory = []) => {
  try {
    console.log('🚀 开始生成报价单，项目信息:', projectInfo)

    // 构建Prompt，要求AI返回JSON格式
    const systemPrompt = `你是一个专业的工程报价单助手。根据用户提供的信息，生成规范的工程报价单数据。

      要求：
      1. 必须返回纯JSON格式，不要包含任何markdown标记或额外说明
      2. 金额必须是数字字符串，不包含货币符号
      3. 项目明细必须详细、专业
      4. 根据工程类型合理估算单价
      5. ⚠️ 重要：报价单的totalAmount（总金额）必须严格小于或等于用户提供的预算
      6. 合理拆分子项目，确保各子项目的totalPrice之和等于totalAmount
      7. 如果预算不足，减少子项目数量或降低单价，但总价绝对不能超过预算

      JSON格式要求：
      {
        "quotationNumber": "报价单编号（格式：INV-XX-XXXX）",
        "date": "日期（格式：YYYY/MM/DD）",
        "companyName": "客户公司名称",
        "phoneNumber": "联系电话",
        "address": "公司地址",
        "projectName": "项目名称",
        "items": [
          {
            "sequence": 序号,
            "itemName": "子项目名称",
            "quantity": 数量,
            "unit": "单位（如：Lot、份、项、m²等）",
            "unitPrice": "单价（纯数字字符串）",
            "totalPrice": "小计（纯数字字符串）"
          }
        ],
        "totalAmount": "总金额（纯数字字符串）",
        "currency": "MOP"
      }`

    const userPrompt = `根据以下信息生成报价单：

    客户公司：${projectInfo.companyName || projectInfo.clientName || '待补充'}
    项目名称：${projectInfo.projectName || '待补充'}
    预算上限：${projectInfo.budget || '待评估'} 澳门元

    ${conversationHistory.length > 0 ? '\n对话历史：\n' + conversationHistory.map(msg => `${msg.role}: ${msg.content}`).join('\n') : ''}

    ⚠️ 重要约束：
    1. totalAmount（总金额）必须 ≤ ${projectInfo.budget || 0}
    2. 所有子项目的totalPrice相加必须等于totalAmount
    3. 如果预算${projectInfo.budget}不够，请合理调整子项目数量或单价

    请根据项目类型，拆分成合理的子项目，并给出专业的报价。直接返回JSON，不要有任何其他内容。`

    // 调用AI API
    const messages = [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt }
    ]

    const aiResponse = await sendMessageToAI(messages)
    
    console.log('📥 AI原始响应:', aiResponse.content)

    // 解析JSON
    let quotationData
    try {
      // 尝试提取JSON（处理可能包含markdown的情况）
      let jsonText = aiResponse.content.trim()
      
      // 移除可能的markdown代码块标记
      jsonText = jsonText.replace(/```json\s*/g, '')
      jsonText = jsonText.replace(/```\s*/g, '')
      
      quotationData = JSON.parse(jsonText)
      console.log('✅ JSON解析成功')
    } catch (parseError) {
      console.error('❌ JSON解析失败:', parseError)
      throw new Error('AI返回的数据格式不正确，无法解析JSON')
    }

    // 验证必需字段
    const requiredFields = ['companyName', 'projectName', 'items', 'totalAmount']
    const missingFields = requiredFields.filter(field => !quotationData[field])
    
    if (missingFields.length > 0) {
      throw new Error(`报价单数据缺少必需字段: ${missingFields.join(', ')}`)
    }

    // 验证items格式
    if (!Array.isArray(quotationData.items) || quotationData.items.length === 0) {
      throw new Error('报价单必须包含至少一个子项目')
    }

    // ⚠️ 验证预算约束
    const budget = parseFloat(projectInfo.budget) || 0
    const totalAmount = parseFloat(quotationData.totalAmount) || 0
    
    if (budget > 0 && totalAmount > budget) {
      console.error(`❌ 预算超支！总价${totalAmount} > 预算${budget}`)
      throw new Error(`❌ 报价单总价（${totalAmount}）超过预算上限（${budget}）！\n请AI重新生成或手动调整金额。`)
    }
    
    // 验证子项目金额之和
    const itemsSum = quotationData.items.reduce((sum, item) => {
      return sum + parseFloat(item.totalPrice || 0)
    }, 0)
    
    if (Math.abs(itemsSum - totalAmount) > 0.01) {
      console.warn(`⚠️ 子项目金额之和(${itemsSum})与总金额(${totalAmount})不匹配`)
    }
    
    console.log(`✅ 预算验证通过：总价${totalAmount} ≤ 预算${budget}`)

    // 补充默认值
    const finalData = {
      quotationNumber: quotationData.quotationNumber || `INV-${Date.now().toString().slice(-6)}`,
      quotationVersion: '1.0',  // 初始版本号，QuotationSheet会根据情况自动递增
      currentDate: quotationData.date || new Date().toLocaleDateString('zh-CN'),
      clientName: quotationData.companyName,
      phoneNumber: quotationData.phoneNumber || '',
      address: quotationData.address || '',
      projectName: quotationData.projectName,
      items: quotationData.items.map((item, index) => ({
        sequence: item.sequence || index + 1,
        project: item.itemName,
        quantity: item.quantity || 1,
        unit: item.unit || 'Lot',
        unitPrice: `MOP $ ${parseFloat(item.unitPrice || 0).toFixed(2)}`,
        totalPrice: `MOP $ ${parseFloat(item.totalPrice || 0).toFixed(2)}`
      })),
      totalAmount: `MOP $ ${parseFloat(quotationData.totalAmount || 0).toFixed(2)}`,
      currency: quotationData.currency || 'MOP',
      notes: [
        '1.本报价单包括以下所有费用除额外工作',
        '2.本报价单按现场实际作为开设数量',
        '3.本工程不包括税费',
        '4.若因客情用申报后如果得到回答'
      ]
    }

    console.log('✅ 报价单生成成功:', finalData)
    return finalData

  } catch (error) {
    console.error('❌ 生成报价单失败:', error.message)
    throw error
  }
}

/**
 * 从对话中提取项目信息
 * @param {Array} messages - 对话历史
 * @returns {Object} 提取的项目信息
 */
export const extractProjectInfo = (messages) => {
  // TODO: 使用AI或正则表达式从对话中提取关键信息
  // 这里可以使用AI来理解对话内容并提取结构化数据
  
  const info = {
    clientName: '',
    //phoneNumber: '',
    //address: '',
    projectName: '',
    budget: ''
  }
  
  // 简单的关键词匹配示例
  messages.forEach(msg => {
    if (msg.role === 'user') {
      const content = msg.content.toLowerCase()
      // 这里添加更复杂的提取逻辑
    }
  })
  
  return info
}

