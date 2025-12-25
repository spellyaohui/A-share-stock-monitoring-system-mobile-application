// ============================================
// 股票监测系统移动端 - 用户状态管理
// ============================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api'
import { isLoggedIn, clearToken } from '../utils/request'
import type { User } from '../types'

export const useUserStore = defineStore('user', () => {
  // 状态
  const userInfo = ref<User | null>(null)
  const loading = ref(false)
  
  // 计算属性
  const isAuthenticated = computed(() => isLoggedIn())
  const username = computed(() => userInfo.value?.username || '')
  const userId = computed(() => userInfo.value?.id || 0)
  
  /**
   * 用户登录
   */
  async function login(username: string, password: string): Promise<boolean> {
    loading.value = true
    try {
      await authApi.login(username, password)
      // 登录成功后获取用户信息
      await fetchUserInfo()
      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 获取用户信息
   */
  async function fetchUserInfo(): Promise<boolean> {
    if (!isLoggedIn()) {
      return false
    }
    
    try {
      const user = await authApi.getMe()
      userInfo.value = user
      return true
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果获取用户信息失败，可能是 token 无效
      logout()
      return false
    }
  }
  
  /**
   * 退出登录
   */
  function logout(): void {
    userInfo.value = null
    clearToken()
  }
  
  /**
   * 检查登录状态
   * 用于应用启动时检查
   */
  async function checkAuth(): Promise<boolean> {
    if (!isLoggedIn()) {
      return false
    }
    
    // 尝试获取用户信息来验证 token 是否有效
    return await fetchUserInfo()
  }
  
  /**
   * 初始化用户状态
   * 在应用启动时调用
   */
  async function init(): Promise<void> {
    if (isLoggedIn()) {
      await fetchUserInfo()
    }
  }
  
  return {
    // 状态
    userInfo,
    loading,
    
    // 计算属性
    isAuthenticated,
    username,
    userId,
    
    // 方法
    login,
    logout,
    fetchUserInfo,
    checkAuth,
    init
  }
})
