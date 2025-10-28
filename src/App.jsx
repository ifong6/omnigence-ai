import { useState } from 'react'
import ChatBox from './components/ChatBox/ChatBox'
import QuotationSheet from './components/QuotationSheet/QuotationSheet'
import { exportQuotationPDF } from './utils/reactPdfExport'
import { HiDownload } from 'react-icons/hi'  // 导入下载图标

function App() {
  const [quotationData, setQuotationData] = useState(null)

  const handleQuotationGenerated = (data) => {
    setQuotationData(data)
  }

  const handleQuotationSave = (data) => {
    // 保存报价单到本地存储
    if (data) {
      setQuotationData(data)
    }
  }

  const handleDownloadPDF = async () => {
    if (!quotationData) {
      alert('请先生成报价单！')
      return
    }

    console.log('📥 准备导出PDF...')
    
    try {
      // 导出PDF（隐藏逻辑在 exportQuotationPDF 内部处理）
      const success = await exportQuotationPDF(quotationData)
      
      console.log('📄 PDF导出结果:', success)
      
      if (success && handleQuotationSave) {
        handleQuotationSave(quotationData)
      }
    } catch (error) {
      console.error('❌ PDF导出失败:', error)
      alert(`PDF导出失败: ${error.message}\n\n请检查浏览器控制台获取详细信息。`)
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 左侧 - 对话区域 */}
      <div className="w-2/5 border-r border-gray-200 bg-white">
        <ChatBox onQuotationGenerated={handleQuotationGenerated} />
      </div>

      {/* 右侧 - 预览区域 */}
      <div className="w-3/5 flex flex-col">
        {/* 报价单预览 */}
        <div className="flex-1 overflow-auto">
          <QuotationSheet 
            data={quotationData}
            onSave={handleQuotationSave}
          />
        </div>

        {/* 下载PDF按钮 */}
        <div className="h-18  border-gray-200 bg-white flex items-center justify-center print:hidden">
          <button
            onClick={handleDownloadPDF}
            className="bg-black text-white px-10 py-2 rounded-lg hover:bg-gray-800 transition-colors flex items-center justify-center space-x-2"
          >
            <HiDownload className="text-white text-1xl" />
            <span>Download PDF</span>
          </button>
        </div>

      </div>
    </div>
  );
}

export default App;
