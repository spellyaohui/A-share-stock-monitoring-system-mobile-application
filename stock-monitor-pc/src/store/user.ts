import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api'
import type { User } from '@/types'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('access_token') || '')
  const userInfo = ref<User | null>(null)
  const isLoggedIn = ref<boolean>(!!token.value)

  async function login(username: string, password: string) {
    try {
      const res = await api.auth.login(username, password)
      localStorage.setItem('access_token', res.access_token)
      token.value = res.access_token
      isLoggedIn.value = true
      await fetchUserInfo()
      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  async function fetchUserInfo() {
    try {
      const res = await api.auth.getMe()
      userInfo.value = res
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 不要在这里清除登录状态，让调用者决定如何处理
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    isLoggedIn.value = false
    localStorage.removeItem('access_token')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    login,
    fetchUserInfo,
    logout
  }
})
