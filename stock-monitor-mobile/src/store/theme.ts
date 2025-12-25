// ============================================
// 股票监测系统移动端 - 主题状态管理
// ============================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 主题类型
export type ThemeMode = 'light' | 'dark' | 'auto'

export const useThemeStore = defineStore('theme', () => {
  // 状态
  const mode = ref<ThemeMode>('auto')  // 主题模式：light/dark/auto
  const systemTheme = ref<'light' | 'dark'>('light')  // 系统当前主题
  
  // 计算当前实际主题
  const currentTheme = computed(() => {
    if (mode.value === 'auto') {
      return systemTheme.value
    }
    return mode.value
  })
  
  // 是否为暗色主题
  const isDark = computed(() => currentTheme.value === 'dark')
  
  /**
   * 初始化主题
   */
  function initTheme(): void {
    // 从本地存储读取主题设置
    const savedMode = uni.getStorageSync('theme_mode') as ThemeMode
    if (savedMode) {
      mode.value = savedMode
    }
    
    // 获取系统主题
    updateSystemTheme()
    
    // 监听系统主题变化
    // #ifndef H5
    // 非 H5 平台使用 uni.onThemeChange
    try {
      uni.onThemeChange((result: { theme: string }) => {
        console.log('系统主题变化:', result.theme)
        systemTheme.value = result.theme as 'light' | 'dark'
        applyTheme()
      })
    } catch (e) {
      console.log('onThemeChange 不支持')
    }
    // #endif
    
    // 初始应用主题
    applyTheme()
  }
  
  /**
   * 更新系统主题
   */
  function updateSystemTheme(): void {
    try {
      const info = uni.getSystemInfoSync()
      // @ts-ignore - theme 属性在开启 darkmode 后才有
      if (info.theme) {
        // @ts-ignore
        systemTheme.value = info.theme as 'light' | 'dark'
        console.log('当前系统主题（uni API）:', systemTheme.value)
      } else {
        // H5 平台使用 matchMedia 检测
        // #ifdef H5
        if (typeof window !== 'undefined' && window.matchMedia) {
          const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)')
          systemTheme.value = darkModeQuery.matches ? 'dark' : 'light'
          console.log('当前系统主题（matchMedia）:', systemTheme.value)
          
          // 监听系统主题变化
          darkModeQuery.addEventListener('change', (e) => {
            console.log('系统主题变化（matchMedia）:', e.matches ? 'dark' : 'light')
            systemTheme.value = e.matches ? 'dark' : 'light'
            applyTheme()
          })
        }
        // #endif
      }
    } catch (e) {
      console.error('获取系统主题失败:', e)
      // 降级处理：H5 使用 matchMedia
      // #ifdef H5
      if (typeof window !== 'undefined' && window.matchMedia) {
        const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)')
        systemTheme.value = darkModeQuery.matches ? 'dark' : 'light'
        console.log('当前系统主题（降级 matchMedia）:', systemTheme.value)
      }
      // #endif
    }
  }
  
  /**
   * 应用主题到页面
   */
  function applyTheme(): void {
    const theme = currentTheme.value
    console.log('应用主题:', theme)
    
    // 设置导航栏样式
    try {
      uni.setNavigationBarColor({
        frontColor: '#ffffff',
        backgroundColor: theme === 'dark' ? '#1e1e2e' : '#667eea',
        animation: {
          duration: 300,
          timingFunc: 'easeIn'
        }
      })
    } catch (e) {
      // 某些页面可能不支持
    }
    
    // 设置 TabBar 样式
    try {
      if (theme === 'dark') {
        uni.setTabBarStyle({
          color: '#6c7086',
          selectedColor: '#89b4fa',
          backgroundColor: '#1e1e2e',
          borderStyle: 'black'
        })
      } else {
        uni.setTabBarStyle({
          color: '#94a3b8',
          selectedColor: '#667eea',
          backgroundColor: '#ffffff',
          borderStyle: 'white'
        })
      }
    } catch (e) {
      // 某些页面可能没有 TabBar
    }
  }
  
  /**
   * 设置主题模式
   */
  function setMode(newMode: ThemeMode): void {
    mode.value = newMode
    uni.setStorageSync('theme_mode', newMode)
    
    // 应用新主题
    applyTheme()
    
    uni.showToast({
      title: newMode === 'auto' ? '跟随系统' : (newMode === 'dark' ? '深色模式' : '浅色模式'),
      icon: 'none',
      duration: 1500
    })
  }
  
  /**
   * 切换主题
   */
  function toggleTheme(): void {
    const modes: ThemeMode[] = ['light', 'dark', 'auto']
    const currentIndex = modes.indexOf(mode.value)
    const nextIndex = (currentIndex + 1) % modes.length
    setMode(modes[nextIndex])
  }
  
  /**
   * 获取主题模式文本
   */
  function getModeText(): string {
    switch (mode.value) {
      case 'light': return '浅色模式'
      case 'dark': return '深色模式'
      case 'auto': return '跟随系统'
      default: return '跟随系统'
    }
  }
  
  /**
   * 获取主题图标
   */
  function getModeIcon(): string {
    switch (mode.value) {
      case 'light': return '☀️'
      case 'dark': return '🌙'
      case 'auto': return '🔄'
      default: return '🔄'
    }
  }
  
  return {
    // 状态
    mode,
    systemTheme,
    currentTheme,
    isDark,
    
    // 方法
    initTheme,
    updateSystemTheme,
    applyTheme,
    setMode,
    toggleTheme,
    getModeText,
    getModeIcon
  }
})
