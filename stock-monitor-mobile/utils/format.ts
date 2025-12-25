// ============================================
// 股票监测系统移动端 - 格式化工具函数
// ============================================

/**
 * 格式化价格
 * @param price 价格数值
 * @param decimals 小数位数，默认 2
 * @returns 格式化后的价格字符串
 */
export function formatPrice(price?: number | null, decimals: number = 2): string {
  if (price === undefined || price === null) return '--'
  return price.toFixed(decimals)
}

/**
 * 格式化涨跌幅
 * @param change 涨跌幅数值（百分比）
 * @param decimals 小数位数，默认 2
 * @returns 格式化后的涨跌幅字符串（带正负号和百分比）
 */
export function formatChange(change?: number | null, decimals: number = 2): string {
  if (change === undefined || change === null) return '--'
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change.toFixed(decimals)}%`
}

/**
 * 格式化涨跌额
 * @param amount 涨跌额数值
 * @param decimals 小数位数，默认 2
 * @returns 格式化后的涨跌额字符串（带正负号）
 */
export function formatChangeAmount(amount?: number | null, decimals: number = 2): string {
  if (amount === undefined || amount === null) return '--'
  const sign = amount >= 0 ? '+' : ''
  return `${sign}${amount.toFixed(decimals)}`
}

/**
 * 格式化成交量
 * @param volume 成交量数值
 * @returns 格式化后的成交量字符串（万/亿）
 */
export function formatVolume(volume?: number | null): string {
  if (volume === undefined || volume === null) return '--'
  
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  }
  if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toString()
}

/**
 * 格式化金额
 * @param amount 金额数值
 * @returns 格式化后的金额字符串（万/亿）
 */
export function formatMoney(amount?: number | null): string {
  if (amount === undefined || amount === null) return '--'
  
  if (Math.abs(amount) >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  }
  if (Math.abs(amount) >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toFixed(2)
}

/**
 * 格式化市值
 * @param value 市值数值
 * @returns 格式化后的市值字符串
 */
export function formatMarketCap(value?: number | null): string {
  if (value === undefined || value === null) return '--'
  
  if (value >= 1000000000000) {
    return (value / 1000000000000).toFixed(2) + '万亿'
  }
  if (value >= 100000000) {
    return (value / 100000000).toFixed(2) + '亿'
  }
  if (value >= 10000) {
    return (value / 10000).toFixed(2) + '万'
  }
  return value.toFixed(2)
}

/**
 * 格式化百分比
 * @param value 百分比数值
 * @param decimals 小数位数，默认 2
 * @returns 格式化后的百分比字符串
 */
export function formatPercent(value?: number | null, decimals: number = 2): string {
  if (value === undefined || value === null) return '--'
  return value.toFixed(decimals) + '%'
}

/**
 * 格式化日期
 * @param date 日期字符串或 Date 对象
 * @param format 格式化模式，默认 'YYYY-MM-DD'
 * @returns 格式化后的日期字符串
 */
export function formatDate(date?: string | Date | null, format: string = 'YYYY-MM-DD'): string {
  if (!date) return '--'
  
  const d = typeof date === 'string' ? new Date(date) : date
  
  if (isNaN(d.getTime())) return '--'
  
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化时间（相对时间）
 * @param date 日期字符串或 Date 对象
 * @returns 相对时间字符串
 */
export function formatRelativeTime(date?: string | Date | null): string {
  if (!date) return '--'
  
  const d = typeof date === 'string' ? new Date(date) : date
  
  if (isNaN(d.getTime())) return '--'
  
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 0) {
    return days === 1 ? '昨天' : `${days}天前`
  }
  if (hours > 0) {
    return `${hours}小时前`
  }
  if (minutes > 0) {
    return `${minutes}分钟前`
  }
  return '刚刚'
}

/**
 * 获取涨跌颜色类名
 * @param change 涨跌幅数值
 * @returns CSS 类名
 */
export function getChangeClass(change?: number | null): string {
  if (change === undefined || change === null) return ''
  return change >= 0 ? 'text-up' : 'text-down'
}

/**
 * 获取涨跌背景颜色类名
 * @param change 涨跌幅数值
 * @returns CSS 类名
 */
export function getChangeBgClass(change?: number | null): string {
  if (change === undefined || change === null) return ''
  return change >= 0 ? 'bg-up' : 'bg-down'
}

/**
 * 判断是否为涨
 * @param change 涨跌幅数值
 * @returns 是否为涨
 */
export function isUp(change?: number | null): boolean {
  return (change ?? 0) >= 0
}

/**
 * 判断是否为跌
 * @param change 涨跌幅数值
 * @returns 是否为跌
 */
export function isDown(change?: number | null): boolean {
  return (change ?? 0) < 0
}

/**
 * 格式化股票代码（添加市场前缀）
 * @param code 股票代码
 * @returns 带市场前缀的股票代码
 */
export function formatStockCode(code?: string | null): string {
  if (!code) return '--'
  
  // 已经有前缀的直接返回
  if (code.includes('.')) return code
  
  // 根据代码判断市场
  if (code.startsWith('6')) {
    return `${code}.SH`
  }
  if (code.startsWith('0') || code.startsWith('3')) {
    return `${code}.SZ`
  }
  if (code.startsWith('8') || code.startsWith('4')) {
    return `${code}.BJ`
  }
  
  return code
}

/**
 * 数字千分位格式化
 * @param num 数字
 * @returns 千分位格式化后的字符串
 */
export function formatThousands(num?: number | null): string {
  if (num === undefined || num === null) return '--'
  return num.toLocaleString('zh-CN')
}
