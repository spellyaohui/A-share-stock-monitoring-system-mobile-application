export interface ApiResponse<T = any> {
  data: T
}

export interface StockInfo {
  id: number
  code: string
  name: string
  market?: string
  industry?: string
  full_code?: string
}

export interface StockRealtime extends StockInfo {
  price: number
  open: number
  high: number
  low: number
  close: number
  pre_close: number  // 修改字段名
  volume: number
  amount: number
  change: number
  change_percent: number  // 添加涨跌幅字段
  timestamp: string
}

export interface MonitorConfig {
  id?: number
  stock_id: number
  price_min?: number
  price_max?: number
  rise_threshold?: number
  fall_threshold?: number
  is_active?: boolean
  created_at?: string
  stock?: StockInfo
  current_price?: number
  change?: number
}

export interface KlineData {
  dates: string[]
  data: [number, number, number, number][]
  volumes: number[]
  ma?: {
    ma5?: number[]
    ma10?: number[]
    ma20?: number[]
    ma60?: number[]
  }
}

export interface User {
  id: number
  username: string
  email?: string
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

// 五档盘口数据
export interface BidAskItem {
  price: number
  volume: number
}

export interface BidAskData {
  code: string
  timestamp: string
  bids: BidAskItem[]  // 买盘（买1-买5）
  asks: BidAskItem[]  // 卖盘（卖1-卖5）
}

// 分钟K线数据
export interface MinuteKlineItem {
  time: string
  open: number
  close: number
  high: number
  low: number
  volume: number
  amount: number
  latest_price?: number
}

export interface MinuteKlineResponse {
  klines: MinuteKlineItem[]
  period: string
  total: number
}

// 热门股票
export interface HotStockItem {
  rank: number
  code: string
  name: string
  price: number
  change_percent: number
  rank_change: number  // 排名变化
}

export interface HotStockResponse {
  list: HotStockItem[]
  total: number
}

// 热门关键词
export interface HotKeywordItem {
  keyword: string
  heat: number
  related_stocks: string
}

export interface HotKeywordResponse {
  list: HotKeywordItem[]
  total: number
}
