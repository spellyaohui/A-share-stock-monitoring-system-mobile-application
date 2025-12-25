<template>
  <view class="dashboard-page">
    <!-- 统计卡片区域 -->
    <view class="stats-section">
      <view class="stats-grid">
        <StatCard icon="📊" :value="monitorStore.monitorCount" label="监测中" gradient="primary" />
        <StatCard icon="✅" :value="monitorStore.activeCount" label="活跃中" gradient="success" />
        <StatCard icon="📈" :value="monitorStore.upCount" label="上涨" gradient="danger" />
        <StatCard icon="📉" :value="monitorStore.downCount" label="下跌" gradient="info" />
      </view>
    </view>
    
    <!-- 监测列表区域 -->
    <view class="monitor-section">
      <view class="section-header">
        <text class="section-title">我的监测</text>
        <view class="refresh-btn" @click="handleRefresh">
          <text class="refresh-icon" :class="{ 'rotating': loading }">🔄</text>
        </view>
      </view>
      
      <!-- 加载骨架屏 -->
      <LoadingSkeleton v-if="loading && monitors.length === 0" type="card" :count="3" />
      
      <!-- 监测列表 -->
      <scroll-view 
        class="monitor-list" 
        scroll-y 
        :refresher-enabled="true"
        :refresher-triggered="refreshing"
        @refresherrefresh="onPullDownRefresh"
      >
        <view class="monitor-items">
          <StockCard
            v-for="item in monitors"
            :key="item.id"
            :monitor="item"
            @click="goToDetail"
            @toggle="handleToggle"
            @delete="handleDelete"
          />
        </view>
        
        <!-- 空状态 -->
        <view class="empty-state" v-if="!loading && monitors.length === 0">
          <text class="empty-icon">📭</text>
          <text class="empty-text">暂无监测</text>
          <text class="empty-hint">点击下方按钮添加股票监测</text>
          <view class="empty-btn" @click="goToSearch">
            <text>添加监测</text>
          </view>
        </view>
        
        <!-- 底部安全区域 -->
        <view class="safe-bottom"></view>
      </scroll-view>
    </view>
    
    <!-- 悬浮添加按钮 -->
    <view class="fab-btn" @click="goToSearch">
      <text class="fab-icon">+</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useMonitorStore } from '@/store/monitor'
import StatCard from '@/components/StatCard.vue'
import StockCard from '@/components/StockCard.vue'
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'

const monitorStore = useMonitorStore()

// 状态
const loading = ref(false)
const refreshing = ref(false)

// 计算属性
const monitors = computed(() => monitorStore.monitors)

// 生命周期
onMounted(async () => {
  await loadData()
  monitorStore.startAutoRefresh()
})

onUnmounted(() => {
  monitorStore.stopAutoRefresh()
})

// 加载数据
async function loadData() {
  loading.value = true
  try {
    await monitorStore.loadMonitors()
  } catch (error) {
    console.error('加载监测列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 下拉刷新
async function onPullDownRefresh() {
  refreshing.value = true
  try {
    await monitorStore.loadMonitors()
    uni.showToast({ title: '刷新成功', icon: 'success', duration: 1000 })
  } catch (error) {
    uni.showToast({ title: '刷新失败', icon: 'none' })
  } finally {
    refreshing.value = false
  }
}

// 手动刷新
async function handleRefresh() {
  if (loading.value) return
  await loadData()
}

// 切换监测状态
async function handleToggle(id: number, active: boolean) {
  try {
    await monitorStore.toggleMonitor(id, active)
    uni.showToast({ 
      title: active ? '已启用' : '已禁用', 
      icon: 'success',
      duration: 1000
    })
  } catch (error) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

// 删除监测
function handleDelete(id: number) {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除该监测吗？',
    confirmColor: '#ef4444',
    success: async (res) => {
      if (res.confirm) {
        try {
          await monitorStore.deleteMonitor(id)
          uni.showToast({ title: '删除成功', icon: 'success' })
        } catch (error) {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    }
  })
}

// 跳转到详情
function goToDetail(stockId: number) {
  uni.navigateTo({ url: `/pages/stock-detail/index?id=${stockId}` })
}

// 跳转到搜索
function goToSearch() {
  uni.switchTab({ url: '/pages/stock-search/index' })
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.dashboard-page {
  min-height: 100vh;
  background: var(--bg-primary);
  padding-bottom: calc($tabbar-height + $safe-area-bottom);
}

// 统计卡片区域
.stats-section {
  padding: $spacing-md;
  background: $primary-gradient;
  padding-top: calc($spacing-md + env(safe-area-inset-top));
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $spacing-sm;
}

// 监测列表区域
.monitor-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-md $spacing-md $spacing-sm;
}

.section-title {
  font-size: $font-lg;
  font-weight: $font-semibold;
  color: var(--text-primary);
}

.refresh-btn {
  padding: $spacing-xs;
}

.refresh-icon {
  font-size: 40rpx;
  display: inline-block;
  transition: transform 0.3s;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 监测列表
.monitor-list {
  flex: 1;
  height: calc(100vh - 400rpx - $tabbar-height);
}

.monitor-items {
  padding: 0 $spacing-md;
}

// 空状态
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $spacing-2xl;
}

.empty-icon {
  font-size: 160rpx;
  margin-bottom: $spacing-md;
}

.empty-text {
  font-size: $font-md;
  color: var(--text-secondary);
  margin-bottom: $spacing-xs;
}

.empty-hint {
  font-size: $font-sm;
  color: var(--text-muted);
  margin-bottom: $spacing-lg;
}

.empty-btn {
  padding: $spacing-md $spacing-xl;
  background: $primary-gradient;
  border-radius: $radius-full;
  
  text {
    color: #ffffff;
    font-size: $font-base;
    font-weight: $font-medium;
  }
  
  &:active {
    opacity: 0.9;
    transform: scale(0.98);
  }
}

// 底部安全区域
.safe-bottom {
  height: calc($spacing-xl + $safe-area-bottom);
}

// 悬浮添加按钮
.fab-btn {
  position: fixed;
  right: $spacing-lg;
  bottom: calc($tabbar-height + $spacing-lg + $safe-area-bottom);
  width: 112rpx;
  height: 112rpx;
  background: $primary-gradient;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 32rpx rgba(102, 126, 234, 0.4);
  z-index: 100;
  transition: all $transition-normal;
  
  &:active {
    transform: scale(0.95);
    box-shadow: 0 4rpx 16rpx rgba(102, 126, 234, 0.3);
  }
}

.fab-icon {
  font-size: 56rpx;
  color: #ffffff;
  font-weight: 300;
  line-height: 1;
}
</style>
