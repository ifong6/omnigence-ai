/**
 * 配置统一导出文件
 * 所有组件从这里导入配置
 */

import apiConfig from './api.config'
import appConfig from './app.config'

// 导出所有配置
export { apiConfig, appConfig }

// 默认导出（方便导入）
export default {
  api: apiConfig,
  app: appConfig,
}

