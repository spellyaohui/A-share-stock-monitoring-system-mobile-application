<template>
  <view class="progress-loading">
    <view class="loading-content">
      <!-- 圆形进度 -->
      <view class="progress-circle">
        <view class="circle-bg"></view>
        <view class="circle-progress" :style="{ transform: `rotate(${progressDegree}deg)` }"></view>
        <view class="circle-mask" v-if="progress < 50"></view>
        <view class="circle-center">
          <text class="progress-text">{{ Math.round(progress) }}%</text>
        </view>
      </view>
      
      <!-- 加载文字 -->
      <text class="loading-message">{{ message }}</text>
      
      <!-- 进度条 -->
      <view class="progress-bar">
        <view class="progress-bar-fill" :style="{ width: `${progress}%` }"></view>
      </view>
      
      <!-- 提示文字 -->
      <text class="loading-hint">{{ hint }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

interface Props {
  loading?: boolean
  message?: string
  hint?: string
  duration?: number  // 预估加载时间（毫秒）
}

const props = withDefaults(defineProps<Props>(), {
  loading: true,
  message: '加载中...',
  hint: '正在获取数据，请稍候',
  duration: 3000
})

const progress = ref(0)
let timer: number | null = null
let startTime = 0

// 计算圆形进度的旋转角度
const progressDegree = computed(() => {
  return (progress.value / 100) * 360
})

// 模拟进度增长
function startProgress() {
  startTime = Date.now()
  progress.value = 0
  
  const tick = () => {
    if (!props.loading) {
      // 加载完成，快速到100%
      progress.value = 100
      return
    }
    
    const elapsed = Date.now() - startTime
    // 使用缓动函数，越接近100%增长越慢
    const targetProgress = Math.min(95, (elapsed / props.duration) * 100)
    const eased = easeOutQuad(targetProgress / 100) * 95
    
    progress.value = Math.max(progress.value, eased)
    
    if (progress.value < 95) {
      timer = requestAnimationFrame(tick) as unknown as number
    }
  }
  
  timer = requestAnimationFrame(tick) as unknown as number
}

// 缓动函数
function easeOutQuad(t: number): number {
  return t * (2 - t)
}

// 监听 loading 状态
watch(() => props.loading, (newVal) => {
  if (!newVal) {
    // 加载完成
    progress.value = 100
    if (timer) {
      cancelAnimationFrame(timer)
      timer = null
    }
  } else {
    startProgress()
  }
})

onMounted(() => {
  if (props.loading) {
    startProgress()
  }
})

onUnmounted(() => {
  if (timer) {
    cancelAnimationFrame(timer)
  }
})
</script>

<style lang="scss" scoped>
.progress-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 48rpx;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
}

// 圆形进度
.progress-circle {
  position: relative;
  width: 120rpx;
  height: 120rpx;
}

.circle-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 8rpx solid #e5e7eb;
  box-sizing: border-box;
}

.circle-progress {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 8rpx solid transparent;
  border-top-color: #667eea;
  border-right-color: #667eea;
  box-sizing: border-box;
  transition: transform 0.1s linear;
}

.circle-mask {
  position: absolute;
  width: 50%;
  height: 100%;
  right: 0;
  background: #fff;
}

.circle-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.progress-text {
  font-size: 24rpx;
  font-weight: 600;
  color: #667eea;
}

// 加载文字
.loading-message {
  font-size: 28rpx;
  color: var(--text-primary);
  font-weight: 500;
}

// 进度条
.progress-bar {
  width: 400rpx;
  height: 8rpx;
  background: #e5e7eb;
  border-radius: 4rpx;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 4rpx;
  transition: width 0.1s linear;
}

// 提示文字
.loading-hint {
  font-size: 24rpx;
  color: var(--text-secondary);
}
</style>
