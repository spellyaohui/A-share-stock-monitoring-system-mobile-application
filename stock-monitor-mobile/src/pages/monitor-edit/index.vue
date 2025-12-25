<template>
  <view class="edit-page">
    <!-- 股票信息头部 -->
    <view class="stock-header">
      <view class="stock-icon">📊</view>
      <view class="stock-info">
        <text class="stock-name">{{ stockInfo.name || '加载中...' }}</text>
        <text class="stock-code">{{ stockInfo.code || '--' }}</text>
      </view>
      <view class="stock-price" v-if="currentPrice">
        <text class="price-value" :class="getChangeClass(priceChange)">
          {{ currentPrice.toFixed(2) }}
        </text>
        <text class="price-change" :class="getChangeClass(priceChange)">
          {{ formatChange(priceChange) }}
        </text>
      </view>
    </view>

    <!-- 监测条件表单 -->
    <view class="form-section">
      <view class="section-header">
        <text class="section-icon">⚙️</text>
        <text class="section-title">监测条件</text>
      </view>
      
      <!-- 价格监测 -->
      <view class="form-group">
        <view class="group-title">
          <text class="title-icon">💰</text>
          <text class="title-text">价格监测</text>
        </view>
        <view class="form-row">
          <view class="form-item">
            <text class="form-label">最低价</text>
            <view class="input-wrapper">
              <input
                class="form-input"
                type="digit"
                v-model="form.price_min"
                placeholder="选填"
              />
              <text class="input-unit">元</text>
            </view>
            <text class="form-hint">低于此价格时提醒</text>
          </view>
          <view class="form-item">
            <text class="form-label">最高价</text>
            <view class="input-wrapper">
              <input
                class="form-input"
                type="digit"
                v-model="form.price_max"
                placeholder="选填"
              />
              <text class="input-unit">元</text>
            </view>
            <text class="form-hint">高于此价格时提醒</text>
          </view>
        </view>
      </view>
      
      <!-- 涨跌幅监测 -->
      <view class="form-group">
        <view class="group-title">
          <text class="title-icon">📈</text>
          <text class="title-text">涨跌幅监测</text>
        </view>
        <view class="form-row">
          <view class="form-item">
            <text class="form-label">涨幅阈值</text>
            <view class="input-wrapper">
              <input
                class="form-input"
                type="digit"
                v-model="form.rise_threshold"
                placeholder="选填"
              />
              <text class="input-unit">%</text>
            </view>
            <text class="form-hint">涨幅超过时提醒</text>
          </view>
          <view class="form-item">
            <text class="form-label">跌幅阈值</text>
            <view class="input-wrapper">
              <input
                class="form-input"
                type="digit"
                v-model="form.fall_threshold"
                placeholder="选填"
              />
              <text class="input-unit">%</text>
            </view>
            <text class="form-hint">跌幅超过时提醒</text>
          </view>
        </view>
      </view>
      
      <!-- 提示信息 -->
      <view class="form-tips">
        <text class="tip-icon">💡</text>
        <text class="tip-text">至少设置一个监测条件，满足任一条件时将触发提醒</text>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="actions">
      <view class="btn btn-delete" @click="deleteMonitor" v-if="monitorId">
        <text class="btn-icon">🗑️</text>
        <text class="btn-text">删除监测</text>
      </view>
      <view class="btn btn-save" @click="saveMonitor">
        <text class="btn-icon">✓</text>
        <text class="btn-text">{{ monitorId ? '保存修改' : '添加监测' }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { stockApi, monitorApi } from '@/api'
import type { StockInfo } from '@/types'

// 获取页面参数
const stockId = ref(0)
const stockInfo = ref<StockInfo>({} as StockInfo)
const monitorId = ref<number | null>(null)
const currentPrice = ref<number | null>(null)
const priceChange = ref<number | null>(null)

const form = reactive({
  stock_id: 0,
  price_min: '',
  price_max: '',
  rise_threshold: '',
  fall_threshold: ''
})

onMounted(() => {
  // 获取页面参数
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  const options = currentPage.options || {}
  
  if (options.stockId) {
    stockId.value = parseInt(options.stockId)
    form.stock_id = stockId.value
    loadData()
  }
})

async function loadData() {
  await Promise.all([
    loadStockInfo(),
    loadMonitorInfo()
  ])
}

async function loadStockInfo() {
  try {
    const res = await stockApi.getDetail(stockId.value)
    stockInfo.value = res
    
    // 获取实时价格
    try {
      const realtime = await stockApi.getRealtime(stockId.value)
      currentPrice.value = realtime.price
      priceChange.value = realtime.change_percent
    } catch (e) {
      console.error('获取实时价格失败:', e)
    }
  } catch (error) {
    console.error('加载股票信息失败:', error)
    uni.showToast({ title: '加载股票信息失败', icon: 'none' })
  }
}

async function loadMonitorInfo() {
  try {
    const res = await monitorApi.getList()
    const monitor = res.find((m: any) => m.stock_id === stockId.value)
    if (monitor) {
      monitorId.value = monitor.id
      form.price_min = monitor.price_min?.toString() || ''
      form.price_max = monitor.price_max?.toString() || ''
      form.rise_threshold = monitor.rise_threshold?.toString() || ''
      form.fall_threshold = monitor.fall_threshold?.toString() || ''
    }
  } catch (error) {
    console.error('加载监测信息失败:', error)
  }
}

// 表单验证
function validateForm(): string | null {
  const { price_min, price_max, rise_threshold, fall_threshold } = form
  
  // 至少填写一个条件
  if (!price_min && !price_max && !rise_threshold && !fall_threshold) {
    return '请至少设置一个监测条件'
  }
  
  // 价格验证
  if (price_min && price_max) {
    const min = parseFloat(price_min)
    const max = parseFloat(price_max)
    if (min >= max) {
      return '最低价必须小于最高价'
    }
  }
  
  // 阈值验证
  if (rise_threshold) {
    const val = parseFloat(rise_threshold)
    if (val < 0 || val > 100) {
      return '涨幅阈值必须在 0-100 之间'
    }
  }
  
  if (fall_threshold) {
    const val = parseFloat(fall_threshold)
    if (val < 0 || val > 100) {
      return '跌幅阈值必须在 0-100 之间'
    }
  }
  
  return null
}

async function saveMonitor() {
  const error = validateForm()
  if (error) {
    uni.showToast({ title: error, icon: 'none' })
    return
  }
  
  const data = {
    stock_id: form.stock_id,
    price_min: form.price_min ? parseFloat(form.price_min) : undefined,
    price_max: form.price_max ? parseFloat(form.price_max) : undefined,
    rise_threshold: form.rise_threshold ? parseFloat(form.rise_threshold) : undefined,
    fall_threshold: form.fall_threshold ? parseFloat(form.fall_threshold) : undefined
  }

  try {
    if (monitorId.value) {
      await monitorApi.update(monitorId.value, data)
      uni.showToast({ title: '保存成功', icon: 'success' })
    } else {
      await monitorApi.create(data)
      uni.showToast({ title: '添加成功', icon: 'success' })
    }
    setTimeout(() => {
      uni.navigateBack()
    }, 1000)
  } catch (error: any) {
    uni.showToast({ title: error.detail || '操作失败', icon: 'none' })
  }
}

function deleteMonitor() {
  if (!monitorId.value) return

  uni.showModal({
    title: '确认删除',
    content: '确定要删除该监测吗？删除后无法恢复。',
    confirmColor: '#ef4444',
    success: async (res) => {
      if (res.confirm) {
        try {
          await monitorApi.delete(monitorId.value!)
          uni.showToast({ title: '删除成功', icon: 'success' })
          setTimeout(() => {
            uni.navigateBack()
          }, 1000)
        } catch (error) {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    }
  })
}

// 获取涨跌颜色类
function getChangeClass(value?: number | null): string {
  if (!value && value !== 0) return ''
  return value >= 0 ? 'text-up' : 'text-down'
}

// 格式化涨跌幅
function formatChange(value?: number | null): string {
  if (!value && value !== 0) return '--'
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}
</script>


<style lang="scss" scoped>
@import '@/styles/variables.scss';

.edit-page {
  min-height: 100vh;
  background: var(--bg-primary);
  padding-bottom: 200rpx;
}

// 股票头部
.stock-header {
  display: flex;
  align-items: center;
  padding: $spacing-xl;
  background: $primary-gradient;
  gap: $spacing-md;
}

.stock-icon {
  width: 88rpx;
  height: 88rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: $radius-lg;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44rpx;
  flex-shrink: 0;
}

.stock-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  min-width: 0;
}

.stock-name {
  font-size: $font-lg;
  font-weight: $font-bold;
  color: #ffffff;
}

.stock-code {
  font-size: $font-sm;
  color: rgba(255, 255, 255, 0.8);
}

.stock-price {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4rpx;
}

.price-value {
  font-size: $font-xl;
  font-weight: $font-bold;
  color: #ffffff;
}

.price-change {
  font-size: $font-sm;
  padding: 4rpx 12rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: $radius-xs;
  color: #ffffff;
}

// 表单区域
.form-section {
  margin: $spacing-lg;
  background: var(--bg-card);
  border-radius: $radius-xl;
  padding: $spacing-lg;
  box-shadow: var(--shadow-sm);
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
  font-size: $font-md;
  font-weight: $font-semibold;
  color: var(--text-primary);
}

// 表单组
.form-group {
  margin-bottom: $spacing-xl;
  
  &:last-of-type {
    margin-bottom: $spacing-lg;
  }
}

.group-title {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  margin-bottom: $spacing-md;
}

.title-icon {
  font-size: 28rpx;
}

.title-text {
  font-size: $font-base;
  font-weight: $font-medium;
  color: var(--text-primary);
}

.form-row {
  display: flex;
  gap: $spacing-md;
}

.form-item {
  flex: 1;
}

.form-label {
  display: block;
  font-size: $font-sm;
  color: var(--text-secondary);
  margin-bottom: $spacing-xs;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: var(--bg-primary);
  border-radius: $radius-md;
  padding: 0 $spacing-md;
  height: 88rpx;
  margin-bottom: 8rpx;
}

.form-input {
  flex: 1;
  font-size: $font-base;
  color: var(--text-primary);
  
  &::placeholder {
    color: var(--text-muted);
  }
}

.input-unit {
  font-size: $font-sm;
  color: var(--text-secondary);
  margin-left: $spacing-xs;
}

.form-hint {
  font-size: $font-xs;
  color: var(--text-muted);
}

// 提示信息
.form-tips {
  display: flex;
  align-items: flex-start;
  gap: $spacing-sm;
  padding: $spacing-md;
  background: rgba(59, 130, 246, 0.1);
  border-radius: $radius-md;
}

.tip-icon {
  font-size: 28rpx;
  flex-shrink: 0;
}

.tip-text {
  font-size: $font-sm;
  color: var(--info-color);
  line-height: $line-height-normal;
}

// 操作按钮
.actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  gap: $spacing-md;
  padding: $spacing-lg;
  padding-bottom: calc($spacing-lg + $safe-area-bottom);
  background: var(--bg-card);
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.08);
}

.btn {
  flex: 1;
  height: 96rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-xs;
  border-radius: $radius-lg;
  font-weight: $font-medium;
  transition: all $transition-fast;
  
  &:active {
    transform: scale(0.98);
  }
}

.btn-icon {
  font-size: 32rpx;
}

.btn-text {
  font-size: $font-md;
}

.btn-delete {
  background: rgba(239, 68, 68, 0.1);
  
  .btn-text {
    color: var(--danger-color);
  }
}

.btn-save {
  background: $primary-gradient;
  flex: 2;
  
  .btn-text {
    color: #ffffff;
  }
}

// 涨跌颜色
.text-up {
  color: var(--up-color) !important;
}

.text-down {
  color: var(--down-color) !important;
}
</style>
