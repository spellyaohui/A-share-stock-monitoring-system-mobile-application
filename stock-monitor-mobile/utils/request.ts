// ============================================
// 股票监测系统移动端 - HTTP 请求封装
// ============================================

// 获取 API 基础地址
function getBaseUrl(): string {
  // #ifdef H5
  // H5 环境使用相对路径，通过 vite 代理
  return '/api'
  // #endif
  
  // #ifdef APP-PLUS
  // APP 环境使用完整地址
  // 开发时使用本机 IP，生产环境替换为实际服务器地址
  return 'http://192.168.1.141:8000/api'  // 你的电脑局域网 IP
  // #endif
  
  // #ifdef MP-WEIXIN
  // 小程序环境
  return 'https://your-domain.com/api'
  // #endif
  
  // 默认返回
  // @ts-ignore
  return import.meta.env?.DEV ? '/api' : 'https://your-domain.com/api'
}

// API 基础地址
const BASE_URL = getBaseUrl()

// 请求配置接口
interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  params?: Record<string, any>
  header?: Record<string, string>
  showLoading?: boolean
  showError?: boolean
}

// 响应接口
interface Response<T = any> {
  statusCode: number
  data: T
  header: Record<string, string>
}

/**
 * 获取存储的 Token
 */
function getToken(): string {
  return uni.getStorageSync('access_token') || ''
}

/**
 * 设置 Token
 */
export function setToken(token: string): void {
  uni.setStorageSync('access_token', token)
}

/**
 * 清除 Token
 */
export function clearToken(): void {
  uni.removeStorageSync('access_token')
}

/**
 * 检查是否已登录
 */
export function isLoggedIn(): boolean {
  return !!getToken()
}

// 标记是否正在跳转登录页，避免重复跳转
let isRedirectingToLogin = false

/**
 * 处理错误响应
 */
function handleError(statusCode: number, data: any): void {
  let message = '请求失败'
  
  switch (statusCode) {
    case 400:
      message = data?.detail || '请求参数错误'
      break
    case 401:
      message = '登录已过期，请重新登录'
      clearToken()
      // 避免重复跳转
      if (!isRedirectingToLogin) {
        isRedirectingToLogin = true
        // 延迟跳转，让用户看到提示
        setTimeout(() => {
          uni.reLaunch({ 
            url: '/pages/index/index',
            complete: () => {
              // 跳转完成后重置标记
              setTimeout(() => {
                isRedirectingToLogin = false
              }, 1000)
            }
          })
        }, 1500)
      }
      break
    case 403:
      message = '没有权限访问'
      break
    case 404:
      message = '请求的资源不存在'
      break
    case 422:
      message = data?.detail?.[0]?.msg || '数据验证失败'
      break
    case 500:
      message = '服务器内部错误'
      break
    case 502:
    case 503:
    case 504:
      message = '服务器暂时不可用，请稍后重试'
      break
    default:
      message = data?.detail || data?.message || '网络请求失败'
  }
  
  // 401 时只显示一次提示
  if (statusCode !== 401 || !isRedirectingToLogin) {
    uni.showToast({
      title: message,
      icon: 'none',
      duration: 2000
    })
  }
}

/**
 * 处理网络错误
 */
function handleNetworkError(): void {
  uni.showToast({
    title: '网络连接失败，请检查网络设置',
    icon: 'none',
    duration: 2000
  })
}

/**
 * 构建完整 URL（处理查询参数）
 */
function buildUrl(url: string, params?: Record<string, any>): string {
  if (!params) return url
  
  const queryString = Object.entries(params)
    .filter(([_, value]) => value !== undefined && value !== null && value !== '')
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&')
  
  if (!queryString) return url
  
  return url.includes('?') ? `${url}&${queryString}` : `${url}?${queryString}`
}

/**
 * 核心请求函数
 */
function request<T = any>(options: RequestOptions): Promise<T> {
  const {
    url,
    method = 'GET',
    data,
    params,
    header = {},
    showLoading = false,
    showError = true
  } = options
  
  const token = getToken()
  const fullUrl = BASE_URL + buildUrl(url, params)
  
  // 显示加载提示
  if (showLoading) {
    uni.showLoading({ title: '加载中...', mask: true })
  }
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: fullUrl,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...header
      },
      success: (res: Response<T>) => {
        if (showLoading) {
          uni.hideLoading()
        }
        
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          if (showError) {
            handleError(res.statusCode, res.data)
          }
          reject({
            statusCode: res.statusCode,
            data: res.data,
            message: (res.data as any)?.detail || '请求失败'
          })
        }
      },
      fail: (err) => {
        if (showLoading) {
          uni.hideLoading()
        }
        
        if (showError) {
          handleNetworkError()
        }
        
        reject({
          statusCode: 0,
          data: null,
          message: err.errMsg || '网络请求失败'
        })
      }
    })
  })
}

/**
 * 表单数据请求（用于登录等）
 */
function requestForm<T = any>(url: string, data: Record<string, any>): Promise<T> {
  const token = getToken()
  const fullUrl = BASE_URL + url
  
  // 构建 form-urlencoded 数据
  const formData = Object.entries(data)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&')
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: fullUrl,
      method: 'POST',
      data: formData,
      header: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res: Response<T>) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          handleError(res.statusCode, res.data)
          reject({
            statusCode: res.statusCode,
            data: res.data,
            message: (res.data as any)?.detail || '请求失败'
          })
        }
      },
      fail: (err) => {
        handleNetworkError()
        reject({
          statusCode: 0,
          data: null,
          message: err.errMsg || '网络请求失败'
        })
      }
    })
  })
}

/**
 * API 请求方法封装
 */
export const http = {
  /**
   * GET 请求
   */
  get<T = any>(url: string, params?: Record<string, any>, options?: Partial<RequestOptions>): Promise<T> {
    return request<T>({ url, method: 'GET', params, ...options })
  },
  
  /**
   * POST 请求
   */
  post<T = any>(url: string, data?: any, options?: Partial<RequestOptions>): Promise<T> {
    return request<T>({ url, method: 'POST', data, ...options })
  },
  
  /**
   * PUT 请求
   */
  put<T = any>(url: string, data?: any, options?: Partial<RequestOptions>): Promise<T> {
    return request<T>({ url, method: 'PUT', data, ...options })
  },
  
  /**
   * DELETE 请求
   */
  delete<T = any>(url: string, options?: Partial<RequestOptions>): Promise<T> {
    return request<T>({ url, method: 'DELETE', ...options })
  },
  
  /**
   * 表单 POST 请求
   */
  postForm<T = any>(url: string, data: Record<string, any>): Promise<T> {
    return requestForm<T>(url, data)
  }
}

// 导出旧版 API 兼容
export const api = {
  get: http.get,
  post: http.post,
  put: http.put,
  delete: http.delete
}

export default http
