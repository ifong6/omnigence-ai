/**
 * PDF导出工具函数
 */

/**
 * 使用浏览器打印功能导出PDF
 * 这个方法会触发浏览器的打印对话框
 */
export const exportToPDF = () => {
  window.print()
}

/**
 * 配置打印样式
 * 只打印报价单部分，隐藏其他内容
 */
export const configurePrintStyles = () => {
  // 检查是否已经添加过样式，避免重复
  if (document.getElementById('quotation-print-styles')) {
    return
  }

  const style = document.createElement('style')
  style.id = 'quotation-print-styles'
  style.textContent = `
    @media print {
      /* ========== 页面设置 ========== */
      @page {
        margin: 1cm;
        size: A4 portrait;
      }
      
      /* ========== 隐藏不需要打印的部分 ========== */
      
      /* 隐藏整个左侧聊天区域 */
      body > #root > div > div:first-child {
        display: none !important;
      }
      
      /* 隐藏右上角搜索栏 */
      body > #root > div > div:last-child > div:first-child {
        display: none !important;
      }
      
      /* 隐藏Download PDF按钮 */
      .print\\:hidden {
        display: none !important;
      }
      
      /* ========== 报价单容器样式调整 ========== */
      
      /* 确保报价单区域占满整个打印页面 */
      body > #root > div > div:last-child > div:last-child {
        padding: 0 !important;
        margin: 0 !important;
        overflow: visible !important;
      }
      
      /* 报价单本身 */
      body {
        margin: 0;
        padding: 0;
        background: white !important;
      }
      
      /* ========== 保持报价单原有样式 ========== */
      
      /* 移除不必要的阴影 */
      .shadow-lg, .shadow-md, .shadow-sm {
        box-shadow: none !important;
      }
      
      /* 保持边框 */
      .border, .border-b, .border-t, .border-l, .border-r {
        border-color: #000 !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }
      
      /* 保持背景色 */
      .bg-gray-100, .bg-gray-50 {
        background-color: #f3f4f6 !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }
      
      .bg-white {
        background-color: white !important;
      }
      
      /* 保持文字颜色 */
      .text-gray-600, .text-gray-700, .text-gray-800 {
        color: #374151 !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }
      
      .text-blue-600 {
        color: #2563eb !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }
      
      /* ========== 表格样式 ========== */
      
      /* 确保表格不被分页 */
      table {
        page-break-inside: avoid;
        border-collapse: collapse;
      }
      
      /* 表格边框 */
      table, th, td {
        border: 1px solid #000 !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }
      
      /* 表头背景 */
      thead {
        background-color: #f3f4f6 !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }
      
      /* ========== 输入框样式调整 ========== */
      
      /* 打印时输入框显示为普通文本样式 */
      input {
        border: 1px solid #d1d5db !important;
        background: white !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }
      
      /* ========== 避免内容被分页 ========== */
      
      .print\\:avoid-break {
        page-break-inside: avoid;
      }
      
      /* 签名区域不分页 */
      .bg-gray-100:last-child {
        page-break-inside: avoid;
      }
      
      /* ========== 确保所有内容可见 ========== */
      
      * {
        overflow: visible !important;
      }
    }
  `
  document.head.appendChild(style)
}

// 在页面加载时自动配置打印样式
if (typeof window !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', configurePrintStyles)
  } else {
    configurePrintStyles()
  }
}

/**
 * 使用html2pdf库导出PDF
 * @param {string} elementId - 要导出的元素ID
 * @param {string} filename - PDF文件名
 */
export const exportWithLibrary = async (elementId, filename = 'quotation.pdf') => {
  // 用于存储隐藏状态
  let hiddenElements = []
  let leftPanel = null
  let leftPanelDisplay = ''
  
  try {
    console.log('🚀 开始生成PDF...')
    
    // 获取要导出的元素
    const element = document.getElementById(elementId)
    
    if (!element) {
      throw new Error(`找不到ID为 ${elementId} 的元素`)
    }
    
    console.log('✅ 找到报价单元素:', element)
    
    // 隐藏不需要打印的元素
    const hideElements = document.querySelectorAll('.hide-in-pdf')
    hideElements.forEach(el => {
      if (el.style.display !== 'none') {
        hiddenElements.push({ element: el, display: el.style.display })
        el.style.display = 'none'
      }
    })
    
    // 隐藏左侧聊天区域
    leftPanel = document.querySelector('.flex.h-screen > div:first-child')
    if (leftPanel && leftPanel.style.display !== 'none') {
      leftPanelDisplay = leftPanel.style.display
      leftPanel.style.display = 'none'
    }
    
    // 等待DOM更新
    await new Promise(resolve => setTimeout(resolve, 200))
    
    // 动态导入 html2canvas 和 jsPDF
    const html2canvas = (await import('html2canvas')).default
    const { jsPDF } = await import('jspdf')
    
    console.log('📦 成功加载 html2canvas 和 jsPDF')
    
    // 注入临时样式来强制使用传统颜色格式
    const tempStyle = document.createElement('style')
    tempStyle.id = 'pdf-export-color-fix'
    tempStyle.textContent = `
      * {
        color: rgb(17, 24, 39) !important; /* gray-900 */
        background-color: rgb(255, 255, 255) !important;
        border-color: rgb(229, 231, 235) !important; /* gray-200 */
      }
      .bg-gray-100 {
        background-color: rgb(243, 244, 246) !important; /* gray-100 */
      }
      .bg-gray-50 {
        background-color: rgb(249, 250, 251) !important; /* gray-50 */
      }
      .text-gray-600 {
        color: rgb(75, 85, 99) !important; /* gray-600 */
      }
      .text-gray-700 {
        color: rgb(55, 65, 81) !important; /* gray-700 */
      }
      .text-gray-800 {
        color: rgb(31, 41, 55) !important; /* gray-800 */
      }
      .border-gray-300 {
        border-color: rgb(209, 213, 219) !important; /* gray-300 */
      }
      .border-gray-800 {
        border-color: rgb(31, 41, 55) !important; /* gray-800 */
      }
    `
    document.head.appendChild(tempStyle)
    
    // 等待样式应用
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // html2canvas 配置 - 简化为避免 oklch 问题
    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
      logging: true,
      backgroundColor: '#ffffff',
      removeContainer: false,
      allowTaint: true,
      imageTimeout: 15000,
      ignoreElements: (el) => {
        // 忽略任何可能导致问题的元素
        return false
      }
    })
    
    // 移除临时样式
    document.getElementById('pdf-export-color-fix')?.remove()
    
    console.log('📸 Canvas 生成完成')
    
    // 创建 PDF
    const imgData = canvas.toDataURL('image/png', 0.95)
    const pdf = new jsPDF('portrait', 'mm', 'a4')
    
    // A4 尺寸 (mm)
    const a4Width = 210
    const a4Height = 297
    const margin = 10
    
    // 计算图片尺寸以适配 A4
    const canvasWidth = canvas.width
    const canvasHeight = canvas.height
    const imgWidth = a4Width - (margin * 2)
    const imgHeight = (canvasHeight * imgWidth) / canvasWidth
    
    // 检查是否需要分页
    let heightLeft = imgHeight
    let position = 0
    
    // 添加第一页
    pdf.addImage(imgData, 'PNG', margin, margin + position, imgWidth, imgHeight)
    heightLeft -= a4Height - (margin * 2)
    
    // 如果需要，添加更多页
    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', margin, position, imgWidth, imgHeight)
      heightLeft -= a4Height - (margin * 2)
    }
    
    // 保存PDF
    pdf.save(filename)
    
    console.log('✅ PDF生成成功！')
    return true
    
  } catch (error) {
    console.error('❌ PDF导出失败:', error)
    alert(`PDF导出失败: ${error.message}\n\n请查看浏览器控制台获取更多信息。`)
    return false
  } finally {
    // 移除临时样式（如果还存在）
    document.getElementById('pdf-export-color-fix')?.remove()
    
    // 恢复隐藏的元素
    if (hiddenElements.length > 0) {
      hiddenElements.forEach(({ element, display }) => {
        element.style.display = display || ''
      })
    }
    
    // 恢复左侧聊天区域
    if (leftPanel) {
      leftPanel.style.display = leftPanelDisplay
    }
  }
}

/**
 * 使用浏览器原生打印功能导出PDF（作为备选方案）
 */
export const exportWithBrowserPrint = async (elementId, filename = 'quotation.pdf') => {
  try {
    console.log('🖨️ 使用浏览器打印功能导出PDF...')
    
    // 隐藏不需要打印的元素
    const hideElements = document.querySelectorAll('.hide-in-pdf')
    const hiddenStates = []
    hideElements.forEach(el => {
      hiddenStates.push({ element: el, display: el.style.display })
      el.style.display = 'none'
    })
    
    // 隐藏左侧面板
    const leftPanel = document.querySelector('.flex.h-screen > div:first-child')
    const leftPanelDisplay = leftPanel ? leftPanel.style.display : ''
    if (leftPanel) {
      leftPanel.style.display = 'none'
    }
    
    // 等待DOM更新
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // 触发打印
    window.print()
    
    // 恢复元素
    hideElements.forEach((el, index) => {
      el.style.display = hiddenStates[index].display || ''
    })
    if (leftPanel) {
      leftPanel.style.display = leftPanelDisplay
    }
    
    console.log('✅ 浏览器打印已触发，请选择"保存为PDF"')
    return true
    
  } catch (error) {
    console.error('❌ 浏览器打印失败:', error)
    return false
  }
}

/**
 * 导出报价单为PDF（推荐使用此函数）
 * @param {Object} quotationData - 报价单数据（用于生成文件名）
 */
export const exportQuotationPDF = async (quotationData) => {
  try {
    // 生成文件名：报价单编号_客户名称_日期.pdf
    const filename = `${quotationData.quotationNumber || 'quotation'}_${quotationData.clientName || 'client'}_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')}.pdf`
    
    console.log('📝 PDF文件名:', filename)
    
    // 导出ID为quotation-sheet的元素
    const success = await exportWithLibrary('quotation-sheet', filename)
    
    return success
  } catch (error) {
    console.error('❌ 导出报价单PDF失败:', error)
    return false
  }
}

