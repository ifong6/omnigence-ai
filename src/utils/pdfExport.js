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
  try {
    console.log('🚀 开始生成PDF...')
    
    // 动态导入html2pdf
    const html2pdf = (await import('html2pdf.js')).default
    
    // 获取要导出的元素
    const element = document.getElementById(elementId)
    
    if (!element) {
      throw new Error(`找不到ID为 ${elementId} 的元素`)
    }
    
    // PDF配置选项
    const opt = {
      margin: [10, 10, 10, 10],  // 上右下左边距（mm）
      filename: filename,
      image: { 
        type: 'jpeg', 
        quality: 0.98 
      },
      html2canvas: { 
        scale: 2,  // 提高清晰度
        useCORS: true,
        letterRendering: true
      },
      jsPDF: { 
        unit: 'mm', 
        format: 'a4', 
        orientation: 'portrait'  // 纵向
      },
      pagebreak: { 
        mode: ['avoid-all', 'css', 'legacy']  // 避免内容被截断
      }
    }
    
    console.log('📄 生成PDF配置:', opt)
    
    // 生成并下载PDF
    await html2pdf().set(opt).from(element).save()
    
    console.log('✅ PDF生成成功！')
    return true
    
  } catch (error) {
    console.error('❌ PDF导出失败:', error)
    alert(`PDF导出失败: ${error.message}`)
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

