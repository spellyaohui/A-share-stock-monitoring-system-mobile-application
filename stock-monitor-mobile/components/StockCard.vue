<template>
  <view class="stock-card" :class="{ 'has-alert': monitor.has_alert }" @click="handleClick">
    <!-- 预警标识 -->
    <view class="alert-badge" v-if="monitor.has_alert">
      <text>🔔</text>
    </view>
    
    <!-- 头部：股票信息和开关 -->
    <view class="card-header">
      <view class="stock-info">
        <text class="stock-name">{{ monitor.stock_name || monitor.stock?.name || '--' }}</text>
        <text class="stock-code">{{ monitor.stock_code || monitor.stock?.code || '--' }}</text>
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
        {{ formatPrice(monitor.price || monitor.current_price) }}
      </text>
      <view class="change-info" :class="priceClass">
        <text class="change-percent">{{ formatChange(monitor.change_percent || monitor.change) }}</text>
      </view>
    </view>
    
    <!-- 预警信息 -->
    <view class="alerts-section" v-if="monitor.alerts && monitor.alerts.length > 0">
      <view 
        class="alert-item" 
        v-for="(alert, index) in monitor.alerts" 
        :key="index"
        :class="'alert-' + alert.level"
      >
        <text class="alert-icon">{{ getAlertIcon(alert.level) }}</text>
        <text class="alert-message">{{ alert.message }}</text>
      </view>
    </view>
    
    <!-- 监测条件标签 -->
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
import type { MonitorConfig } from '../types'

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
@import '../styles/variables.scss';

.stock-card {
  background: var(--bg-card);
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: var(--shadow-sm);
  transition: all 0.25s ease;
  position: relative;
  
  &:active {
    transform: scale(0.98);
    background: var(--bg-secondary);
  }
  
  &.has-alert {
    border-left: 6rpx solid var(--warning-color);
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, var(--bg-card) 100%);
  }
}

.alert-badge {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  font-size: 32rpx;
  animation: shake 0.5s ease-in-out infinite;
}

@keyframes shake {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-10deg); }
  75% { transform: rotate(10deg); }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24rpx;
}

.stock-info {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.stock-name {
  font-size: 32rpx;
  font-weight: 600;
  color: var(--text-primary);
}

.stock-code {
  font-size: 24rpx;
  color: var(--text-secondary);
}

.stock-switch {
  transform: scale(0.85);
}

.price-section {
  display: flex;
  align-items: baseline;
  margin-bottom: 24rpx;
}

.current-price {
  font-size: 72rpx;
  font-weight: 700;
  margin-right: 24rpx;
}

.change-info {
  display: flex;
  flex-direction: column;
}

.change-percent {
  font-size: 28rpx;
  font-weight: 500;
}

.text-up {
  color: var(--up-color);
}

.text-down {
  color: var(--down-color);
}

// 预警信息
.alerts-section {
  margin-bottom: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.alert-item {
  display: flex;
  align-items: center;
  padding: 8rpx 16rpx;
  border-radius: 12rpx;
  font-size: 22rpx;
}

.alert-icon {
  margin-right: 8rpx;
}

.alert-message {
  flex: 1;
}

.alert-danger {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
}

.alert-warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning-color);
}

.alert-info {
  background: rgba(59, 130, 246, 0.1);
  color: var(--info-color);
}

.conditions {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
  margin-bottom: 24rpx;
}

.condition-tag {
  display: inline-flex;
  align-items: center;
  padding: 8rpx 16rpx;
  border-radius: 12rpx;
  font-size: 22rpx;
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

.card-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 24rpx;
  border-top: 1rpx solid var(--border-color);
}

.action-btn {
  padding: 8rpx 24rpx;
  border-radius: 12rpx;
  font-size: 24rpx;
  
  &:active {
    opacity: 0.7;
  }
}

.delete-btn {
  color: var(--danger-color);
}

// 暗黑模式适配
@media (prefers-color-scheme: dark) {
  .stock-card.has-alert {
    background: linear-gradient(135deg, rgba(251, 191, 36, 0.08) 0%, var(--bg-card) 100%);
  }
}
</style>
