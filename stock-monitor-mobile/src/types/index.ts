// ============================================
// 股票监测系统移动端 - TypeScript 类型定义
// ============================================

// API 响应基础类型
export interface ApiResponse<T = any> {
  code?: number
  data: T
  message?: string
}

// 用户相关类型
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

// 股票基础信息
export interface StockInfo {
  id: number
  code: string
  name: string
  market?: string
  industry?: string
  full_code?: string
}

// 股票实时行情
export interface StockRealtime extends StockInfo {
  price: number
  open: number
  high: number
  low: number
  close: number
  pre_close: number
  volume: number
  amount: number
  change: number
  change_percent: number
  timestamp: string
}

// 监测配置
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

// 创建监测请求
export interface CreateMonitorRequest {
  stock_id: number
  price_min?: number
  price_max?: number
  rise_threshold?: number
  fall_threshold?: number
}

// 更新监测请求
export interface UpdateMonitorRequest {
  price_min?: number
  price_max?: number
  rise_threshold?: number
  fall_threshold?: number
  is_active?: boolean
}

// K线数据
export interface KlineItem {
  date: string
  open: number
  close: number
  high: number
  low: number
  volume: number
  amount?: number
}

export interface KlineData {
  klines: KlineItem[]
  ma?: {
    ma5?: number[]
    ma10?: number[]
    ma20?: number[]
    ma60?: number[]
  }
}

// 市场统计数据
export interface MarketStats {
  total_stocks: number
  up_stocks: number
  down_stocks: number
  flat_stocks: number
  limit_up: number
  limit_down: number
  up_ratio: number
  down_ratio: number
}

// 市场概况数据
export interface MarketOverview {
  market_stats: MarketStats
  top_volume: RankingItem[]
  top_gainers: RankingItem[]
  top_losers: RankingItem[]
}

// 排行榜项目
export interface RankingItem {
  代码: string
  名称: string
  最新价: number
  涨跌幅: number
  涨跌额?: number
  成交量?: number
  成交额?: number
  振幅?: number
  换手率?: number
  市盈率?: number
  市净率?: number
}

// 板块数据
export interface SectorItem {
  板块名称: string
  涨跌幅: number
  上涨家数: number
  下跌家数: number
  领涨股票: string
  领涨涨跌幅?: number
  总市值?: number
}

export interface SectorsData {
  industries: SectorItem[]
  concepts: SectorItem[]
}

// 龙虎榜数据
export interface LhbItem {
  序号: number
  代码: string
  名称: string
  涨跌幅?: number
  上榜次数: number
  龙虎榜净买额: number
  龙虎榜买入额?: number
  龙虎榜卖出额?: number
}

export interface LhbData {
  lhb_data: LhbItem[]
}

// 财务数据
export interface FinancialBasicInfo {
  股票代码: string
  股票名称: string
  最新价: number
  市盈率?: number
  市净率?: number
  换手率?: number
  总市值?: number
  流通市值?: number
  成交额?: number
  行业?: string
  总股本?: number
  流通股?: number
}

export interface FinancialRatios {
  市盈率_动态?: number
  市净率?: number
  换手率?: number
  量比?: number
  振幅?: number
  '60日涨跌幅'?: number
}

export interface FinancialData {
  basic_info?: FinancialBasicInfo
  financial_ratios?: FinancialRatios
}

// 资金流向
export interface FundFlowItem {
  日期: string
  '主力净流入-净额': number
  '主力净流入-净占比': number
  '超大单净流入-净额'?: number
  '大单净流入-净额'?: number
  '中单净流入-净额'?: number
  '小单净流入-净额'?: number
}

export interface FundFlowData {
  fund_flow: FundFlowItem[]
}

// 新闻数据
export interface NewsItem {
  新闻标题: string
  新闻内容?: string
  发布时间: string
  文章来源: string
  新闻链接: string
}

export interface NewsData {
  news: NewsItem[]
}

// 技术指标
export interface TechnicalData {
  technical: {
    ma5?: number
    ma10?: number
    ma20?: number
    ma60?: number
    rsi?: number
    volume_ratio?: number
  }
}

// 通知配置
export interface NotificationConfig {
  email_enabled: boolean
  email_address?: string
  webhook_enabled: boolean
  webhook_url?: string
}

// 通知历史
export interface NotificationHistory {
  id: number
  type: string
  title: string
  content: string
  created_at: string
  is_read: boolean
}
