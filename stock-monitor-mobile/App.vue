<template>
  <view />
</template>

<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useUserStore } from './store/user'
import { useThemeStore } from './store/theme'
import { isLoggedIn } from './utils/request'

onLaunch(async () => {
  console.log('App Launch')
  
  // 初始化主题（跟随系统）
  const themeStore = useThemeStore()
  themeStore.initTheme()
  
  // 检查登录状态
  if (isLoggedIn()) {
    console.log('检测到已登录，验证 token...')
    const userStore = useUserStore()
    
    try {
      // 尝试获取用户信息来验证 token 是否有效
      const isValid = await userStore.checkAuth()
      
      if (isValid) {
        console.log('Token 有效，跳转到主页')
        // Token 有效，跳转到主页
        uni.reLaunch({ url: '/pages/dashboard/index' })
      } else {
        console.log('Token 无效，停留在登录页')
      }
    } catch (error) {
      console.error('验证登录状态失败:', error)
    }
  } else {
    console.log('未登录，显示登录页')
  }
})

onShow(() => {
  console.log('App Show')
  // 每次显示时重新应用主题（处理从后台返回的情况）
  const themeStore = useThemeStore()
  themeStore.applyTheme()
})

onHide(() => {
  console.log('App Hide')
})
</script>

<style lang="scss">
@import './styles/variables.scss';
@import './styles/common.scss';

page {
  background-color: var(--bg-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: var(--text-primary);
  transition: background-color 0.3s ease, color 0.3s ease;
}

// 全局涨跌颜色
.text-up {
  color: var(--up-color) !important;
}

.text-down {
  color: var(--down-color) !important;
}

// 隐藏滚动条
::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}
</style>
