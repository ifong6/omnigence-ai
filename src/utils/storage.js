/**
 * 本地存储工具函数
 * 用于保存和检索报价单数据
 */

const STORAGE_KEY = 'quotations'

/**
 * 保存报价单到本地存储
 * @param {Object} quotation - 报价单数据
 * @returns {boolean} 是否保存成功
 */
export const saveQuotation = (quotation) => {
  try {
    const quotations = getQuotations()
    const newQuotation = {
      ...quotation,
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    quotations.push(newQuotation)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(quotations))
    return true
  } catch (error) {
    console.error('保存报价单失败:', error)
    return false
  }
}

/**
 * 获取所有报价单
 * @returns {Array} 报价单列表
 */
export const getQuotations = () => {
  try {
    const data = localStorage.getItem(STORAGE_KEY)
    return data ? JSON.parse(data) : []
  } catch (error) {
    console.error('读取报价单失败:', error)
    return []
  }
}

/**
 * 根据ID获取报价单
 * @param {string} id - 报价单ID
 * @returns {Object|null} 报价单数据
 */
export const getQuotationById = (id) => {
  try {
    const quotations = getQuotations()
    return quotations.find(q => q.id === id) || null
  } catch (error) {
    console.error('获取报价单失败:', error)
    return null
  }
}

/**
 * 更新报价单
 * @param {string} id - 报价单ID
 * @param {Object} updates - 更新的数据
 * @returns {boolean} 是否更新成功
 */
export const updateQuotation = (id, updates) => {
  try {
    const quotations = getQuotations()
    const index = quotations.findIndex(q => q.id === id)
    if (index !== -1) {
      quotations[index] = {
        ...quotations[index],
        ...updates,
        updatedAt: new Date().toISOString()
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(quotations))
      return true
    }
    return false
  } catch (error) {
    console.error('更新报价单失败:', error)
    return false
  }
}

/**
 * 删除报价单
 * @param {string} id - 报价单ID
 * @returns {boolean} 是否删除成功
 */
export const deleteQuotation = (id) => {
  try {
    const quotations = getQuotations()
    const filtered = quotations.filter(q => q.id !== id)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered))
    return true
  } catch (error) {
    console.error('删除报价单失败:', error)
    return false
  }
}

/**
 * 搜索报价单
 * @param {string} searchTerm - 搜索关键词
 * @returns {Array} 匹配的报价单列表
 */
export const searchQuotations = (searchTerm) => {
  try {
    const quotations = getQuotations()
    const term = searchTerm.toLowerCase()
    return quotations.filter(q => 
      q.quotationNumber?.toLowerCase().includes(term) ||
      q.clientName?.toLowerCase().includes(term) ||
      q.projectName?.toLowerCase().includes(term)
    )
  } catch (error) {
    console.error('搜索报价单失败:', error)
    return []
  }
}

