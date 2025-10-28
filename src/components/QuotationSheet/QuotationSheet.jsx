import { useState, useEffect, useRef } from 'react'
import SignatureModal from '../SignatureModal/SignatureModal'

const QuotationSheet = ({ data, onSave }) => {
  const [formData, setFormData] = useState({
    quotationNumber: 'INV-01-JCE-YY-NO-VER',
    currentDate: new Date().toLocaleDateString('zh-CN'),
    quotationVersion: '1.0',
    companyName: '港珀工程顾问有限公司',
    companyNameEn: 'CHUIKPAR ENGINEERING CONSULTANCY, LTD.',
    businessType: '澳门 • Engineering Consultancy',
    clientName: '',
    phoneNumber: '',
    address: '',
    projectName: '',
    items: [

    ],
    totalAmount: '',
    notes: [
      '1.本报价单包括以下所有费用除额外工作',
      '2.本报价单按现场实际作为开设数量',
      '3.本工程不包括税费',
      '4.若因客情用申报后如果得到回答'
    ],
    managerSignature: null,
    managerSignDate: null,
    technicianSignature: null,
    technicianSignDate: null,
  })

  // 签名弹窗状态
  const [signatureModal, setSignatureModal] = useState({
    isOpen: false,
    type: null, // 'manager' 或 'technician'
    title: ''
  })

  // 用于跟踪上一次的报价单编号和客户名称
  const previousQuotationRef = useRef({
    quotationNumber: '',
    clientName: '',
    projectName: ''
  })

  useEffect(() => {
    if (data) {
      const isNewQuotation = 
        data.quotationNumber !== previousQuotationRef.current.quotationNumber ||
        data.clientName !== previousQuotationRef.current.clientName ||
        data.projectName !== previousQuotationRef.current.projectName

      let newVersion = '1.0'
      
      if (!isNewQuotation && formData.quotationVersion) {
        // 相同的报价单，版本号递增
        const currentVersion = parseFloat(formData.quotationVersion)
        newVersion = (currentVersion + 0.1).toFixed(1)
        console.log(`📝 报价单修订：版本 ${formData.quotationVersion} → ${newVersion}`)
      } else {
        // 新的报价单，重置为1.0
        console.log('新报价单生成：版本 1.0')
      }

      setFormData({ 
        ...formData, 
        ...data,
        quotationVersion: newVersion
      })

      // 更新引用
      previousQuotationRef.current = {
        quotationNumber: data.quotationNumber,
        clientName: data.clientName,
        projectName: data.projectName
      }
    }
  }, [data])

  // 处理表格项的编辑
  const handleItemChange = (index, field, value) => {
    const newItems = [...formData.items]
    newItems[index] = {
      ...newItems[index],
      [field]: value
    }
    
    // 如果修改了数量或单价，自动计算总价
    if (field === 'quantity' || field === 'unitPrice') {
      const quantity = parseFloat(field === 'quantity' ? value : newItems[index].quantity) || 0
      const unitPrice = parseFloat(field === 'unitPrice' ? value : newItems[index].unitPrice) || 0
      const totalPrice = (quantity * unitPrice).toFixed(2)
      
      newItems[index].totalPrice = totalPrice
      console.log(`🧮 自动计算：${quantity} × ${unitPrice} = ${totalPrice}`)
    }
    
    // 计算新的总金额
    const total = newItems.reduce((sum, item) => {
      const price = parseFloat(item.totalPrice) || 0
      return sum + price
    }, 0)
    const formattedTotal = `MOP $ ${total.toFixed(2)}`
    
    // 更新items和总金额
    const updatedFormData = {
      ...formData,
      items: newItems,
      totalAmount: formattedTotal
    }
    
    setFormData(updatedFormData)
    
    // 通知父组件
    if (onSave) {
      onSave(updatedFormData)
    }
    
    console.log(`📝 编辑项目 ${index + 1} 的 ${field}: ${value}`)
  }

  // 自动更新总金额
  const updateTotalAmount = (items) => {
    const total = items.reduce((sum, item) => {
      const price = parseFloat(item.totalPrice) || 0
      return sum + price
    }, 0)
    
    const formattedTotal = `MOP $ ${total.toFixed(2)}`
    
    setFormData(prev => ({
      ...prev,
      totalAmount: formattedTotal
    }))
    
    console.log(`💰 更新总金额: ${formattedTotal}`)
  }

  // 从金额字符串中提取纯数字（去掉"MOP $"等前缀）
  const extractNumber = (value) => {
    if (typeof value === 'number') return value
    if (typeof value === 'string') {
      // 移除所有非数字和小数点的字符
      const number = value.replace(/[^\d.]/g, '')
      return number
    }
    return '0.00'
  }

  // 添加新的项目行
  const handleAddItem = () => {
    const newItem = {
      sequence: formData.items.length + 1,
      project: '',
      quantity: 1,
      unit: 'Lot',
      unitPrice: '0.00',
      totalPrice: '0.00'
    }
    
    const newItems = [...formData.items, newItem]
    
    setFormData({
      ...formData,
      items: newItems
    })
    
    // 更新总金额
    updateTotalAmount(newItems)
    
    console.log('➕ 添加新项目行')
  }

  // 删除项目行
  const handleDeleteItem = (index) => {
    if (formData.items.length <= 1) {
      alert('至少需要保留一个项目！')
      return
    }
    
    const newItems = formData.items.filter((_, i) => i !== index)
    // 重新排序序号
    const reorderedItems = newItems.map((item, i) => ({
      ...item,
      sequence: i + 1
    }))
    
    setFormData({
      ...formData,
      items: reorderedItems
    })
    
    // 更新总金额
    updateTotalAmount(reorderedItems)
    
    console.log(`🗑️ 删除项目行 ${index + 1}`)
  }

  // 打开签名弹窗
  const handleOpenSignature = (type) => {
    const titles = {
      manager: '管理顾问主席签名',
      technician: '技术员签名'
    }
    
    setSignatureModal({
      isOpen: true,
      type: type,
      title: titles[type]
    })
  }

  // 保存签名
  const handleSaveSignature = ({ signature, date }) => {
    const updatedFormData = {
      ...formData,
      ...(signatureModal.type === 'manager' ? {
        managerSignature: signature,
        managerSignDate: date
      } : {
        technicianSignature: signature,
        technicianSignDate: date
      })
    }
    
    setFormData(updatedFormData)
    
    // 通知父组件
    if (onSave) {
      onSave(updatedFormData)
    }
    
    console.log(`✍️ ${signatureModal.type === 'manager' ? '管理顾问' : '技术员'}签名完成`)
  }

  // 清除签名
  const handleClearSignature = (type) => {
    const updatedFormData = {
      ...formData,
      ...(type === 'manager' ? {
        managerSignature: null,
        managerSignDate: null
      } : {
        technicianSignature: null,
        technicianSignDate: null
      })
    }
    
    setFormData(updatedFormData)
    
    // 通知父组件
    if (onSave) {
      onSave(updatedFormData)
    }
    
    console.log(`🗑️ 清除${type === 'manager' ? '管理顾问' : '技术员'}签名`)
  }

  return (
    <div id="quotation-sheet" className="px-4 mx-auto bg-white">
      {/* 顶部标识区域 */}
      <div className="p-6 border-gray-800">
        <div className="flex justify-between items-start">
            <div className="text-xs text-gray-600">
              <div className="font-bold">{formData.companyName}</div>
              <div className="text-gray-500">{formData.companyNameEn}</div>
              <div className="mt-1  border border-gray-800 rounded-2xl px-2 w-fit">{formData.businessType}</div>
            </div>
          <div className="text-left text-xs">
            <div className="font-bold">编号 NO：{formData.quotationNumber}</div>
            <div className="font-bold">日期 Date：{formData.currentDate}</div>
            <div className="font-bold">版本 REV：{formData.quotationVersion}</div>
          </div>
        </div>
      </div>

      {/* 报价单标题 */}
      <div className="text-center ">
        <h1 className="text-2xl font-bold">报价单 Quotation Sheet</h1>
        <p className="text-sm text-gray-600 mt-1">Official quotation</p>
      </div>

      {/* 客户信息 */}
      <div className="p-6 space-y-3">
        {/* 第一行：客户（占满整行） */}
        <div className="flex items-center">
          <label className="bg-gray-100 px-4 py-2 rounded-l font-medium min-w-[100px]">
            客户
          </label>
          <input
            type="text"
            value={formData.clientName}
            onChange={(e) =>
              setFormData({ ...formData, clientName: e.target.value })
            }
            className="flex-1 px-4 py-2 border border-l-0 border-gray-300 rounded-r focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* 第二行：电话号码和地址（两列等宽） */}
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center">
            <label className="bg-gray-100 px-4 py-2 rounded-l font-medium min-w-[100px]">
              电话号码
            </label>
            <input
              type="text"
              value={formData.phoneNumber}
              onChange={(e) =>
                setFormData({ ...formData, phoneNumber: e.target.value })
              }
              className="flex-1 px-4 py-2 border border-l-0 border-gray-300 rounded-r focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex items-center">
            <label className="bg-gray-100 px-4 py-2 rounded-l font-medium min-w-[100px]">
              地址
            </label>
            <input
              type="text"
              value={formData.address}
              onChange={(e) =>
                setFormData({ ...formData, address: e.target.value })
              }
              className="flex-1 px-4 py-2 border border-l-0 border-gray-300 rounded-r focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="flex items-center mt-8">
          <div className="bg-gray-100 px-4 py-2 rounded-l font-medium min-w-[100px]">项目名称</div>
          <input
            type="text"
            value={formData.projectName}
            onChange={(e) =>
              setFormData({ ...formData, projectName: e.target.value })
            }
            className="flex-1 px-4 py-2 border border-l-0 border-gray-300 rounded-r focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* 项目明细表 */}
      <div className="px-6 pb-6">
        <table className="w-full border-collapse border border-gray-300">
          <thead className="bg-gray-100">
            <tr>
              <th className="border border-gray-300 px-3 py-2 text-sm">序号</th>
              <th className="border border-gray-300 px-3 py-2 text-sm">项目</th>
              <th className="border border-gray-300 px-3 py-2 text-sm">数量</th>
              <th className="border border-gray-300 px-3 py-2 text-sm">单位</th>
              <th className="border border-gray-300 px-3 py-2 text-sm">
                单价
                <br />
                (澳门元)
              </th>
              <th className="border border-gray-300 px-3 py-2 text-sm">
                价钱总计
                <br />
                (澳门元)
              </th>
              <th className="border border-gray-300 px-3 py-2 text-sm hide-in-pdf">
                操作
              </th>
            </tr>
          </thead>
          <tbody>
            {formData.items.map((item, index) => (
              <tr key={index}>
                <td className="border border-gray-300 px-1 py-1 text-center text-sm">
                  <input
                    type="number"
                    value={item.sequence}
                    onChange={(e) => handleItemChange(index, 'sequence', e.target.value)}
                    className="w-full text-center border-0 focus:outline-none focus:ring-1 focus:ring-blue-500 rounded px-1"
                  />
                </td>
                <td className="border border-gray-300 px-1 py-1 text-sm">
                  <input
                    type="text"
                    value={item.project}
                    onChange={(e) => handleItemChange(index, 'project', e.target.value)}
                    className="w-full border-0 focus:outline-none focus:ring-1 focus:ring-blue-500 rounded px-2"
                  />
                </td>
                <td className="border border-gray-300 px-1 py-1 text-center text-sm">
                  <input
                    type="number"
                    value={item.quantity}
                    onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                    className="w-full text-center border-0 focus:outline-none focus:ring-1 focus:ring-blue-500 rounded px-1"
                  />
                </td>
                <td className="border border-gray-300 px-1 py-1 text-center text-sm">
                  <input
                    type="text"
                    value={item.unit}
                    onChange={(e) => handleItemChange(index, 'unit', e.target.value)}
                    className="w-full text-center border-0 focus:outline-none focus:ring-1 focus:ring-blue-500 rounded px-2"
                  />
                </td>
                <td className="border border-gray-300 px-1 py-1 text-right text-sm">
                  <input
                    type="number"
                    step="0.01"
                    value={extractNumber(item.unitPrice)}
                    onChange={(e) => handleItemChange(index, 'unitPrice', e.target.value)}
                    className="w-full text-right border-0 focus:outline-none focus:ring-1 focus:ring-blue-500 rounded px-2"
                    placeholder="0.00"
                  />
                </td>
                <td className="border border-gray-300 px-1 py-1 text-right text-sm">
                  <input
                    type="number"
                    step="0.01"
                    value={extractNumber(item.totalPrice)}
                    onChange={(e) => handleItemChange(index, 'totalPrice', e.target.value)}
                    className="w-full text-right border-0 focus:outline-none focus:ring-1 focus:ring-blue-500 rounded px-2 bg-gray-50"
                    placeholder="0.00"
                    readOnly
                    title="自动计算：数量 × 单价"
                  />
                </td>
                <td className="border border-gray-300 px-2 py-1 text-center text-sm hide-in-pdf">
                  <button
                    onClick={() => handleDeleteItem(index)}
                    className="text-red-600 hover:text-red-800 hover:bg-red-50 px-2 py-1 rounded transition-colors"
                    title="删除此项"
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            ))}
            <tr className="bg-gray-50 font-bold">
              <td
                colSpan="5"
                className="border border-gray-300 px-3 py-2 text-right"
              >
                合计
              </td>
              <td className="border border-gray-300 px-3 py-2 text-right">
                {formData.totalAmount}
              </td>
              <td className="border border-gray-300 hide-in-pdf"></td>
            </tr>
          </tbody>
        </table>

        {/* 添加项目按钮 */}
        <div className="mt-3 hide-in-pdf">
          <button
            onClick={handleAddItem}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors flex items-center space-x-2"
          >
            <span>➕</span>
            <span>添加新项目</span>
          </button>
        </div>
      </div>

      {/* 备注 */}
      <div className="px-6 pb-6">
        <div className="text-sm font-medium mb-2">备注：</div>
        <div className="text-sm text-gray-700 space-y-1">
          {formData.notes.map((note, index) => (
            <div key={index}>{note}</div>
          ))}
        </div>
      </div>

      {/* 签名区域 */}
      <div className="px-6 pb-6">
        <div className="">
          <div className="bg-gray-100 p-2 rounded-lg font-medium mb-4">Signature</div>
          <div className="grid grid-cols-2 gap-8">
            {/* 管理顾问签名 */}
            <div>
              <div className="mb-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm">管理顾问主席签名及确认:</span>
                  {formData.managerSignature && (
                    <button
                      onClick={() => handleClearSignature('manager')}
                      className="text-xs text-red-600 hover:text-red-800 hide-in-pdf"
                    >
                      清除
                    </button>
                  )}
                </div>
                {formData.managerSignature ? (
                  <div className="border-2 border-gray-300 rounded p-2 bg-white">
                    <img 
                      src={formData.managerSignature} 
                      alt="Manager Signature" 
                      className="w-full h-20 object-contain"
                    />
                  </div>
                ) : (
                  <button
                    onClick={() => handleOpenSignature('manager')}
                    className="w-full py-3 border-2 border-dashed border-gray-300 rounded hover:border-blue-500 hover:bg-blue-50 transition-colors text-gray-500 hover:text-blue-600 hide-in-pdf"
                  >
                    点击签名
                  </button>
                )}
              </div>
              <div className="flex items-center">
                <span className="mr-2 text-sm">日期:</span>
                <div className="flex-1 py-2 border-b border-gray-400 text-sm">
                  {formData.managerSignDate || ''}
                </div>
              </div>
            </div>
            
            {/* 技术员签名 */}
            <div>
              <div className="mb-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm">技术员:</span>
                  {formData.technicianSignature && (
                    <button
                      onClick={() => handleClearSignature('technician')}
                      className="text-xs text-red-600 hover:text-red-800 hide-in-pdf"
                    >
                      清除
                    </button>
                  )}
                </div>
                {formData.technicianSignature ? (
                  <div className="border-2 border-gray-300 rounded p-2 bg-white">
                    <img 
                      src={formData.technicianSignature} 
                      alt="Technician Signature" 
                      className="w-full h-20 object-contain"
                    />
                  </div>
                ) : (
                  <button
                    onClick={() => handleOpenSignature('technician')}
                    className="w-full py-3 border-2 border-dashed border-gray-300 rounded hover:border-blue-500 hover:bg-blue-50 transition-colors text-gray-500 hover:text-blue-600 hide-in-pdf"
                  >
                    点击签名
                  </button>
                )}
              </div>
              <div className="flex items-center">
                <span className="mr-2 text-sm">日期:</span>
                <div className="flex-1 py-2 border-b border-gray-400 text-sm">
                  {formData.technicianSignDate || ''}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 签名弹窗 */}
      <SignatureModal
        isOpen={signatureModal.isOpen}
        title={signatureModal.title}
        onSave={handleSaveSignature}
        onClose={() => setSignatureModal({ isOpen: false, type: null, title: '' })}
      />

    </div>
  )
}

export default QuotationSheet

