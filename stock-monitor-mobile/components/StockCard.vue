<template>
  <view class="stock-card" :class="{ 'has-alert': monitor.has_alert }" @click="handleClick">
    <!-- 主要内容区：单行紧凑布局 -->
    <view class="card-main">
      <!-- 左侧：股票信息 -->
      <view class="stock-info">
        <view class="stock-name-row">
          <text class="stock-name">{{ monitor.stock_name || monitor.stock?.name || '--' }}</text>
          <text class="alert-icon" v-if="monitor.has_alert">🔔</text>
        </view>
        <text class="stock-code">{{ monitor.stock_code || monitor.stock?.code || '--' }}</text>
      </view>
      
      <!-- 中间：价格和涨跌 -->
      <view class="price-section">
        <text class="current-price" :class="priceClass">
          {{ formatPrice(monitor.price || monitor.current_price) }}
        </text>
        <text class="change-percent" :class="priceClass">
          {{ formatChange(monitor.change_percent || monitor.change) }}
        </text>
      </view>
      
      <!-- 右侧：开关和删除 -->
      <view class="actions-section">
        <switch 
          class="stock-switch"
          :checked="monitor.is_active !== false" 
          @change="handleToggle"
          color="#667eea"
        />
        <view class="delete-btn" @click.stop="handleDelete" v-if="showActions">
          <text>✕</text>
        </view>
      </view>
    </view>
    
    <!-- 预警信息（仅在有预警时显示，单行） -->
    <view class="alert-row" v-if="monitor.alerts && monitor.alerts.length > 0">
      <text class="alert-text" :class="'alert-' + monitor.alerts[0].level">
        {{ getAlertIcon(monitor.alerts[0].level) }} {{ monitor.alerts[0].message }}
      </text>
    </view>
    
    <!-- 监测条件标签（单行横向排列） -->
    <view class="conditions" v-if="hasConditions">
      <view class="condition-tag tag-warning" v-if="monitor.price_upper">
        <text>≤{{ monitor.price_upper }}</text>
      </view>
      <view class="condition-tag tag-success" v-if="monitor.price_lower">
        <text>≥{{ monitor.price_lower }}</text>
      </view>
      <view class="condition-tag tag-danger" v-if="monitor.change_upper">
        <text>涨{{ monitor.change_upper }}%</text>
      </view>
      <view class="condition-tag tag-info" v-if="monitor.change_lower">
        <text>跌{{ monitor.change_lower }}%</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { MonitorConfig } from '../types'

interface Props {
  monitor: MonitorConfig
  showActions?: boolean
}

interface Emits {
  (e: 'click', data: { stockId: number, code?: string, name?: string }): void
  (e: 'toggle', id: number, active: boolean): void
  (e: 'delete', id: number): void
}

const props = withDefaults(defineProps<Props>(), {
  showActions: true
})

const emit = defineEmits<Emits>()

// 计算属性
const priceClass = computed(() => {
  const change = props.monitor.change_percent || props.monitor.change || 0
  return change >= 0 ? 'text-up' : 'text-down'
})

const hasConditions = computed(() => {
  return props.monitor.price_lower || 
         props.monitor.price_upper || 
         props.monitor.change_upper || 
         props.monitor.change_lower ||
         props.monitor.price_min || 
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

// 获取预警图标
function getAlertIcon(level: string): string {
  switch (level) {
    case 'danger': return '🚨'
    case 'warning': return '⚠️'
    case 'info': return 'ℹ️'
    default: return '🔔'
  }
}

// 事件处理
function handleClick() {
  if (props.monitor.stock_id) {
    emit('click', {
      stockId: props.monitor.stock_id,
      code: props.monitor.stock?.code || props.monitor.stock_code,
      name: props.monitor.stock?.name || props.monitor.stock_name
    })
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
@import '../styles/variables.scss';

.stock-card {
  background: var(--bg-card);
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 16rpx;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
  
  &:active {
    transform: scale(0.98);
    background: var(--bg-secondary);
  }
  
  &.has-alert {
    border-left: 4rpx solid var(--warning-color);
  }
}

// 主要内容区：横向布局
.card-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

// 股票信息
.stock-info {
  flex: 1;
  min-width: 0;
}

.stock-name-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.stock-name {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.alert-icon {
  font-size: 24rpx;
  animation: shake 0.5s ease-in-out infinite;
}

@keyframes shake {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-10deg); }
  75% { transform: rotate(10deg); }
}

.stock-code {
  font-size: 20rpx;
  color: var(--text-secondary);
  margin-top: 2rpx;
}

// 价格区域
.price-section {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  margin: 0 16rpx;
}

.current-price {
  font-size: 32rpx;
  font-weight: 700;
}

.change-percent {
  font-size: 22rpx;
  font-weight: 500;
}

.text-up {
  color: var(--up-color);
}

.text-down {
  color: var(--down-color);
}

// 操作区
.actions-section {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.stock-switch {
  transform: scale(0.7);
}

.delete-btn {
  width: 44rpx;
  height: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.1);
  
  text {
    font-size: 24rpx;
    color: var(--danger-color);
  }
  
  &:active {
    background: rgba(239, 68, 68, 0.2);
  }
}

// 预警信息行
.alert-row {
  margin-top: 12rpx;
  padding-top: 12rpx;
  border-top: 1rpx solid var(--border-light);
}

.alert-text {
  font-size: 22rpx;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.alert-danger {
  color: var(--danger-color);
}

.alert-warning {
  color: var(--warning-color);
}

.alert-info {
  color: var(--info-color);
}

// 监测条件标签
.conditions {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
  margin-top: 12rpx;
}

.condition-tag {
  display: inline-flex;
  align-items: center;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
  font-weight: 500;
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
</style>
