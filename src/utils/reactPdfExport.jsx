import React from 'react'
import { Document, Page, Text, View, StyleSheet, pdf, Font, Image } from '@react-pdf/renderer'

// 注册支持中文的字体
// 使用系统自带的无需下载的方案，确保中文正常显示
Font.register({
  family: 'NotoSansSC',
  src: 'https://cdn.jsdelivr.net/npm/@fontsource/noto-sans-sc@5.0.0/files/noto-sans-sc-chinese-simplified-400-normal.woff'
})

// 定义PDF样式 - 优化后适配A4单页
const styles = StyleSheet.create({
  page: {
    padding: '15mm',
    fontSize: 8,
    fontFamily: 'NotoSansSC',
    backgroundColor: '#ffffff',
    lineHeight: 1.2,
  },
  // 头部区域
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
    paddingBottom: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  companyInfo: {
    flex: 1,
  },
  companyName: {
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  companyAddress: {
    fontSize: 7,
    color: '#6b7280',
    marginBottom: 2,
  },
  quotationType: {
    backgroundColor: '#1f2937',
    color: '#ffffff',
    padding: '2 6',
    borderRadius: 2,
    fontSize: 6,
    marginTop: 2,
    alignSelf: 'flex-start',
  },
  headerRight: {
    alignItems: 'flex-end',
  },
  headerRightText: {
    fontSize: 7,
    marginBottom: 1,
    textAlign: 'right',
  },
  headerRightLabel: {
    fontWeight: 'bold',
  },
  // 标题区域
  titleSection: {
    alignItems: 'center',
    marginVertical: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    letterSpacing: 1,
    marginBottom: 8,
    lineHeight: 1.3,
  },
  subtitle: {
    fontSize: 7,
    color: '#6b7280',
    letterSpacing: 0.3,
    marginTop: 3,
    lineHeight: 1.4,
  },
  // 客户信息区域
  customerSection: {
    marginBottom: 6,
  },
  infoRow: {
    flexDirection: 'row',
    marginBottom: 4,
    borderWidth: 1,
    borderColor: '#9ca3af',
    borderRadius: 2,
    overflow: 'hidden',
    minHeight: 20,
  },
  infoLabel: {
    backgroundColor: '#e5e7eb',
    padding: '4 6',
    width: 60,
    fontWeight: 'bold',
    fontSize: 7,
    borderRightWidth: 1,
    borderRightColor: '#9ca3af',
    justifyContent: 'center',
    alignItems: 'center',
  },
  infoValue: {
    padding: '4 6',
    flex: 1,
    fontSize: 7,
    justifyContent: 'center',
  },
  twoColumnRow: {
    flexDirection: 'row',
    gap: 6,
    marginBottom: 4,
  },
  twoColumnItem: {
    flex: 1,
    flexDirection: 'row',
    borderWidth: 1,
    borderColor: '#9ca3af',
    borderRadius: 2,
    overflow: 'hidden',
    minHeight: 20,
  },
  // 表格样式
  table: {
    marginVertical: 4,
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#e5e7eb',
    borderWidth: 1,
    borderColor: '#d1d5db',
    fontWeight: 'bold',
  },
  tableRow: {
    flexDirection: 'row',
    borderLeftWidth: 1,
    borderRightWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#d1d5db',
  },
  tableTotalRow: {
    flexDirection: 'row',
    backgroundColor: '#f3f4f6',
    borderLeftWidth: 1,
    borderRightWidth: 1,
    borderBottomWidth: 1,
    borderTopWidth: 1.5,
    borderColor: '#9ca3af',
    fontWeight: 'bold',
  },
  tableCell: {
    padding: 3,
    fontSize: 7,
    justifyContent: 'center',
  },
  tableCellHeader: {
    padding: 4,
    fontSize: 6.5,
    fontWeight: 'bold',
    justifyContent: 'center',
    lineHeight: 1.1,
  },
  // 列宽
  col1: { width: '8%', textAlign: 'center' },  // 序号
  col2: { width: '28%', textAlign: 'left', paddingLeft: 4 },  // 项目
  col3: { width: '10%', textAlign: 'right', paddingRight: 4 },  // 数量
  col4: { width: '10%', textAlign: 'center' },  // 单位
  col5: { width: '20%', textAlign: 'right', paddingRight: 4 },  // 单价
  col6: { width: '24%', textAlign: 'right', paddingRight: 4 },  // 总计
  // 备注区域
  notesSection: {
    marginTop: 6,
    marginBottom: 6,
  },
  notesTitle: {
    fontWeight: 'bold',
    fontSize: 7,
    marginBottom: 2,
    color: '#1f2937',
  },
  notesContent: {
    fontSize: 6.5,
    lineHeight: 1.3,
    color: '#374151',
    marginBottom: 1,
  },
  // 签名区域
  signatureSection: {
    marginTop: 8,
    paddingTop: 6,
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  signatureTitle: {
    fontWeight: 'bold',
    fontSize: 8,
    marginBottom: 6,
    color: '#1f2937',
  },
  signatureRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 12,
  },
  signatureBox: {
    width: '48%',
  },
  signatureLabel: {
    fontSize: 6.5,
    color: '#374151',
    marginBottom: 2,
  },
  signatureLine: {
    borderBottomWidth: 1,
    borderBottomColor: '#9ca3af',
    paddingBottom: 2,
  },
})

// PDF文档组件
const QuotationPDF = ({ data }) => {
  // 格式化数字为两位小数
  const formatNumber = (value) => {
    if (!value && value !== 0) return '0.00'
    const num = typeof value === 'string' ? parseFloat(value.replace(/[^0-9.-]/g, '')) : value
    return num.toFixed(2)
  }

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* 头部 */}
        <View style={styles.header}>
          <View style={styles.companyInfo}>
            <Text style={styles.companyName}>{data?.companyName || '港珀工程顾问有限公司'}</Text>
            <Text style={styles.companyAddress}>
              {data?.companyNameEn || 'CHUIKPAR ENGINEERING CONSULTANCY, LTD.'}
            </Text>
            <View style={styles.quotationType}>
              <Text>{data?.businessType || '澳门 • Engineering Consultancy'}</Text>
            </View>
          </View>
          <View style={styles.headerRight}>
            <Text style={styles.headerRightText}>
              <Text style={styles.headerRightLabel}>编号 NO：</Text>
              {data?.quotationNumber || 'INV-01-0001'}
            </Text>
            <Text style={styles.headerRightText}>
              <Text style={styles.headerRightLabel}>日期 Date：</Text>
              {data?.currentDate || new Date().toLocaleDateString('zh-CN')}
            </Text>
            <Text style={styles.headerRightText}>
              <Text style={styles.headerRightLabel}>版本 REV：</Text>
              {data?.quotationVersion || '1.0'}
            </Text>
          </View>
        </View>

        {/* 标题 */}
        <View style={styles.titleSection}>
          <Text style={styles.title}>报价单 Quotation Sheet</Text>
          <Text style={styles.subtitle}>Official quotation</Text>
        </View>

        {/* 客户信息 */}
        <View style={styles.customerSection}>
          <View style={styles.infoRow}>
            <View style={styles.infoLabel}>
              <Text>客户</Text>
            </View>
            <View style={styles.infoValue}>
              <Text>{data?.clientName || ''}</Text>
            </View>
          </View>

          <View style={styles.twoColumnRow}>
            <View style={styles.twoColumnItem}>
              <View style={styles.infoLabel}>
                <Text>电话号码</Text>
              </View>
              <View style={styles.infoValue}>
                <Text>{data?.phoneNumber || ''}</Text>
              </View>
            </View>
            <View style={styles.twoColumnItem}>
              <View style={styles.infoLabel}>
                <Text>地址</Text>
              </View>
              <View style={styles.infoValue}>
                <Text>{data?.address || ''}</Text>
              </View>
            </View>
          </View>

          <View style={styles.infoRow}>
            <View style={styles.infoLabel}>
              <Text>项目名称</Text>
            </View>
            <View style={styles.infoValue}>
              <Text>{data?.projectName || ''}</Text>
            </View>
          </View>
        </View>

        {/* 项目明细表 */}
        <View style={styles.table}>
          {/* 表头 */}
          <View style={styles.tableHeader}>
            <View style={[styles.tableCellHeader, styles.col1]}>
              <Text>序号</Text>
            </View>
            <View style={[styles.tableCellHeader, styles.col2]}>
              <Text>项目</Text>
            </View>
            <View style={[styles.tableCellHeader, styles.col3]}>
              <Text>数量</Text>
            </View>
            <View style={[styles.tableCellHeader, styles.col4]}>
              <Text>单位</Text>
            </View>
            <View style={[styles.tableCellHeader, styles.col5]}>
              <Text>单价{'\n'}(澳门元)</Text>
            </View>
            <View style={[styles.tableCellHeader, styles.col6]}>
              <Text>价钱总计{'\n'}(澳门元)</Text>
            </View>
          </View>

          {/* 表格内容 */}
          {data?.items?.map((item, index) => {
            return (
              <View key={index} style={styles.tableRow}>
                <View style={[styles.tableCell, styles.col1]}>
                  <Text>{item.sequence || index + 1}</Text>
                </View>
                <View style={[styles.tableCell, styles.col2]}>
                  <Text>{item.project || ''}</Text>
                </View>
                <View style={[styles.tableCell, styles.col3]}>
                  <Text>{item.quantity || ''}</Text>
                </View>
                <View style={[styles.tableCell, styles.col4]}>
                  <Text>{item.unit || ''}</Text>
                </View>
                <View style={[styles.tableCell, styles.col5]}>
                  <Text>{formatNumber(item.unitPrice)}</Text>
                </View>
                <View style={[styles.tableCell, styles.col6]}>
                  <Text>{formatNumber(item.totalPrice)}</Text>
                </View>
              </View>
            )
          })}

          {/* 合计行 */}
          <View style={styles.tableTotalRow}>
            <View style={[styles.tableCell, styles.col1]}>
              <Text></Text>
            </View>
            <View style={[styles.tableCell, styles.col2]}>
              <Text style={{ textAlign: 'center', fontWeight: 'bold' }}>合计</Text>
            </View>
            <View style={[styles.tableCell, styles.col3]}>
              <Text></Text>
            </View>
            <View style={[styles.tableCell, styles.col4]}>
              <Text></Text>
            </View>
            <View style={[styles.tableCell, styles.col5]}>
              <Text></Text>
            </View>
            <View style={[styles.tableCell, styles.col6]}>
              <Text style={{ fontWeight: 'bold' }}>{data?.totalAmount || 'MOP $ 0.00'}</Text>
            </View>
          </View>
        </View>

        {/* 备注 */}
        {data?.notes && data.notes.length > 0 && (
          <View style={styles.notesSection}>
            <Text style={styles.notesTitle}>备注：</Text>
            {data.notes.map((note, index) => (
              <Text key={index} style={styles.notesContent}>{note}</Text>
            ))}
          </View>
        )}

        {/* 签名区域 */}
        <View style={styles.signatureSection}>
          <Text style={styles.signatureTitle}>Signature</Text>
          <View style={styles.signatureRow}>
            <View style={styles.signatureBox}>
              <Text style={styles.signatureLabel}>管理顾问主席签名及确认：</Text>
              {data?.managerSignature ? (
                <Image 
                  src={data.managerSignature} 
                  style={{ 
                    width: '100%', 
                    height: 30, 
                    objectFit: 'contain',
                    marginTop: 3
                  }} 
                />
              ) : (
                <View style={styles.signatureLine}></View>
              )}
            </View>
            <View style={styles.signatureBox}>
              <Text style={styles.signatureLabel}>技术员：</Text>
              {data?.technicianSignature ? (
                <Image 
                  src={data.technicianSignature} 
                  style={{ 
                    width: '100%', 
                    height: 30, 
                    objectFit: 'contain',
                    marginTop: 3
                  }} 
                />
              ) : (
                <View style={styles.signatureLine}></View>
              )}
            </View>
          </View>
          <View style={[styles.signatureRow, { marginTop: 8 }]}>
            <View style={styles.signatureBox}>
              <Text style={styles.signatureLabel}>日期：</Text>
              <View style={styles.signatureLine}>
                <Text style={{ fontSize: 6.5, paddingTop: 2 }}>{data?.managerSignDate || ''}</Text>
              </View>
            </View>
            <View style={styles.signatureBox}>
              <Text style={styles.signatureLabel}>日期：</Text>
              <View style={styles.signatureLine}>
                <Text style={{ fontSize: 6.5, paddingTop: 2 }}>{data?.technicianSignDate || ''}</Text>
              </View>
            </View>
          </View>
        </View>
      </Page>
    </Document>
  )
}

/**
 * 导出报价单为PDF
 * @param {Object} quotationData - 报价单数据
 * @returns {Promise<boolean>} - 是否成功导出
 */
export const exportQuotationPDF = async (quotationData) => {
  try {
    console.log('📄 开始生成PDF...', quotationData)

    if (!quotationData) {
      throw new Error('报价单数据为空')
    }

    // 生成PDF文件
    const blob = await pdf(<QuotationPDF data={quotationData} />).toBlob()
    
    console.log('✅ PDF生成成功，准备下载')

    // 创建下载链接
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // 生成文件名
    const fileName = `报价单_${quotationData.clientName || '客户'}_${quotationData.quotationNumber || Date.now()}.pdf`
    link.download = fileName
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    // 释放URL对象
    setTimeout(() => URL.revokeObjectURL(url), 100)
    
    console.log('✅ PDF下载完成:', fileName)
    return true

  } catch (error) {
    console.error('❌ PDF生成失败:', error)
    alert(`PDF生成失败: ${error.message}\n\n请检查浏览器控制台获取详细信息。`)
    return false
  }
}
