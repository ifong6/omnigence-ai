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
  let originalStyle = {}
  let element = null
  let inputReplacements = []
  
  try {
    console.log('🚀 开始生成PDF...')
    
    // 获取要导出的元素
    element = document.getElementById(elementId)
    
    if (!element) {
      throw new Error(`找不到ID为 ${elementId} 的元素`)
    }
    
    console.log('✅ 找到报价单元素:', element)
    
    // 保存原始样式
    originalStyle = {
      position: element.style.position,
      left: element.style.left,
      top: element.style.top,
      width: element.style.width,
      maxWidth: element.style.maxWidth,
      minHeight: element.style.minHeight,
      margin: element.style.margin,
      padding: element.style.padding,
      transform: element.style.transform,
      zIndex: element.style.zIndex,
      background: element.style.background,
      boxSizing: element.style.boxSizing,
      fontSize: element.style.fontSize
    }
    
    // 让报价单元素独立显示，占据全屏
    // A4 宽度 210mm ≈ 794px (at 96 DPI)
    element.style.position = 'fixed'
    element.style.left = '0'
    element.style.top = '0'
    element.style.width = '210mm'  // 使用 mm 单位更精确
    element.style.maxWidth = '210mm'
    element.style.minHeight = '297mm'  // A4 高度
    element.style.margin = '0'
    element.style.padding = '12mm 15mm'  // 上下12mm，左右15mm页边距
    element.style.transform = 'none'
    element.style.zIndex = '9999'
    element.style.background = 'white'
    element.style.boxSizing = 'border-box'
    element.style.fontSize = '11pt'  // 设置基础字体大小
    element.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    
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
    
    // 隐藏下载按钮所在的容器
    const downloadButtonContainer = document.querySelector('.h-18')
    if (downloadButtonContainer) {
      downloadButtonContainer.style.display = 'none'
    }
    
    // 等待DOM更新
    await new Promise(resolve => setTimeout(resolve, 300))
    
    // 将表格中的 input 转换为纯文本以避免错位
    const inputs = element.querySelectorAll('input')
    
    inputs.forEach(input => {
      const div = document.createElement('div')
      const value = input.value || input.placeholder || ''
      
      // 使用 innerHTML 而非 textContent 以支持特殊字符
      // 但需要转义 HTML 以防注入
      const escapedValue = value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;')
      
      div.innerHTML = escapedValue
      
      // 复制计算后的样式
      const computedStyle = window.getComputedStyle(input)
      const parentTd = input.closest('td')
      
      // 设置基本样式
      div.style.width = '100%'
      div.style.minHeight = computedStyle.height
      div.style.lineHeight = '1.5'
      div.style.padding = '0'
      div.style.margin = '0'
      div.style.fontSize = '10pt'
      div.style.fontFamily = computedStyle.fontFamily
      div.style.fontWeight = computedStyle.fontWeight
      div.style.color = computedStyle.color
      div.style.backgroundColor = 'transparent'
      div.style.border = 'none'
      div.style.boxSizing = 'border-box'
      div.style.overflow = 'visible'
      div.style.wordWrap = 'break-word'
      div.style.whiteSpace = 'normal'
      div.style.display = 'block'
      
      // 根据列索引设置对齐方式
      if (parentTd) {
        const colIndex = parentTd.cellIndex
        
        if (colIndex === 0) {
          // 序号 - 居中
          div.style.textAlign = 'center'
        } else if (colIndex === 1) {
          // 项目 - 左对齐
          div.style.textAlign = 'left'
        } else if (colIndex === 2) {
          // 数量 - 右对齐
          div.style.textAlign = 'right'
        } else if (colIndex === 3) {
          // 单位 - 居中
          div.style.textAlign = 'center'
        } else if (colIndex === 4) {
          // 单价 - 右对齐
          div.style.textAlign = 'right'
        } else if (colIndex === 5) {
          // 价钱总计 - 右对齐
          div.style.textAlign = 'right'
        } else {
          div.style.textAlign = 'left'
        }
      }
      
      // 保存原始信息
      inputReplacements.push({
        input: input,
        parent: input.parentNode,
        nextSibling: input.nextSibling,
        replacement: div
      })
      
      input.parentNode.replaceChild(div, input)
    })
    
    console.log(`🔄 已替换 ${inputs.length} 个 input 元素`)
    
    // 等待替换完成并确保DOM稳定
    await new Promise(resolve => setTimeout(resolve, 300))
    
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
      
      /* 全局字体优化 */
      #quotation-sheet {
        font-size: 11pt !important;
        line-height: 1.5 !important;
        color: rgb(17, 24, 39) !important;
      }
      
      /* 顶部公司信息区域优化 */
      #quotation-sheet > div:first-child {
        padding: 8px 0 !important;
        margin-bottom: 10px !important;
      }
      
      #quotation-sheet > div:first-child .flex {
        align-items: flex-start !important;
        justify-content: space-between !important;
        width: 100% !important;
      }
      
      /* 公司名称区域（左侧） */
      #quotation-sheet > div:first-child .text-xs:first-child {
        font-size: 9pt !important;
        line-height: 1.5 !important;
        text-align: left !important;
      }
      
      #quotation-sheet > div:first-child .text-xs:first-child .font-bold {
        font-weight: 600 !important;
        font-size: 10pt !important;
        margin-bottom: 2px !important;
      }
      
      #quotation-sheet > div:first-child .text-xs:first-child .text-gray-500 {
        font-size: 8.5pt !important;
        color: rgb(107, 114, 128) !important;
        margin-bottom: 4px !important;
      }
      
      /* 业务类型标签 */
      #quotation-sheet > div:first-child .border.rounded-2xl {
        padding: 3px 10px !important;
        font-size: 7.5pt !important;
        border-color: rgb(31, 41, 55) !important;
        border-width: 1px !important;
        display: inline-block !important;
        margin-top: 3px !important;
      }
      
      /* 编号日期区域（右侧） */
      #quotation-sheet > div:first-child .text-left {
        font-size: 9pt !important;
        line-height: 1.7 !important;
        text-align: right !important;
      }
      
      #quotation-sheet > div:first-child .text-left .font-bold {
        font-weight: 600 !important;
        font-size: 9pt !important;
        margin-bottom: 2px !important;
        white-space: nowrap !important;
      }
      
      /* 报价单标题区域优化 */
      #quotation-sheet > div:nth-child(2) {
        margin: 15px 0 12px 0 !important;
        padding: 0 !important;
      }
      
      #quotation-sheet h1 {
        font-size: 22pt !important;
        font-weight: 700 !important;
        margin: 0 0 6px 0 !important;
        text-align: center !important;
        letter-spacing: 1px !important;
      }
      
      #quotation-sheet h1 + p {
        font-size: 8pt !important;
        color: rgb(75, 85, 99) !important;
        margin: 0 !important;
        text-align: center !important;
      }
      
      /* 客户信息区域优化 */
      #quotation-sheet > div:nth-child(3) {
        padding: 12px 0 !important;
        margin-top: 8px !important;
      }
      
      /* 客户信息行容器 */
      #quotation-sheet > div:nth-child(3) > div {
        display: flex !important;
        align-items: center !important;
        margin-bottom: 8px !important;
      }
      
      /* 客户信息标签 - 固定宽度确保对齐 */
      #quotation-sheet > div:nth-child(3) label,
      #quotation-sheet > div:nth-child(3) .bg-gray-100 {
        background-color: rgb(243, 244, 246) !important;
        padding: 7px 12px !important;
        font-weight: 600 !important;
        font-size: 10pt !important;
        width: 90px !important;
        min-width: 90px !important;
        max-width: 90px !important;
        text-align: center !important;
        border-radius: 4px 0 0 4px !important;
        flex-shrink: 0 !important;
        display: inline-block !important;
        box-sizing: border-box !important;
      }
      
      /* 客户信息输入框（会被替换成div） */
      #quotation-sheet > div:nth-child(3) input {
        font-size: 10pt !important;
        padding: 7px 12px !important;
        line-height: 1.4 !important;
        border-radius: 0 4px 4px 0 !important;
        flex: 1 !important;
      }
      
      /* 替换后的div元素 */
      #quotation-sheet > div:nth-child(3) > div > div {
        font-size: 10pt !important;
        padding: 7px 12px !important;
        line-height: 1.4 !important;
      }
      
      /* 网格布局的两列（电话和地址） */
      #quotation-sheet > div:nth-child(3) .grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 12px !important;
      }
      
      /* 备注区域优化 */
      #quotation-sheet .text-sm {
        font-size: 9pt !important;
        line-height: 1.6 !important;
      }
      
      /* 签名区域优化 */
      #quotation-sheet > div:last-child {
        padding: 12px 0 !important;
        margin-top: 15px !important;
      }
      
      #quotation-sheet > div:last-child .text-sm {
        font-size: 9pt !important;
      }
      
      #quotation-sheet > div:last-child .font-bold {
        font-weight: 600 !important;
      }
      
      /* 表格布局优化 */
      table {
        table-layout: fixed !important;
        width: 100% !important;
        border-collapse: collapse !important;
        font-size: 10.5pt !important;
      }
      
      /* 表格列宽优化 - 精确分配 */
      table thead tr th:nth-child(1) { 
        width: 7% !important;
        min-width: 40px !important;
      }   /* 序号 */
      table thead tr th:nth-child(2) { 
        width: 28% !important;
        min-width: 120px !important;
      }  /* 项目 */
      table thead tr th:nth-child(3) { 
        width: 10% !important;
        min-width: 60px !important;
      }  /* 数量 */
      table thead tr th:nth-child(4) { 
        width: 10% !important;
        min-width: 50px !important;
      }  /* 单位 */
      table thead tr th:nth-child(5) { 
        width: 20% !important;
        min-width: 90px !important;
      }  /* 单价 */
      table thead tr th:nth-child(6) { 
        width: 25% !important;
        min-width: 100px !important;
      }  /* 总计 */
      table thead tr th:nth-child(7) { 
        width: 0 !important;
        display: none !important;
      }   /* 操作 */
      
      /* 表格单元格基础样式 */
      table td, table th {
        padding: 8px 10px !important;
        vertical-align: middle !important;
        box-sizing: border-box !important;
        border: 1px solid rgb(209, 213, 219) !important;
        line-height: 1.5 !important;
        word-wrap: break-word !important;
      }
      
      /* 表头样式 */
      table th {
        background-color: rgb(243, 244, 246) !important;
        font-weight: 600 !important;
        text-align: center !important;
        font-size: 9.5pt !important;
        padding: 7px 8px !important;
      }
      
      /* 表格body单元格样式 */
      table tbody td {
        font-size: 10pt !important;
        padding: 7px 10px !important;
      }
      
      /* 序号列居中 */
      table tbody td:nth-child(1) {
        text-align: center !important;
      }
      
      /* 项目列左对齐 */
      table tbody td:nth-child(2) {
        text-align: left !important;
        padding-left: 12px !important;
      }
      
      /* 数量列右对齐 */
      table tbody td:nth-child(3) {
        text-align: right !important;
        padding-right: 12px !important;
      }
      
      /* 单位列居中 */
      table tbody td:nth-child(4) {
        text-align: center !important;
      }
      
      /* 单价列右对齐 */
      table tbody td:nth-child(5) {
        text-align: right !important;
        padding-right: 12px !important;
      }
      
      /* 价钱总计列右对齐 */
      table tbody td:nth-child(6) {
        text-align: right !important;
        padding-right: 12px !important;
      }
      
      /* 合计行样式 */
      table tbody tr:last-child {
        background-color: rgb(249, 250, 251) !important;
        font-weight: 700 !important;
      }
      
      /* 合计行第一列（空白） */
      table tbody tr:last-child td:nth-child(1) {
        border: none !important;
        background-color: white !important;
      }
      
      /* 合计行第二列（"合计"文字）居中 */
      table tbody tr:last-child td:nth-child(2) {
        text-align: center !important;
        font-weight: 700 !important;
      }
      
      /* 合计行金额保持右对齐 */
      table tbody tr:last-child td:nth-child(6) {
        text-align: right !important;
        font-weight: 700 !important;
      }
      
      /* input 替换的 div 元素样式 */
      table td > div {
        display: block !important;
        width: 100% !important;
        box-sizing: border-box !important;
        overflow: visible !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.5 !important;
      }
      
      /* 确保替换的div继承父td的对齐方式 */
      table tbody td:nth-child(1) > div {
        text-align: center !important;
      }
      
      table tbody td:nth-child(2) > div {
        text-align: left !important;
      }
      
      table tbody td:nth-child(3) > div {
        text-align: right !important;
      }
      
      table tbody td:nth-child(4) > div {
        text-align: center !important;
      }
      
      table tbody td:nth-child(5) > div {
        text-align: right !important;
      }
      
      table tbody td:nth-child(6) > div {
        text-align: right !important;
      }
      
      /* 完全隐藏 hide-in-pdf 元素及其占位 */
      .hide-in-pdf {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
      }
      
      /* 隐藏操作列 */
      table thead tr th:nth-child(7),
      table tbody tr td:nth-child(7) {
        display: none !important;
        width: 0 !important;
      }
      
      /* 页面断点优化 */
      table {
        page-break-inside: avoid !important;
      }
      
      table tbody tr {
        page-break-inside: avoid !important;
        page-break-after: auto !important;
      }
      
      /* 避免标题和备注被分页 */
      h1, h2, h3 {
        page-break-after: avoid !important;
      }
      
      /* 签名区域不分页 */
      #quotation-sheet > div:last-child {
        page-break-inside: avoid !important;
      }
      
      /* 表格上下间距 */
      table {
        margin: 8px 0 !important;
      }
    `
    document.head.appendChild(tempStyle)
    
    // 等待样式完全应用并渲染
    await new Promise(resolve => setTimeout(resolve, 200))
    
    // html2canvas 配置 - 平衡质量与稳定性
    // 210mm @ 96 DPI = 794px
    const canvas = await html2canvas(element, {
      scale: 2,  // 2倍分辨率，平衡质量与性能
      useCORS: true,
      logging: true,  // 开启日志便于调试
      backgroundColor: '#ffffff',
      removeContainer: false,
      allowTaint: true,
      imageTimeout: 15000,
      width: element.offsetWidth,  // 使用元素实际宽度
      height: element.offsetHeight,  // 使用元素实际高度
      scrollY: -window.scrollY,
      scrollX: -window.scrollX,
      foreignObjectRendering: false,  // 禁用可能导致问题的渲染
      ignoreElements: (el) => {
        // 忽略具有 hide-in-pdf 类的元素
        return el.classList && el.classList.contains('hide-in-pdf')
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
    
    const pageHeight = a4Height - (margin * 2)
    
    console.log(`📏 Canvas尺寸: ${canvasWidth}x${canvasHeight}`)
    console.log(`📄 PDF尺寸: ${imgWidth}mm x ${imgHeight}mm`)
    console.log(`📃 页面高度: ${pageHeight}mm`)
    
    // 智能分页处理
    if (imgHeight > pageHeight) {
      console.log('📄 内容超过一页，启用分页')
      
      // 计算需要的页数
      const totalPages = Math.ceil(imgHeight / pageHeight)
      console.log(`📚 总页数: ${totalPages}`)
      
      // 逐页添加内容
      for (let i = 0; i < totalPages; i++) {
        if (i > 0) {
          pdf.addPage()
        }
        
        // 计算当前页应显示的图片部分
        const sourceY = i * pageHeight * (canvasHeight / imgHeight)
        const sourceHeight = Math.min(pageHeight * (canvasHeight / imgHeight), canvasHeight - sourceY)
        const destHeight = sourceHeight * (imgHeight / canvasHeight)
        
        // 创建临时 canvas 来裁剪图片
        const tempCanvas = document.createElement('canvas')
        const tempCtx = tempCanvas.getContext('2d')
        tempCanvas.width = canvasWidth
        tempCanvas.height = sourceHeight
        
        // 从原始 canvas 裁剪当前页的内容
        tempCtx.drawImage(canvas, 0, sourceY, canvasWidth, sourceHeight, 0, 0, canvasWidth, sourceHeight)
        const pageImgData = tempCanvas.toDataURL('image/png', 0.95)
        
        // 添加到 PDF
        pdf.addImage(pageImgData, 'PNG', margin, margin, imgWidth, destHeight)
        
        console.log(`📄 第 ${i + 1}/${totalPages} 页已添加`)
      }
    } else {
      // 内容适合一页
      console.log('📄 内容适合一页')
      pdf.addImage(imgData, 'PNG', margin, margin, imgWidth, imgHeight)
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
    
    // 恢复 input 元素
    if (inputReplacements.length > 0) {
      console.log(`🔄 恢复 ${inputReplacements.length} 个 input 元素`)
      inputReplacements.forEach(({ input, parent, replacement }) => {
        try {
          if (parent && replacement && replacement.parentNode === parent) {
            parent.replaceChild(input, replacement)
          }
        } catch (error) {
          console.warn('恢复 input 时出错:', error)
        }
      })
    }
    
    // 恢复报价单元素的原始样式
    if (element && Object.keys(originalStyle).length > 0) {
      element.style.position = originalStyle.position || ''
      element.style.left = originalStyle.left || ''
      element.style.top = originalStyle.top || ''
      element.style.width = originalStyle.width || ''
      element.style.maxWidth = originalStyle.maxWidth || ''
      element.style.minHeight = originalStyle.minHeight || ''
      element.style.margin = originalStyle.margin || ''
      element.style.padding = originalStyle.padding || ''
      element.style.transform = originalStyle.transform || ''
      element.style.zIndex = originalStyle.zIndex || ''
      element.style.background = originalStyle.background || ''
      element.style.boxSizing = originalStyle.boxSizing || ''
      element.style.fontSize = originalStyle.fontSize || ''
    }
    
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
    
    // 恢复下载按钮容器
    const downloadButtonContainer = document.querySelector('.h-18')
    if (downloadButtonContainer) {
      downloadButtonContainer.style.display = ''
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

