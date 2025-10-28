# PDF导出解决方案 - @react-pdf/renderer

## 📋 方案概述

本项目使用 **@react-pdf/renderer** 库实现PDF导出功能，这是一个专为React设计的PDF生成解决方案。

## ✨ 方案优势

### 1. **自动下载**
- ✅ 无需用户手动操作打印对话框
- ✅ 点击"Download PDF"按钮即可自动下载
- ✅ 提供更好的用户体验

### 2. **完美的样式控制**
- ✅ 使用React组件语法定义PDF布局
- ✅ 精确控制每个元素的样式
- ✅ 零浏览器兼容性问题

### 3. **React友好**
- ✅ 使用JSX语法编写PDF模板
- ✅ 可以复用React组件逻辑
- ✅ 类型安全（支持TypeScript）

### 4. **高性能**
- ✅ 纯JavaScript实现，不依赖浏览器打印功能
- ✅ 生成速度快
- ✅ 支持大型文档

## 🏗️ 技术架构

### 核心依赖
```json
{
  "@react-pdf/renderer": "^4.2.0"
}
```

### 主要文件
- `src/utils/reactPdfExport.js` - PDF生成核心逻辑
- `src/App.jsx` - PDF下载触发入口

## 📖 使用说明

### 1. PDF文档结构

PDF文档使用 `@react-pdf/renderer` 的组件定义：

```jsx
import { Document, Page, Text, View, StyleSheet } from '@react-pdf/renderer'

const QuotationPDF = ({ data }) => (
  <Document>
    <Page size="A4" style={styles.page}>
      {/* PDF内容 */}
    </Page>
  </Document>
)
```

### 2. 样式定义

使用 `StyleSheet.create` 定义样式（类似CSS）：

```jsx
const styles = StyleSheet.create({
  page: {
    padding: 40,
    fontSize: 10,
    fontFamily: 'Helvetica',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  // ...更多样式
})
```

### 3. 导出PDF

```javascript
import { exportQuotationPDF } from './utils/reactPdfExport'

// 在组件中调用
const handleDownloadPDF = async () => {
  const success = await exportQuotationPDF(quotationData)
  if (success) {
    console.log('PDF下载成功')
  }
}
```

## 🎨 PDF样式特性

### 布局系统
- **Flexbox布局** - 与CSS Flexbox类似
- **Box模型** - 支持padding、margin、border
- **定位** - 支持absolute和relative定位

### 文本样式
- **字体** - Helvetica, Times-Roman, Courier（内置）
- **字号** - fontSize属性
- **字重** - fontWeight: 'normal' | 'bold'
- **颜色** - color属性（支持hex和rgb）

### 尺寸单位
- **pt** - 点（默认单位）
- **百分比** - '50%'
- **无单位数字** - 等同于pt

## 📄 PDF内容区域

### 1. 页面头部
- 公司信息
- 报价单号
- 日期

### 2. 标题区域
- 主标题："报价单"
- 副标题："QUOTATION SHEET"

### 3. 客户信息
- 客户名称
- 电话号码、地址（两列布局）
- 项目名称

### 4. 项目明细表
- 表头：序号、项目、数量、单位、单价、总计
- 数据行：自动计算每行总计
- 合计行：所有项目总计

### 5. 备注区域
- 可选的备注信息

### 6. 签名区域
- 客户签名、业务员签名
- 日期确认

## 🔧 自定义配置

### 修改页面尺寸
```jsx
<Page size="A4">  // 支持: A4, A3, Letter等
```

### 修改页边距
```jsx
const styles = StyleSheet.create({
  page: {
    padding: 40,  // 修改这个值
  }
})
```

### 修改字体
```jsx
const styles = StyleSheet.create({
  page: {
    fontFamily: 'Helvetica',  // 可选: Times-Roman, Courier
  }
})
```

## 🐛 常见问题

### Q: PDF中文显示异常？
A: `@react-pdf/renderer` 默认支持中文（使用Helvetica字体的Unicode变体）。如果需要特殊字体，可以注册自定义字体：

```javascript
import { Font } from '@react-pdf/renderer'

Font.register({
  family: 'NotoSans',
  src: 'path/to/NotoSans-Regular.ttf'
})
```

### Q: 如何调整表格列宽？
A: 在 `reactPdfExport.js` 中修改对应的列宽样式：

```javascript
col1: { width: '8%' },  // 序号列
col2: { width: '24%' }, // 项目列
// ...
```

### Q: 如何添加页码？
A: 使用 `render` 属性动态添加：

```jsx
<Page>
  <Text render={({ pageNumber, totalPages }) => 
    `第 ${pageNumber} 页 / 共 ${totalPages} 页`
  } fixed />
</Page>
```

### Q: PDF文件太大？
A: 优化建议：
- 避免使用高分辨率图片
- 减少不必要的样式
- 使用内置字体而不是自定义字体

## 📊 性能对比

| 方案 | 生成速度 | 样式保真度 | 用户体验 | 维护性 |
|------|---------|-----------|---------|--------|
| html2canvas + jsPDF | 慢 | 中等 | 中等 | 低 |
| window.print() | 快 | 高 | 差（需手动操作） | 中 |
| **@react-pdf/renderer** | **快** | **高** | **优秀** | **高** |

## 🚀 未来优化方向

1. **添加水印** - 在PDF中添加公司水印
2. **多页支持** - 自动分页处理长表格
3. **模板系统** - 支持多种报价单模板
4. **预览功能** - 下载前预览PDF
5. **批量导出** - 同时导出多个报价单

## 📚 参考资料

- [官方文档](https://react-pdf.org/)
- [样式指南](https://react-pdf.org/styling)
- [组件API](https://react-pdf.org/components)
- [示例代码](https://react-pdf.org/repl)

## 🎯 总结

使用 `@react-pdf/renderer` 方案可以：
- ✅ 实现自动下载PDF
- ✅ 完美控制PDF样式
- ✅ 提供优秀的用户体验
- ✅ 易于维护和扩展

这是目前最适合本项目的PDF导出解决方案。

