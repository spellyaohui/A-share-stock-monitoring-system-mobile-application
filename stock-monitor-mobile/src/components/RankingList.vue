<template>
  <view class="ranking-list">
    <!-- 标题 -->
    <view class="ranking-header">
      <text class="ranking-icon">{{ icon }}</text>
      <text class="ranking-title">{{ title }}</text>
    </view>
    
    <!-- 列表 -->
    <view class="ranking-items">
      <view 
        class="ranking-item" 
        v-for="(item, index) in items" 
        :key="item.代码"
        @click="handleItemClick(item)"
      >
        <!-- 排名 -->
        <view class="rank-badge" :class="getRankClass(index)">
          <text>{{ index + 1 }}</text>
        </view>
        
        <!-- 股票信息 -->
        <view class="item-info">
          <text class="item-name">{{ item.名称 }}</text>
          <text class="item-code">{{ item.代码 }}</text>
        </view>
        
        <!-- 价格和涨跌幅 -->
        <view class="item-data">
          <text class="item-price">{{ formatPrice(item.最新价) }}</text>
          <text class="item-change" :class="getChangeClass(item.涨跌幅)">
            {{ formatChange(item.涨跌幅) }}
          </text>
        </view>
      </view>
    </view>
    
    <!-- 空状态 -->
    <view class="empty-state" v-if="items.length === 0">
      <text class="empty-text">暂无数据</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import type { RankingItem } from '@/types'

interface Props {
  title: string
  icon: string
  items: RankingItem[]
}

interface Emits {
  (e: 'itemClick', item: RankingItem): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

// 获取排名样式类
function getRankClass(index: number): string {
  if (index === 0) return 'rank-gold'
  if (index === 1) return 'rank-silver'
  if (index === 2) return 'rank-bronze'
  return ''
}

// 获取涨跌颜色类
function getChangeClass(change?: number): string {
  if (!change && change !== 0) return ''
  return change >= 0 ? 'text-up' : 'text-down'
}

// 格式化价格
function formatPrice(price?: number): string {
  if (!price && price !== 0) return '--'
  return price.toFixed(2)
}

// 格式化涨跌幅
function formatChange(change?: number): string {
  if (!change && change !== 0) return '--'
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

// 点击事件
function handleItemClick(item: RankingItem) {
  emit('itemClick', item)
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.ranking-list {
  background: var(--bg-card);
  border-radius: $radius-lg;
  padding: $spacing-lg;
  box-shadow: var(--shadow-sm);
}

.ranking-header {
  display: flex;
  align-items: center;
  margin-bottom: $spacing-md;
  padding-bottom: $spacing-md;
  border-bottom: 1rpx solid var(--border-color);
}

.ranking-icon {
  font-size: 40rpx;
  margin-right: $spacing-sm;
}

.ranking-title {
  font-size: $font-md;
  font-weight: $font-semibold;
  color: var(--text-primary);
}

.ranking-items {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.ranking-item {
  display: flex;
  align-items: center;
  padding: $spacing-sm;
  border-radius: $radius-md;
  background: var(--bg-primary);
  transition: all $transition-fast;
  
  &:active {
    background: var(--bg-secondary);
    transform: translateX(8rpx);
  }
}

.rank-badge {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: var(--text-muted);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-sm;
  font-weight: $font-semibold;
  margin-right: $spacing-md;
  flex-shrink: 0;
}

.rank-gold {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
}

.rank-silver {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
}

.rank-bronze {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
  min-width: 0;
}

.item-name {
  font-size: $font-base;
  font-weight: $font-medium;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-code {
  font-size: $font-xs;
  color: var(--text-secondary);
}

.item-data {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4rpx;
}

.item-price {
  font-size: $font-base;
  font-weight: $font-semibold;
  color: var(--text-primary);
}

.item-change {
  font-size: $font-sm;
  font-weight: $font-medium;
}

.text-up {
  color: var(--up-color);
}

.text-down {
  color: var(--down-color);
}

.empty-state {
  padding: $spacing-xl;
  text-align: center;
}

.empty-text {
  font-size: $font-base;
  color: var(--text-muted);
}
</style>
