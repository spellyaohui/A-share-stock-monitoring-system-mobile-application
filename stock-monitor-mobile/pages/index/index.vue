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
import { useUserStore } from '../../store/user'

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
@import '../../styles/variables.scss';

.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32rpx;
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
  padding: 48rpx 32rpx;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 32rpx;
  box-shadow: 0 16rpx 48rpx rgba(0, 0, 0, 0.16);
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
  margin-bottom: 48rpx;
}

.logo-icon {
  font-size: 120rpx;
  margin-bottom: 24rpx;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20rpx); }
}

.app-title {
  display: block;
  font-size: 44rpx;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8rpx;
}

.app-subtitle {
  display: block;
  font-size: 24rpx;
  color: #64748b;
}

// 表单区域
.form-section {
  margin-bottom: 48rpx;
}

.input-group {
  margin-bottom: 24rpx;
}

.input-wrapper {
  display: flex;
  align-items: center;
  padding: 0 24rpx;
  height: 100rpx;
  background: #f1f5f9;
  border-radius: 24rpx;
  border: 2rpx solid transparent;
  transition: all 0.25s ease;
}

.input-focus {
  background: #ffffff;
  border-color: #667eea;
  box-shadow: 0 0 0 6rpx rgba(102, 126, 234, 0.15);
}

.input-icon {
  font-size: 40rpx;
  margin-right: 16rpx;
}

.input {
  flex: 1;
  height: 100%;
  font-size: 28rpx;
  color: #1e293b;
}

.placeholder {
  color: #94a3b8;
}

.toggle-password {
  padding: 16rpx;
  font-size: 36rpx;
}

// 登录按钮
.login-btn {
  width: 100%;
  height: 100rpx;
  margin-top: 32rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 24rpx;
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
  font-size: 32rpx;
  font-weight: 600;
  letter-spacing: 8rpx;
}

.loading-spinner {
  width: 36rpx;
  height: 36rpx;
  border: 4rpx solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  margin-right: 16rpx;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

// 底部信息
.footer-section {
  text-align: center;
}

.divider-line {
  display: flex;
  align-items: center;
  margin-bottom: 24rpx;
}

.line {
  flex: 1;
  height: 1rpx;
  background: #e2e8f0;
}

.divider-text {
  padding: 0 24rpx;
  font-size: 22rpx;
  color: #94a3b8;
}

.hint-text {
  font-size: 24rpx;
  color: #64748b;
}

// 版本信息
.version-info {
  position: absolute;
  bottom: 60rpx;
  left: 0;
  right: 0;
  text-align: center;
  
  text {
    font-size: 22rpx;
    color: rgba(255, 255, 255, 0.6);
  }
}

// 暗黑模式适配
@media (prefers-color-scheme: dark) {
  .login-page {
    background: linear-gradient(135deg, #1e1e2e 0%, #313244 100%);
  }
  
  .login-container {
    background: rgba(30, 30, 46, 0.95);
  }
  
  .app-title {
    color: #cdd6f4;
  }
  
  .app-subtitle {
    color: #a6adc8;
  }
  
  .input-wrapper {
    background: #181825;
  }
  
  .input-focus {
    background: #1e1e2e;
    border-color: #89b4fa;
    box-shadow: 0 0 0 6rpx rgba(137, 180, 250, 0.15);
  }
  
  .input {
    color: #cdd6f4;
  }
  
  .placeholder {
    color: #6c7086;
  }
  
  .login-btn {
    background: linear-gradient(135deg, #89b4fa 0%, #b4befe 100%);
  }
  
  .line {
    background: #313244;
  }
  
  .divider-text {
    color: #6c7086;
  }
  
  .hint-text {
    color: #a6adc8;
  }
}
</style>
