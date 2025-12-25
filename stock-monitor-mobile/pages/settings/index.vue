<template>
  <view class="settings-page">
    <!-- 用户信息卡片 -->
    <view class="user-card">
      <view class="user-avatar">
        <text class="avatar-text">{{ avatarText }}</text>
      </view>
      <view class="user-info">
        <text class="user-name">{{ userStore.userInfo?.username || '未登录' }}</text>
        <text class="user-role">普通用户</text>
      </view>
      <view class="user-badge">
        <text class="badge-icon">✓</text>
        <text class="badge-text">已认证</text>
      </view>
    </view>

    <!-- 通知设置 -->
    <view class="settings-section">
      <view class="section-header">
        <text class="section-icon">🔔</text>
        <text class="section-title">通知设置</text>
      </view>
      
      <view class="setting-item">
        <view class="setting-left">
          <text class="setting-label">启用通知</text>
          <text class="setting-desc">开启后将推送监测预警</text>
        </view>
        <switch 
          :checked="configForm.is_enabled" 
          @change="onEnabledChange" 
          color="#667eea" 
        />
      </view>
      
      <view class="setting-item" v-if="configForm.is_enabled">
        <view class="setting-left">
          <text class="setting-label">Webhook 地址</text>
        </view>
      </view>
      <view class="input-wrapper" v-if="configForm.is_enabled">
        <input
          class="setting-input"
          v-model="configForm.api_url"
          placeholder="请输入 Webhook 回调地址"
          @blur="saveConfig"
        />
      </view>
    </view>

    <!-- 通知历史 -->
    <view class="settings-section">
      <view class="section-header">
        <text class="section-icon">📋</text>
        <text class="section-title">通知历史</text>
        <text class="section-badge" v-if="history.length > 0">{{ history.length }}</text>
      </view>
      
      <scroll-view class="history-list" scroll-y v-if="history.length > 0">
        <view class="history-item" v-for="item in history" :key="item.id">
          <view class="history-icon" :class="{ sent: item.is_sent }">
            <text>{{ item.is_sent ? '✓' : '!' }}</text>
          </view>
          <view class="history-content">
            <text class="history-text">{{ item.content }}</text>
            <view class="history-meta">
              <text class="history-time">{{ formatTime(item.created_at) }}</text>
              <view class="history-status" :class="{ sent: item.is_sent }">
                {{ item.is_sent ? '已发送' : '待发送' }}
              </view>
            </view>
          </view>
        </view>
      </scroll-view>
      
      <view class="empty-history" v-else>
        <text class="empty-icon">📭</text>
        <text class="empty-text">暂无通知记录</text>
      </view>
    </view>

    <!-- 关于应用 -->
    <view class="settings-section">
      <view class="section-header">
        <text class="section-icon">ℹ️</text>
        <text class="section-title">关于应用</text>
      </view>
      
      <view class="about-item">
        <text class="about-label">应用名称</text>
        <text class="about-value">股票监测系统</text>
      </view>
      <view class="about-item">
        <text class="about-label">版本号</text>
        <text class="about-value">v{{ appVersion }}</text>
      </view>
      <view class="about-item">
        <text class="about-label">数据来源</text>
        <text class="about-value">AkShare</text>
      </view>
      <!-- #ifdef APP-PLUS -->
      <view class="about-item clickable" @click="handleCheckUpdate">
        <text class="about-label">检查更新</text>
        <view class="setting-right">
          <text class="about-value">{{ checkingUpdate ? '检查中...' : '点击检查' }}</text>
          <text class="arrow-icon">›</text>
        </view>
      </view>
      <!-- #endif -->
    </view>

    <!-- 退出登录 -->
    <view class="logout-section">
      <view class="logout-btn" @click="handleLogout">
        <text class="logout-icon">🚪</text>
        <text class="logout-text">退出登录</text>
      </view>
    </view>
    
    <!-- 底部版权 -->
    <view class="footer">
      <text class="footer-text">© 2024 股票监测系统</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../../store/user'
import { notificationApi } from '../../api'
// 导入升级中心检查更新方法
// #ifdef APP-PLUS
import checkUpdate from '@/uni_modules/uni-upgrade-center-app/utils/check-update'
// #endif

const userStore = useUserStore()

// 应用版本号
const appVersion = ref('1.0.0')
// 检查更新状态
const checkingUpdate = ref(false)

// 头像文字
const avatarText = computed(() => {
  const username = userStore.userInfo?.username || ''
  return username.charAt(0).toUpperCase()
})

// 通知配置
const configForm = ref({
  api_url: '',
  is_enabled: false
})

// 通知历史
const history = ref<any[]>([])

onMounted(async () => {
  await Promise.all([loadConfig(), loadHistory()])
  
  // 获取应用版本号
  // #ifdef APP-PLUS
  const systemInfo = uni.getSystemInfoSync()
  appVersion.value = systemInfo.appVersion || '1.0.0'
  // #endif
})

// 加载通知配置
async function loadConfig() {
  try {
    const res = await notificationApi.getConfig()
    configForm.value = {
      api_url: res.api_url || '',
      is_enabled: res.is_enabled || false
    }
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

// 加载通知历史
async function loadHistory() {
  try {
    const res = await notificationApi.getHistory(20)
    history.value = res || []
  } catch (error) {
    console.error('加载历史失败:', error)
  }
}

// 切换通知开关
function onEnabledChange(e: any) {
  configForm.value.is_enabled = e.detail.value
  saveConfig()
}

// 保存配置
async function saveConfig() {
  try {
    await notificationApi.updateConfig(configForm.value)
    uni.showToast({ title: '保存成功', icon: 'success' })
  } catch (error) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  }
}

// 格式化时间
function formatTime(time: string): string {
  if (!time) return ''
  const date = new Date(time)
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${month}-${day} ${hours}:${minutes}`
}

// 手动检查更新
// #ifdef APP-PLUS
async function handleCheckUpdate() {
  if (checkingUpdate.value) return
  
  checkingUpdate.value = true
  try {
    const res = await checkUpdate()
    console.log('检查更新结果:', res)
    // 如果有更新，checkUpdate 内部会自动弹出更新弹窗
  } catch (err: any) {
    // code 为 0 表示已是最新版本
    if (err.code === 0) {
      uni.showToast({ title: '已是最新版本', icon: 'success' })
    } else {
      console.error('检查更新失败:', err)
      uni.showToast({ title: err.message || '检查更新失败', icon: 'none' })
    }
  } finally {
    checkingUpdate.value = false
  }
}
// #endif

// 退出登录
function handleLogout() {
  uni.showModal({
    title: '确认退出',
    content: '确定要退出登录吗？',
    confirmColor: '#667eea',
    success: (res) => {
      if (res.confirm) {
        userStore.logout()
        uni.reLaunch({ url: '/pages/index/index' })
      }
    }
  })
}
</script>


<style lang="scss" scoped>
@import '../../styles/variables.scss';

.settings-page {
  min-height: 100vh;
  background: var(--bg-primary);
  padding: $spacing-lg;
  padding-bottom: calc($tabbar-height + $safe-area-bottom + 100rpx);
}

// 用户卡片
.user-card {
  display: flex;
  align-items: center;
  padding: $spacing-xl;
  background: $primary-gradient;
  border-radius: $radius-xl;
  margin-bottom: $spacing-lg;
  box-shadow: $shadow-lg;
}

.user-avatar {
  width: 120rpx;
  height: 120rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: $spacing-lg;
}

.avatar-text {
  font-size: $font-2xl;
  font-weight: $font-bold;
  color: #ffffff;
}

.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.user-name {
  font-size: $font-lg;
  font-weight: $font-bold;
  color: #ffffff;
}

.user-role {
  font-size: $font-sm;
  color: rgba(255, 255, 255, 0.8);
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 8rpx 20rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: $radius-full;
}

.badge-icon {
  font-size: $font-sm;
  color: #ffffff;
}

.badge-text {
  font-size: $font-xs;
  color: #ffffff;
}

// 设置区块
.settings-section {
  background: var(--bg-card);
  border-radius: $radius-lg;
  padding: $spacing-lg;
  margin-bottom: $spacing-lg;
  box-shadow: $shadow-sm;
}

.section-header {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-lg;
  padding-bottom: $spacing-md;
  border-bottom: 1rpx solid var(--border-color);
}

.section-icon {
  font-size: 36rpx;
}

.section-title {
  flex: 1;
  font-size: $font-md;
  font-weight: $font-semibold;
  color: var(--text-primary);
}

.section-badge {
  padding: 4rpx 16rpx;
  background: var(--primary-color);
  color: #ffffff;
  font-size: $font-xs;
  border-radius: $radius-full;
}

// 设置项
.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-md 0;
}

.setting-left {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.setting-right {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.theme-icon {
  font-size: 36rpx;
}

.arrow-icon {
  font-size: 32rpx;
  color: var(--text-muted);
}

.setting-label {
  font-size: $font-base;
  color: var(--text-primary);
  font-weight: $font-medium;
}

.setting-desc {
  font-size: $font-xs;
  color: var(--text-secondary);
}

.input-wrapper {
  margin-top: $spacing-sm;
}

.setting-input {
  width: 100%;
  height: 88rpx;
  padding: 0 $spacing-lg;
  background: var(--bg-secondary);
  border-radius: $radius-md;
  font-size: $font-base;
  color: var(--text-primary);
  
  &::placeholder {
    color: var(--text-muted);
  }
}

// 通知历史
.history-list {
  max-height: 400rpx;
}

.history-item {
  display: flex;
  gap: $spacing-md;
  padding: $spacing-md 0;
  border-bottom: 1rpx solid var(--border-light);
  
  &:last-child {
    border-bottom: none;
  }
}

.history-icon {
  width: 48rpx;
  height: 48rpx;
  background: var(--bg-secondary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  text {
    font-size: $font-sm;
    color: var(--text-muted);
  }
  
  &.sent {
    background: rgba(34, 197, 94, 0.1);
    
    text {
      color: var(--success-color);
    }
  }
}

.history-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  min-width: 0;
}

.history-text {
  font-size: $font-sm;
  color: var(--text-primary);
  line-height: $line-height-normal;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.history-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-time {
  font-size: $font-xs;
  color: var(--text-muted);
}

.history-status {
  padding: 4rpx 12rpx;
  background: var(--bg-secondary);
  border-radius: $radius-xs;
  font-size: $font-xs;
  color: var(--text-muted);
  
  &.sent {
    background: rgba(34, 197, 94, 0.1);
    color: var(--success-color);
  }
}

.empty-history {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $spacing-xl;
}

.empty-icon {
  font-size: 60rpx;
  margin-bottom: $spacing-sm;
}

.empty-text {
  font-size: $font-sm;
  color: var(--text-muted);
}

// 关于应用
.about-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-md 0;
  border-bottom: 1rpx solid var(--border-light);
  
  &:last-child {
    border-bottom: none;
  }
  
  &.clickable {
    &:active {
      opacity: 0.7;
    }
  }
}

.about-label {
  font-size: $font-base;
  color: var(--text-secondary);
}

.about-value {
  font-size: $font-base;
  color: var(--text-primary);
  font-weight: $font-medium;
}

// 退出登录
.logout-section {
  margin-top: $spacing-lg;
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
  height: 96rpx;
  background: var(--bg-card);
  border-radius: $radius-lg;
  box-shadow: $shadow-sm;
  transition: all $transition-fast;
  
  &:active {
    transform: scale(0.98);
    background: var(--bg-secondary);
  }
}

.logout-icon {
  font-size: 36rpx;
}

.logout-text {
  font-size: $font-md;
  color: var(--danger-color);
  font-weight: $font-medium;
}

// 底部版权
.footer {
  margin-top: $spacing-xl;
  text-align: center;
}

.footer-text {
  font-size: $font-xs;
  color: var(--text-muted);
}
</style>
