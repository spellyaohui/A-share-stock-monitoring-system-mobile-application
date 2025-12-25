<template>
  <view class="login-page">
    <!-- 背景装饰 -->
    <view class="bg-decoration">
      <view class="circle circle-1"></view>
      <view class="circle circle-2"></view>
      <view class="circle circle-3"></view>
    </view>
    
    <!-- 登录容器 -->
    <view class="login-container">
      <!-- Logo 区域 -->
      <view class="logo-section">
        <view class="logo-icon">📈</view>
        <text class="app-title">股票监测系统</text>
        <text class="app-subtitle">实时监控 · 智能预警 · 把握先机</text>
      </view>
      
      <!-- 登录表单 -->
      <view class="form-section">
        <view class="input-group">
          <view class="input-wrapper" :class="{ 'input-focus': usernameFocus }">
            <view class="input-icon">👤</view>
            <input
              class="input"
              v-model="formData.username"
              placeholder="请输入用户名"
              placeholder-class="placeholder"
              @focus="usernameFocus = true"
              @blur="usernameFocus = false"
            />
          </view>
        </view>
        
        <view class="input-group">
          <view class="input-wrapper" :class="{ 'input-focus': passwordFocus }">
            <view class="input-icon">🔒</view>
            <input
              class="input"
              v-model="formData.password"
              :password="!showPassword"
              placeholder="请输入密码"
              placeholder-class="placeholder"
              @focus="passwordFocus = true"
              @blur="passwordFocus = false"
            />
            <view class="toggle-password" @click="showPassword = !showPassword">
              <text>{{ showPassword ? '🙈' : '👁️' }}</text>
            </view>
          </view>
        </view>
        
        <!-- 登录按钮 -->
        <button 
          class="login-btn" 
          :class="{ 'btn-loading': loading }"
          :disabled="loading"
          @click="handleLogin"
        >
          <view class="btn-content">
            <view v-if="loading" class="loading-spinner"></view>
            <text>{{ loading ? '登录中...' : '登 录' }}</text>
          </view>
        </button>
      </view>
      
      <!-- 底部信息 -->
      <view class="footer-section">
        <view class="divider-line">
          <view class="line"></view>
          <text class="divider-text">默认账号</text>
          <view class="line"></view>
        </view>
        <text class="hint-text">用户名: admin / 密码: admin</text>
      </view>
    </view>
    
    <!-- 版本信息 -->
    <view class="version-info">
      <text>v1.0.0</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

// 表单数据
const formData = reactive({
  username: '',
  password: ''
})

// 状态
const loading = ref(false)
const showPassword = ref(false)
const usernameFocus = ref(false)
const passwordFocus = ref(false)

// 登录处理
async function handleLogin() {
  // 表单验证
  if (!formData.username.trim()) {
    uni.showToast({ title: '请输入用户名', icon: 'none' })
    return
  }
  
  if (!formData.password) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }
  
  loading.value = true
  
  try {
    const success = await userStore.login(formData.username, formData.password)
    
    if (success) {
      uni.showToast({ 
        title: '登录成功', 
        icon: 'success',
        duration: 1500
      })
      
      // 延迟跳转，让用户看到成功提示
      setTimeout(() => {
        uni.reLaunch({ url: '/pages/dashboard/index' })
      }, 1000)
    } else {
      uni.showToast({ 
        title: '登录失败，请检查用户名和密码', 
        icon: 'none',
        duration: 2000
      })
    }
  } catch (error: any) {
    uni.showToast({ 
      title: error.message || '登录失败', 
      icon: 'none',
      duration: 2000
    })
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.login-page {
  min-height: 100vh;
  background: $primary-gradient;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $spacing-lg;
  position: relative;
  overflow: hidden;
}

// 背景装饰
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.circle-1 {
  width: 400rpx;
  height: 400rpx;
  top: -100rpx;
  right: -100rpx;
}

.circle-2 {
  width: 300rpx;
  height: 300rpx;
  bottom: 200rpx;
  left: -150rpx;
}

.circle-3 {
  width: 200rpx;
  height: 200rpx;
  bottom: -50rpx;
  right: 100rpx;
}

// 登录容器
.login-container {
  width: 100%;
  max-width: 680rpx;
  padding: $spacing-xl $spacing-lg;
  background: rgba(255, 255, 255, 0.95);
  border-radius: $radius-xl;
  box-shadow: $shadow-xl;
  backdrop-filter: blur(20rpx);
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(100rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// Logo 区域
.logo-section {
  text-align: center;
  margin-bottom: $spacing-xl;
}

.logo-icon {
  font-size: 120rpx;
  margin-bottom: $spacing-md;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20rpx);
  }
}

.app-title {
  display: block;
  font-size: $font-xl;
  font-weight: $font-bold;
  color: $text-primary;
  margin-bottom: $spacing-xs;
}

.app-subtitle {
  display: block;
  font-size: $font-sm;
  color: $text-secondary;
}

// 表单区域
.form-section {
  margin-bottom: $spacing-xl;
}

.input-group {
  margin-bottom: $spacing-md;
}

.input-wrapper {
  display: flex;
  align-items: center;
  padding: 0 $spacing-md;
  height: 100rpx;
  background: $bg-secondary;
  border-radius: $radius-lg;
  border: 2rpx solid transparent;
  transition: all $transition-normal;
}

.input-focus {
  background: $bg-white;
  border-color: $primary-color;
  box-shadow: 0 0 0 6rpx rgba(102, 126, 234, 0.15);
}

.input-icon {
  font-size: 40rpx;
  margin-right: $spacing-sm;
}

.input {
  flex: 1;
  height: 100%;
  font-size: $font-base;
  color: $text-primary;
}

.placeholder {
  color: $text-muted;
}

.toggle-password {
  padding: $spacing-sm;
  font-size: 36rpx;
}

// 登录按钮
.login-btn {
  width: 100%;
  height: 100rpx;
  margin-top: $spacing-lg;
  background: $primary-gradient;
  border-radius: $radius-lg;
  border: none;
  overflow: hidden;
  position: relative;
  
  &::after {
    border: none;
  }
  
  &:active {
    opacity: 0.9;
    transform: scale(0.98);
  }
}

.btn-loading {
  opacity: 0.8;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #ffffff;
  font-size: $font-md;
  font-weight: $font-semibold;
  letter-spacing: 8rpx;
}

.loading-spinner {
  width: 36rpx;
  height: 36rpx;
  border: 4rpx solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  margin-right: $spacing-sm;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

// 底部信息
.footer-section {
  text-align: center;
}

.divider-line {
  display: flex;
  align-items: center;
  margin-bottom: $spacing-md;
}

.line {
  flex: 1;
  height: 1rpx;
  background: $border-color;
}

.divider-text {
  padding: 0 $spacing-md;
  font-size: $font-xs;
  color: $text-muted;
}

.hint-text {
  font-size: $font-sm;
  color: $text-secondary;
}

// 版本信息
.version-info {
  position: absolute;
  bottom: 60rpx;
  left: 0;
  right: 0;
  text-align: center;
  
  text {
    font-size: $font-xs;
    color: rgba(255, 255, 255, 0.6);
  }
}
</style>
