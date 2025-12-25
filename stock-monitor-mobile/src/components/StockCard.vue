<template>
  <view class="stock-card" @click="handleClick">
    <!-- 头部：股票信息和开关 -->
    <view class="card-header">
      <view class="stock-info">
        <text class="stock-name">{{ monitor.stock?.name || '--' }}</text>
        <text class="stock-code">{{ monitor.stock?.code || '--' }}</text>
      </view>
      <switch 
        class="stock-switch"
        :checked="monitor.is_active !== false" 
        @change="handleToggle"
        color="#667eea"
      />
    </view>
    
    <!-- 价格区域 -->
    <view class="price-section">
      <text class="current-price" :class="priceClass">
        {{ formatPrice(monitor.current_price) }}
      </text>
      <view class="change-info" :class="priceClass">
        <text class="change-percent">{{ formatChange(monitor.change) }}</text>
      </view>
    </view>
    
    <!-- 监测条件标签 -->
    <view class="conditions" v-if="hasConditions">
      <view class="condition-tag tag-success" v-if="monitor.price_min">
        <text>≥{{ monitor.price_min }}</text>
      </view>
      <view class="condition-tag tag-warning" v-if="monitor.price_max">
        <text>≤{{ monitor.price_max }}</text>
      </view>
      <view class="condition-tag tag-danger" v-if="monitor.rise_threshold">
        <text>涨{{ monitor.rise_threshold }}%</text>
      </view>
      <view class="condition-tag tag-info" v-if="monitor.fall_threshold">
        <text>跌{{ monitor.fall_threshold }}%</text>
      </view>
    </view>
    
    <!-- 底部操作区 -->
    <view class="card-footer" v-if="showActions">
      <view class="action-btn delete-btn" @click.stop="handleDelete">
        <text>删除</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { MonitorConfig } from '@/types'

interface Props {
  monitor: MonitorConfig
  showActions?: boolean
}

interface Emits {
  (e: 'click', stockId: number): void
  (e: 'toggle', id: number, active: boolean): void
  (e: 'delete', id: number): void
}

const props = withDefaults(defineProps<Props>(), {
  showActions: true
})

const emit = defineEmits<Emits>()

// 计算属性
const priceClass = computed(() => {
  const change = props.monitor.change || 0
  return change >= 0 ? 'text-up' : 'text-down'
})

const hasConditions = computed(() => {
  return props.monitor.price_min || 
         props.monitor.price_max || 
         props.monitor.rise_threshold || 
         props.monitor.fall_threshold
})

// 格式化函数
function formatPrice(price?: number): string {
  if (!price && price !== 0) return '--'
  return price.toFixed(2)
}

function formatChange(change?: number): string {
  if (!change && change !== 0) return '--'
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

// 事件处理
function handleClick() {
  if (props.monitor.stock_id) {
    emit('click', props.monitor.stock_id)
  }
}

function handleToggle(e: any) {
  e.stopPropagation()
  if (props.monitor.id) {
    emit('toggle', props.monitor.id, e.detail.value)
  }
}

function handleDelete() {
  if (props.monitor.id) {
    emit('delete', props.monitor.id)
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.stock-card {
  background: var(--bg-card);
  border-radius: $radius-lg;
  padding: $spacing-lg;
  margin-bottom: $spacing-md;
  box-shadow: var(--shadow-sm);
  transition: all $transition-normal;
  
  &:active {
    transform: scale(0.98);
    background: var(--bg-secondary);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-md;
}

.stock-info {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.stock-name {
  font-size: $font-md;
  font-weight: $font-semibold;
  color: var(--text-primary);
}

.stock-code {
  font-size: $font-sm;
  color: var(--text-secondary);
}

.stock-switch {
  transform: scale(0.85);
}

.price-section {
  display: flex;
  align-items: baseline;
  margin-bottom: $spacing-md;
}

.current-price {
  font-size: $font-3xl;
  font-weight: $font-bold;
  margin-right: $spacing-md;
}

.change-info {
  display: flex;
  flex-direction: column;
}

.change-percent {
  font-size: $font-base;
  font-weight: $font-medium;
}

.text-up {
  color: var(--up-color);
}

.text-down {
  color: var(--down-color);
}

.conditions {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-xs;
  margin-bottom: $spacing-md;
}

.condition-tag {
  display: inline-flex;
  align-items: center;
  padding: 8rpx 16rpx;
  border-radius: $radius-sm;
  font-size: $font-xs;
  font-weight: $font-medium;
}

.tag-success {
  background: rgba(34, 197, 94, 0.1);
  color: var(--success-color);
}

.tag-warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning-color);
}

.tag-danger {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
}

.tag-info {
  background: rgba(59, 130, 246, 0.1);
  color: var(--info-color);
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: $spacing-md;
  border-top: 1rpx solid var(--border-color);
}

.action-btn {
  padding: $spacing-xs $spacing-md;
  border-radius: $radius-sm;
  font-size: $font-sm;
  
  &:active {
    opacity: 0.7;
  }
}

.delete-btn {
  color: var(--danger-color);
}
</style>
