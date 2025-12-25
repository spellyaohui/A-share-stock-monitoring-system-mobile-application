import request from '@/utils/request'
import type { ApiResponse, StockInfo, StockRealtime, MonitorConfig, KlineData, LoginResponse, User } from '@/types'

export const api = {
  auth: {
    login(username: string, password: string) {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)
      return request.post<any, LoginResponse>('/auth/login', formData)
    },
    register(username: string, password: string, email?: string) {
      return request.post<any, User>('/auth/register', { username, password, email })
    },
    getMe() {
      return request.get<any, User>('/auth/me')
    }
  },

  stocks: {
    search(keyword: string, type?: string) {
      return request.get<any, StockInfo[]>('/stocks/search', { params: { q: keyword, type } })
    },
    getDetail(id: number) {
      return request.get<any, StockInfo>(`/stocks/${id}`)
    },
    getRealtime(id: number) {
      return request.get<any, StockRealtime>(`/stocks/${id}/realtime`)
    },
    getDaily(id: number, start?: string, end?: string) {
      return request.get<any, any[]>(`/stocks/${id}/daily`, { params: { start, end } })
    },
    // 统一使用 stocks 路由的 kline 接口
    getKline(id: number, period = 'day', limit = 200) {
      return request.get<any, any>(`/stocks/${id}/kline`, { params: { type: period, limit } })
    },
    getIndicators(id: number, indicator = 'ma') {
      return request.get<any, any>(`/stocks/${id}/indicators`, { params: { indicator } })
    }
  },

  monitors: {
    getList() {
      return request.get<any, MonitorConfig[]>('/monitors/')
    },
    create(data: Omit<MonitorConfig, 'id' | 'created_at' | 'stock' | 'current_price' | 'change'>) {
      return request.post<any, MonitorConfig>('/monitors/', data)
    },
    update(id: number, data: Partial<MonitorConfig>) {
      return request.put<any, MonitorConfig>(`/monitors/${id}`, data)
    },
    delete(id: number) {
      return request.delete<any, void>(`/monitors/${id}`)
    }
  },

  // charts 接口已废弃，保留用于向后兼容，建议使用 stocks 接口
  charts: {
    /** @deprecated 请使用 api.stocks.getKline */
    getKline(id: number, period = 'daily', limit = 200) {
      return request.get<any, any>(`/charts/kline/${id}`, { params: { period, limit } })
    },
    /** @deprecated 请使用 api.stocks.getIndicators */
    getIndicators(id: number, indicator = 'ma') {
      return request.get<any, any>(`/charts/indicators/${id}`, { params: { indicator } })
    }
  },

  // 增强版接口
  enhanced: {
    getMarketOverview() {
      return request.get<any, any>('/enhanced/market/overview')
    },
    getHotStocks() {
      return request.get<any, any>('/enhanced/market/hot_stocks')
    },
    getSectors() {
      return request.get<any, any>('/enhanced/market/sectors')
    },
    getStockFinancial(code: string) {
      return request.get<any, any>(`/enhanced/stocks/${code}/financial`)
    },
    getStockTechnical(code: string) {
      return request.get<any, any>(`/enhanced/stocks/${code}/technical`)
    },
    getStockNews(code: string, limit = 10) {
      return request.get<any, any>(`/enhanced/stocks/${code}/news`, { params: { limit } })
    },
    getStockFundFlow(code: string) {
      return request.get<any, any>(`/enhanced/stocks/${code}/fund_flow`)
    }
  },

  notifications: {
    getConfig() {
      return request.get<any, any>('/notifications/config')
    },
    updateConfig(data: any) {
      return request.put<any, void>('/notifications/config', data)
    },
    getHistory(limit = 50) {
      return request.get<any, any[]>('/notifications/history', { params: { limit } })
    }
  }
}
