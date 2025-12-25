<template>
  <view class="skeleton-container">
    <!-- 卡片骨架 -->
    <template v-if="type === 'card'">
      <view class="skeleton-card" v-for="i in count" :key="i">
        <view class="skeleton-header">
          <view class="skeleton skeleton-title"></view>
          <view class="skeleton skeleton-switch"></view>
        </view>
        <view class="skeleton skeleton-price"></view>
        <view class="skeleton-tags">
          <view class="skeleton skeleton-tag"></view>
          <view class="skeleton skeleton-tag"></view>
        </view>
      </view>
    </template>
    
    <!-- 列表骨架 -->
    <template v-else-if="type === 'list'">
      <view class="skeleton-list-item" v-for="i in count" :key="i">
        <view class="skeleton skeleton-avatar"></view>
        <view class="skeleton-list-content">
          <view class="skeleton skeleton-line"></view>
          <view class="skeleton skeleton-line-short"></view>
        </view>
        <view class="skeleton skeleton-value"></view>
      </view>
    </template>
    
    <!-- 统计卡片骨架 -->
    <template v-else-if="type === 'stat'">
      <view class="skeleton-stat-grid">
        <view class="skeleton-stat" v-for="i in count" :key="i">
          <view class="skeleton skeleton-stat-icon"></view>
          <view class="skeleton-stat-content">
            <view class="skeleton skeleton-stat-value"></view>
            <view class="skeleton skeleton-stat-label"></view>
          </view>
        </view>
      </view>
    </template>
    
    <!-- 详情骨架 -->
    <template v-else-if="type === 'detail'">
      <view class="skeleton-detail">
        <view class="skeleton-detail-header">
          <view class="skeleton skeleton-detail-title"></view>
          <view class="skeleton skeleton-detail-price"></view>
        </view>
        <view class="skeleton-detail-grid">
          <view class="skeleton skeleton-detail-item" v-for="i in 8" :key="i"></view>
        </view>
        <view class="skeleton skeleton-chart"></view>
      </view>
    </template>
    
    <!-- 排行榜骨架 -->
    <template v-else-if="type === 'ranking'">
      <view class="skeleton-ranking">
        <view class="skeleton skeleton-ranking-header"></view>
        <view class="skeleton-ranking-item" v-for="i in count" :key="i">
          <view class="skeleton skeleton-rank"></view>
          <view class="skeleton-ranking-info">
            <view class="skeleton skeleton-line"></view>
            <view class="skeleton skeleton-line-short"></view>
          </view>
          <view class="skeleton skeleton-value"></view>
        </view>
      </view>
    </template>
  </view>
</template>

<script setup lang="ts">
interface Props {
  type?: 'card' | 'list' | 'stat' | 'detail' | 'ranking'
  count?: number
}

withDefaults(defineProps<Props>(), {
  type: 'card',
  count: 3
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.skeleton-container {
  width: 100%;
}

// 骨架基础样式
.skeleton {
  background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-primary) 50%, var(--bg-secondary) 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: $radius-sm;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

// 卡片骨架
.skeleton-card {
  background: var(--bg-card);
  border-radius: $radius-lg;
  padding: $spacing-lg;
  margin-bottom: $spacing-md;
  box-shadow: var(--shadow-sm);
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
}

.skeleton-title {
  width: 200rpx;
  height: 40rpx;
}

.skeleton-switch {
  width: 80rpx;
  height: 40rpx;
  border-radius: 20rpx;
}

.skeleton-price {
  width: 240rpx;
  height: 60rpx;
  margin-bottom: $spacing-md;
}

.skeleton-tags {
  display: flex;
  gap: $spacing-xs;
}

.skeleton-tag {
  width: 100rpx;
  height: 40rpx;
}

// 列表骨架
.skeleton-list-item {
  display: flex;
  align-items: center;
  padding: $spacing-md;
  background: var(--bg-card);
  border-radius: $radius-md;
  margin-bottom: $spacing-sm;
}

.skeleton-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  margin-right: $spacing-md;
  flex-shrink: 0;
}

.skeleton-list-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.skeleton-line {
  width: 100%;
  height: 32rpx;
}

.skeleton-line-short {
  width: 60%;
  height: 24rpx;
}

.skeleton-value {
  width: 120rpx;
  height: 40rpx;
}

// 统计卡片骨架
.skeleton-stat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $spacing-md;
}

.skeleton-stat {
  display: flex;
  align-items: center;
  padding: $spacing-lg;
  background: var(--bg-card);
  border-radius: $radius-lg;
}

.skeleton-stat-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: $radius-md;
  margin-right: $spacing-md;
}

.skeleton-stat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.skeleton-stat-value {
  width: 100rpx;
  height: 48rpx;
}

.skeleton-stat-label {
  width: 80rpx;
  height: 28rpx;
}

// 详情骨架
.skeleton-detail {
  padding: $spacing-lg;
}

.skeleton-detail-header {
  margin-bottom: $spacing-lg;
}

.skeleton-detail-title {
  width: 200rpx;
  height: 48rpx;
  margin-bottom: $spacing-sm;
}

.skeleton-detail-price {
  width: 280rpx;
  height: 72rpx;
}

.skeleton-detail-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: $spacing-md;
  margin-bottom: $spacing-lg;
}

.skeleton-detail-item {
  height: 100rpx;
  border-radius: $radius-md;
}

.skeleton-chart {
  width: 100%;
  height: 400rpx;
  border-radius: $radius-lg;
}

// 排行榜骨架
.skeleton-ranking {
  background: var(--bg-card);
  border-radius: $radius-lg;
  padding: $spacing-lg;
}

.skeleton-ranking-header {
  width: 200rpx;
  height: 40rpx;
  margin-bottom: $spacing-md;
}

.skeleton-ranking-item {
  display: flex;
  align-items: center;
  padding: $spacing-sm;
  margin-bottom: $spacing-sm;
}

.skeleton-rank {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  margin-right: $spacing-md;
}

.skeleton-ranking-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}
</style>
