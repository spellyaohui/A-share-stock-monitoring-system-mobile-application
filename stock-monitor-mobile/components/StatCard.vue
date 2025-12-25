<template>
  <view class="stat-card" :class="[`gradient-${gradient}`]">
    <view class="stat-icon">{{ icon }}</view>
    <view class="stat-content">
      <text class="stat-value">{{ displayValue }}</text>
      <text class="stat-label">{{ label }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  icon: string
  value: number | string
  label: string
  gradient?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
}

const props = withDefaults(defineProps<Props>(), {
  gradient: 'primary'
})

const displayValue = computed(() => {
  if (typeof props.value === 'number') {
    // 大数字格式化
    if (props.value >= 100000000) {
      return (props.value / 100000000).toFixed(2) + '亿'
    }
    if (props.value >= 10000) {
      return (props.value / 10000).toFixed(2) + '万'
    }
    return props.value.toString()
  }
  return props.value
})
</script>

<style lang="scss" scoped>
@import '../styles/variables.scss';

.stat-card {
  display: flex;
  align-items: center;
  padding: 32rpx;
  border-radius: 24rpx;
  color: #ffffff;
  box-shadow: var(--shadow-md);
  transition: all 0.25s ease;
  
  &:active {
    transform: scale(0.98);
    opacity: 0.95;
  }
}

.gradient-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.gradient-success {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.gradient-warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.gradient-danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.gradient-info {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.stat-icon {
  font-size: 64rpx;
  margin-right: 24rpx;
  opacity: 0.9;
}

.stat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 56rpx;
  font-weight: 700;
  line-height: 1.2;
}

.stat-label {
  font-size: 24rpx;
  opacity: 0.9;
  margin-top: 8rpx;
}
</style>
