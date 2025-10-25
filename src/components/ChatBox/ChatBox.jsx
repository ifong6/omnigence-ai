import { useState, useRef, useEffect } from 'react'
import { sendMessageToAI, generateQuotation } from '../../services/aiService'
import { HiPaperAirplane, HiMicrophone, HiPaperClip } from 'react-icons/hi'  // 导入图标

// System Prompt：定义AI助手的角色和行为
const SYSTEM_PROMPT = {
  role: 'system',
  content: `你是一个专业的工程报价单助手，名字是"港珀助手"。你的任务是：

  1. 友好地与客户对话，收集必要的项目信息
  2. 需要收集的信息：
    - 客户公司名称（必需）
    - 项目名称（必需）
    - 项目预算范围（必需）
  3. 一次只问1-2个问题，不要一次性问太多
  4. 当收集到公司名称、项目名称和预算后，告诉用户"信息已收集完成，正在为您生成报价单..."
  5. 使用友好、专业的语气
  6. 用中文回复

  记住：你的目标是帮助客户生成专业的工程报价单。`
}

const ChatBox = ({ onQuotationGenerated }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: '您好！我是港珀工程顾问的AI助手。我可以帮您生成专业的工程报价单。\n\n请问您的项目是什么？',
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!inputValue.trim()) return

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputValue,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      // 构建对话历史（包含System Prompt）
      const conversationHistory = [
        SYSTEM_PROMPT,
        ...messages.map(msg => ({ role: msg.role, content: msg.content })),
        { role: 'user', content: userMessage.content }
      ]

      console.log('📤 发送对话历史到AI:', conversationHistory)

      // ✅ 调用真实的AI API
      const aiMessage = await sendMessageToAI(conversationHistory)
      
      console.log('📥 收到AI回复:', aiMessage)

      const aiResponse = {
        id: Date.now() + 1,
        role: 'assistant',
        content: aiMessage.content,
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      }
      
      setMessages(prev => [...prev, aiResponse])

      // 检查是否提到"信息已收集完成"或"生成报价单"
      if (aiMessage.content.includes('信息已收集完成') || 
          aiMessage.content.includes('生成报价单')) {
        console.log('🎯 检测到需要生成报价单，开始提取信息...')
        
        // 尝试从对话历史中提取项目信息
        await handleGenerateQuotation([...messages, userMessage, aiResponse])
      }

    } catch (error) {
      console.error('❌ AI调用失败:', error)
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `❌ 抱歉，发生错误：${error.message}\n\n请检查：\n1. API配置是否正确\n2. 网络连接是否正常\n3. API密钥是否有效`,
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  // 生成报价单
  const handleGenerateQuotation = async (conversationMessages) => {
    try {
      console.log('🚀 开始生成报价单...')
      
      // 从对话中提取信息（简单版本）
      const conversationText = conversationMessages
        .filter(msg => msg.role === 'user')
        .map(msg => msg.content)
        .join(' ')
      
      // 提取基本信息
      const projectInfo = {
        companyName: extractInfo(conversationText, ['公司', '客户']),
        projectName: extractInfo(conversationText, ['项目']),
        budget: extractInfo(conversationText, ['预算', '万', '元'])
      }
      
      console.log('📝 提取的项目信息:', projectInfo)
      
      // 调用AI生成报价单
      const quotationData = await generateQuotation(projectInfo, conversationMessages)
      
      console.log('✅ 报价单生成成功:', quotationData)
      
      // 通知父组件显示报价单
      if (onQuotationGenerated) {
        onQuotationGenerated(quotationData)
      }
      
      // 添加成功消息
      const successMessage = {
        id: Date.now() + 2,
        role: 'assistant',
        content: '✅ 报价单已生成！请查看右侧的报价单预览。您可以直接编辑内容，然后点击"Download PDF"导出。',
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      }
      
      setMessages(prev => [...prev, successMessage])
      
    } catch (error) {
      console.error('❌ 生成报价单失败:', error)
      
      const errorMessage = {
        id: Date.now() + 2,
        role: 'assistant',
        content: `❌ 生成报价单失败：${error.message}\n\n请重新提供信息，或检查API配置。`,
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      }
      
      setMessages(prev => [...prev, errorMessage])
    }
  }

  // 简单的信息提取函数
  const extractInfo = (text, keywords) => {
    for (const keyword of keywords) {
      const regex = new RegExp(`${keyword}[：:是]?\\s*([^，。！？\\s]+)`, 'i')
      const match = text.match(regex)
      if (match) {
        return match[1]
      }
    }
    return ''
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gray-900 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">X</span>
          </div>
          <h1 className="text-lg font-medium">XX公司的XX项目咨询</h1>
        </div>
        <button className="text-gray-500 hover:text-gray-700">
          <span className="text-sm">Help</span> ❓
        </button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-[70%] ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
              <div className="flex items-start space-x-2">
                {message.role === 'assistant' && (
                  <div className="w-8 h-8 bg-gray-800 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-sm">🤖</span>
                  </div>
                )}
                <div className="flex-1">
                  <div className="text-xs text-gray-500 mb-1">{message.timestamp}</div>
                  <div
                    className={`p-3 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {message.content}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-center space-x-2 p-3 bg-gray-100 rounded-lg">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="  mb-10 p-4">
        {/* New dialog 按钮 */}
        <div className="mt-2 flex justify-end">
          <button className="py-2 text-sm text-black hover:text-gray-700 flex items-center">
            <span className="mr-1">✨</span>
            New dialog
          </button>
        </div>
        {/* 输入框容器 - 相对定位 */}
        <div className="relative">
          {/* 左侧附件图标 - 在输入框内 */}
          <button 
            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 z-10" 
            title="添加附件"
          >
            <HiPaperClip className="text-lg" />
          </button>
          
          {/* 输入框 - 左侧和右侧都留出空间 */}
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Send me prompt and request ai chat"
            className="w-full pl-10 pr-20 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          
          {/* 右侧图标组 - 在输入框内 */}
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
            {/* 语音图标 */}
            <button 
              className="text-gray-400 hover:text-gray-600 p-1" 
              title="语音输入"
            >
              <HiMicrophone className="text-lg" />
            </button>
            
            {/* 发送按钮 */}
            <button
              onClick={handleSend}
              disabled={isLoading}
              className="text-gray-400 hover:text-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-110 p-1"
              title="发送消息"
            >
              <HiPaperAirplane className="text-lg transform rotate-90" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatBox

