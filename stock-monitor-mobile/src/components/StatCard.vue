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
@import '@/styles/variables.scss';

.stat-card {
  display: flex;
  align-items: center;
  padding: $spacing-lg;
  border-radius: $radius-lg;
  color: #ffffff;
  box-shadow: $shadow-md;
  transition: all $transition-normal;
  
  &:active {
    transform: scale(0.98);
    opacity: 0.95;
  }
}

.gradient-primary {
  background: $primary-gradient;
}

.gradient-success {
  background: $gradient-success;
}

.gradient-warning {
  background: $gradient-warning;
}

.gradient-danger {
  background: $gradient-danger;
}

.gradient-info {
  background: $gradient-info;
}

.stat-icon {
  font-size: 64rpx;
  margin-right: $spacing-md;
  opacity: 0.9;
}

.stat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: $font-2xl;
  font-weight: $font-bold;
  line-height: 1.2;
}

.stat-label {
  font-size: $font-sm;
  opacity: 0.9;
  margin-top: $spacing-xs;
}
</style>
