/**
 * 应用配置文件
 * 管理应用级别的配置
 */

export const appConfig = {
  // 应用信息
  app: {
    name: 'Omnigence.ai',
    version: '1.0.0',
    description: 'AI报价单生成系统',
  },
  
  // 本地存储配置
  storage: {
    quotationsKey: 'omnigence_quotations',
    userPreferencesKey: 'omnigence_preferences',
    maxStorageSize: 5 * 1024 * 1024, // 5MB
  },
  
  // 报价单配置
  quotation: {
    defaultCompany: {
      name: '港珀工程顾问有限公司',
      nameEn: 'CHUIKPAR ENGINEERING CONSULTANCY, LTD.',
      businessType: '澳门 • Engineering Consultancy',
    },
    defaultCurrency: 'MOP',
    numberPrefix: 'INV',
  },
  
  // UI配置
  ui: {
    theme: 'light',
    language: 'zh-CN',
    dateFormat: 'YYYY/MM/DD',
  },
  
  // 功能开关
  features: {
    enableSearch: true,
    enablePDFExport: true,
    enableAIChat: true,
    enableHistory: true,
  },
}

export default appConfig

