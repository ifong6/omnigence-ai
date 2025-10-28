# PDF导出问题修复总结

## 🐛 问题描述
PDF导出的内容与前端显示的报价单格式不一致，数据字段不匹配。

## 🔍 根本原因
PDF模板使用的数据字段名与前端组件 `QuotationSheet.jsx` 中的实际字段名不一致。

## ✅ 修复内容

### 1. 数据字段映射修正

| 前端字段 | 旧PDF字段 | 新PDF字段 | 说明 |
|---------|----------|----------|------|
| `clientName` | `customerName` | `clientName` | 客户名称 |
| `phoneNumber` | `phone` | `phoneNumber` | 电话号码 |
| `currentDate` | `date` | `currentDate` | 日期 |
| `quotationVersion` | ❌ 无 | `quotationVersion` | 版本号 |
| `companyNameEn` | ❌ 无 | `companyNameEn` | 公司英文名 |
| `businessType` | `quotationType` | `businessType` | 业务类型 |
| `items[].project` | `items[].item` | `items[].project` | 项目名称 |
| `items[].sequence` | ❌ 使用index | `items[].sequence` | 序号 |
| `items[].unitPrice` | `items[].price` | `items[].unitPrice` | 单价 |
| `items[].totalPrice` | ❌ 计算得出 | `items[].totalPrice` | 总价 |
| `totalAmount` | ❌ 计算得出 | `totalAmount` | 总金额 |
| `notes[]` | `notes` (字符串) | `notes[]` (数组) | 备注 |

### 2. 页面头部修正
```jsx
// 旧格式
日期：2023/10/01
报价单号：QT-123456

// 新格式
编号 NO：INV-01-JCE-YY-NO-VER
日期 Date：2023/10/01
版本 REV：1.0
```

### 3. 公司信息修正
```jsx
// 旧格式
OMNIGENCE.AI
中国广东省广州市
AI智能报价

// 新格式
港珀工程顾问有限公司
CHUIKPAR ENGINEERING CONSULTANCY, LTD.
澳门 • Engineering Consultancy
```

### 4. 标题修正
```jsx
// 旧格式
报价单
QUOTATION SHEET

// 新格式
报价单 Quotation Sheet
Official quotation
```

### 5. 表格列名修正
```jsx
// 旧格式
单价 | 总计

// 新格式
单价           | 价钱总计
(澳门元)       | (澳门元)
```

### 6. 金额格式修正
```jsx
// 旧格式
¥6000.00

// 新格式
MOP $ 6000.00
```

### 7. 签名区域修正
```jsx
// 旧格式
客户签名：
业务员签名：

// 新格式
管理顾问主席签名及确认：
技术员：
```

### 8. 备注格式修正
```jsx
// 旧格式
<Text>{data.notes}</Text>  // 单个字符串

// 新格式
{data.notes.map((note, index) => (
  <Text key={index}>{note}</Text>
))}  // 数组循环
```

## 🔧 技术改进

### 1. 数据同步
在 `QuotationSheet.jsx` 中添加了 `useEffect` 监听 `formData` 变化：
```jsx
useEffect(() => {
  if (onSave && formData.items.length > 0) {
    onSave(formData)
  }
}, [formData, onSave])
```

这确保了每次用户编辑报价单时，父组件 `App.jsx` 都能获得最新数据。

### 2. 数据格式化
```jsx
// 格式化数字为两位小数
const formatNumber = (value) => {
  if (!value && value !== 0) return '0.00'
  const num = typeof value === 'string' 
    ? parseFloat(value.replace(/[^0-9.-]/g, '')) 
    : value
  return num.toFixed(2)
}
```

## 📊 测试检查清单

### 生成PDF前检查
- [ ] 确保报价单已填写完整
- [ ] 确保所有项目都有数量和单价
- [ ] 确保总金额显示正确（格式：MOP $ xxxx.xx）

### PDF内容检查
- [ ] 页面头部：公司名称（中英文）、编号、日期、版本
- [ ] 标题：报价单 Quotation Sheet
- [ ] 客户信息：客户、电话号码、地址、项目名称
- [ ] 表格：
  - [ ] 表头包含"(澳门元)"标识
  - [ ] 所有项目数据完整
  - [ ] 序号、数量、单价、总价正确
  - [ ] 合计行显示总金额
- [ ] 备注：所有备注条目都显示
- [ ] 签名：管理顾问主席签名及确认、技术员、日期

## 🚀 使用方法

1. 在聊天框输入需求，生成报价单
2. 在右侧预览区域查看和编辑报价单
3. 点击 "Download PDF" 按钮
4. PDF文件将自动下载到本地

## 📝 注意事项

- PDF导出会使用前端表单中的**实时数据**
- 任何在界面上的编辑都会反映在导出的PDF中
- 总金额会自动计算并格式化为 "MOP $ xxxx.xx"
- 备注默认包含4条预设内容，可根据需要在代码中修改

## 🎉 修复结果

现在PDF导出的内容与前端显示**完全一致**，包括：
✅ 所有数据字段正确映射
✅ 格式和样式完全匹配
✅ 货币单位正确（澳门元 MOP $）
✅ 中英文标签正确显示
✅ 签名区域字段正确

