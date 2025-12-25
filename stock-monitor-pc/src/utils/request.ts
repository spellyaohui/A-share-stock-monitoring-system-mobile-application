import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { useUserStore } from '@/store/user'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // 401 或 403 都视为认证失败
    if (error.response?.status === 401 || error.response?.status === 403) {
      // 只有当前不在登录页面时才清除token并跳转
      const currentPath = window.location.pathname
      if (currentPath !== '/login') {
        // 清空localStorage和store中的token
        localStorage.removeItem('access_token')
        const userStore = useUserStore()
        userStore.token = ''
        userStore.isLoggedIn = false
        userStore.userInfo = null
        router.push('/login')
        ElMessage.error('登录已过期，请重新登录')
      }
    } else {
      ElMessage.error(error.response?.data?.detail || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default request
