// ============================================
// 股票监测系统移动端 - API 接口定义
// ============================================

import { http, setToken, clearToken } from '../utils/request'
import type {
  LoginResponse,
  User,
  StockInfo,
  StockRealtime,
  MonitorConfig,
  CreateMonitorRequest,
  UpdateMonitorRequest,
  KlineData,
  MarketOverview,
  SectorsData,
  LhbData,
  FinancialData,
  FundFlowData,
  NewsData,
  TechnicalData,
  NotificationConfig,
  NotificationHistory
} from '../types'

/**
 * 认证相关接口
 */
export const authApi = {
  /**
   * 用户登录
   */
  async login(username: string, password: string): Promise<LoginResponse> {
    const res = await http.postForm<LoginResponse>('/auth/login', { username, password })
    if (res.access_token) {
      setToken(res.access_token)
    }
    return res
  },
  
  /**
   * 获取当前用户信息
   */
  getMe(): Promise<User> {
    return http.get<User>('/auth/me')
  },
  
  /**
   * 用户注册
   */
  register(username: string, password: string, email?: string): Promise<User> {
    return http.post<User>('/auth/register', { username, password, email })
  },
  
  /**
   * 退出登录
   */
  logout(): void {
    clearToken()
  }
}

/**
 * 股票相关接口
 */
export const stockApi = {
  /**
   * 搜索股票
   */
  search(keyword: string, type?: string): Promise<StockInfo[]> {
    return http.get<StockInfo[]>('/stocks/search', { q: keyword, type })
  },
  
  /**
   * 获取股票详情
   */
  getDetail(id: number): Promise<StockInfo> {
    return http.get<StockInfo>(`/stocks/${id}`)
  },
  
  /**
   * 获取股票实时行情
   */
  getRealtime(id: number): Promise<StockRealtime> {
    return http.get<StockRealtime>(`/stocks/${id}/realtime`)
  },
  
  /**
   * 获取 K 线数据
   * @param id 股票 ID
   * @param period 周期：day | week | month
   * @param limit 数据条数
   */
  getKline(id: number, period: string = 'day', limit: number = 200): Promise<KlineData> {
    return http.get<KlineData>(`/stocks/${id}/kline`, { type: period, limit })
  },
  
  /**
   * 获取技术指标
   */
  getIndicators(id: number, indicator: string = 'ma'): Promise<any> {
    return http.get<any>(`/stocks/${id}/indicators`, { indicator })
  },
  
  /**
   * 获取五档盘口数据
   */
  getBidAsk(id: number): Promise<any> {
    return http.get<any>(`/stocks/${id}/bid-ask`)
  },
  
  /**
   * 获取分钟 K 线数据
   * @param id 股票 ID
   * @param period 分钟周期：1 | 5 | 15 | 30 | 60
   * @param limit 数据条数
   */
  getMinuteKline(id: number, period: string = '5', limit: number = 100): Promise<any> {
    return http.get<any>(`/stocks/${id}/kline-minute`, { period, limit })
  },
  
  /**
   * 获取热门股票排名
   */
  getHotRank(limit: number = 50): Promise<any> {
    return http.get<any>('/stocks/market/hot-rank', { limit })
  },
  
  /**
   * 获取热门关键词
   */
  getHotKeywords(): Promise<any> {
    return http.get<any>('/stocks/market/hot-keywords')
  }
}

/**
 * 监测相关接口
 */
export const monitorApi = {
  /**
   * 获取监测列表
   */
  getList(): Promise<MonitorConfig[]> {
    return http.get<MonitorConfig[]>('/monitors/')
  },
  
  /**
   * 创建监测
   */
  create(data: CreateMonitorRequest): Promise<MonitorConfig> {
    return http.post<MonitorConfig>('/monitors/', data)
  },
  
  /**
   * 更新监测
   */
  update(id: number, data: UpdateMonitorRequest): Promise<MonitorConfig> {
    return http.put<MonitorConfig>(`/monitors/${id}/`, data)
  },
  
  /**
   * 删除监测
   */
  delete(id: number): Promise<void> {
    return http.delete<void>(`/monitors/${id}/`)
  }
}

/**
 * 增强版市场数据接口
 */
export const enhancedApi = {
  /**
   * 获取市场概况
   */
  getMarketOverview(): Promise<MarketOverview> {
    return http.get<MarketOverview>('/enhanced/market/overview')
  },
  
  /**
   * 获取热门股票
   */
  getHotStocks(): Promise<any> {
    return http.get<any>('/enhanced/market/hot_stocks')
  },
  
  /**
   * 获取板块数据
   */
  getSectors(): Promise<SectorsData> {
    return http.get<SectorsData>('/enhanced/market/sectors')
  },
  
  /**
   * 获取龙虎榜数据
   */
  getLhb(): Promise<LhbData> {
    return http.get<LhbData>('/enhanced/market/lhb')
  },
  
  /**
   * 获取股票财务数据
   */
  getStockFinancial(code: string): Promise<FinancialData> {
    return http.get<FinancialData>(`/enhanced/stocks/${code}/financial`)
  },
  
  /**
   * 获取股票技术指标
   */
  getStockTechnical(code: string): Promise<TechnicalData> {
    return http.get<TechnicalData>(`/enhanced/stocks/${code}/technical`)
  },
  
  /**
   * 获取股票新闻
   */
  getStockNews(code: string, limit: number = 10): Promise<NewsData> {
    return http.get<NewsData>(`/enhanced/stocks/${code}/news`, { limit })
  },
  
  /**
   * 获取股票资金流向
   */
  getStockFundFlow(code: string): Promise<FundFlowData> {
    return http.get<FundFlowData>(`/enhanced/stocks/${code}/fund_flow`)
  }
}

/**
 * 实时监测接口 - 专门用于监测股票的实时数据
 * 特点：10秒短缓存，只获取监测的股票
 */
export const realtimeApi = {
  /**
   * 获取用户监测的股票实时数据
   * 包含实时价格和预警状态
   */
  getRealtimeMonitors(): Promise<any> {
    return http.get<any>('/realtime/monitors')
  },
  
  /**
   * 获取单只股票的实时行情
   */
  getRealtimeQuote(code: string): Promise<any> {
    return http.get<any>(`/realtime/quote/${code}`)
  },
  
  /**
   * 获取实时监测服务状态
   */
  getRealtimeStatus(): Promise<any> {
    return http.get<any>('/realtime/status')
  }
}

/**
 * 通知相关接口
 */
export const notificationApi = {
  /**
   * 获取通知配置
   */
  getConfig(): Promise<NotificationConfig> {
    return http.get<NotificationConfig>('/notifications/config')
  },
  
  /**
   * 更新通知配置
   */
  updateConfig(data: Partial<NotificationConfig>): Promise<void> {
    return http.put<void>('/notifications/config', data)
  },
  
  /**
   * 获取通知历史
   */
  getHistory(limit: number = 50): Promise<NotificationHistory[]> {
    return http.get<NotificationHistory[]>('/notifications/history', { limit })
  }
}

/**
 * 统一导出所有 API
 */
export const api = {
  auth: authApi,
  stocks: stockApi,
  monitors: monitorApi,
  enhanced: enhancedApi,
  realtime: realtimeApi,
  notifications: notificationApi
}

export default api
