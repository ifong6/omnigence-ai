import { useState } from 'react'
import ChatBox from './components/ChatBox/ChatBox'
import SearchBar from './components/SearchBar/SearchBar'
import QuotationSheet from './components/QuotationSheet/QuotationSheet'
import { exportQuotationPDF } from './utils/pdfExport'
import { HiDownload } from 'react-icons/hi'  // 导入下载图标

function App() {
  const [quotationData, setQuotationData] = useState(null)
  const [savedQuotations, setSavedQuotations] = useState([])

  const handleQuotationGenerated = (data) => {
    setQuotationData(data)
  }

  const handleQuotationSave = (data) => {
    setSavedQuotations([...savedQuotations, data])
  }

  const handleSearchResult = (result) => {
    setQuotationData(result)
  }

  const handleDownloadPDF = async () => {
    if (!quotationData) {
      alert('请先生成报价单！')
      return
    }

    console.log('📥 准备导出PDF...')
    
    // 临时隐藏不需要打印的元素
    const hideElements = document.querySelectorAll('.hide-in-pdf')
    hideElements.forEach(el => el.style.display = 'none')
    
    try {
      const success = await exportQuotationPDF(quotationData)
      
      if (success && handleQuotationSave) {
        handleQuotationSave(quotationData)
      }
    } finally {
      // 恢复隐藏的元素
      hideElements.forEach(el => el.style.display = '')
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 左侧 - 对话区域 */}
      <div className="w-2/5 border-r border-gray-200 bg-white">
        <ChatBox onQuotationGenerated={handleQuotationGenerated} />
      </div>

      {/* 右侧 - 搜索和预览区域 */}
      <div className="w-3/5 flex flex-col">
        {/* 上方 - 搜索栏 */}
        <div className="h-26 border-b border-gray-200 bg-white">
          <SearchBar 
            savedQuotations={savedQuotations}
            onSearchResult={handleSearchResult}
          />
        </div>

        {/* 中间 - 报价单预览 */}
        <div className="flex-1 overflow-auto">
          <QuotationSheet 
            data={quotationData}
            onSave={handleQuotationSave}
          />
        </div>

        {/* 下方 - 下载PDF按钮 */}
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
