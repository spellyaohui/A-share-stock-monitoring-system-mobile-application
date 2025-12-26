<template>
  <view class="edit-page">
    <!-- 加载状态 -->
    <view class="loading-overlay" v-if="loading">
      <view class="loading-spinner"></view>
      <text class="loading-text">加载中...</text>
    </view>
    
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
import { ref, reactive } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { stockApi, monitorApi } from '../../api'
import type { StockInfo } from '../../types'

// 获取页面参数
const stockId = ref(0)
const stockInfo = ref<StockInfo>({} as StockInfo)
const monitorId = ref<number | null>(null)
const currentPrice = ref<number | null>(null)
const priceChange = ref<number | null>(null)
const loading = ref(true)

const form = reactive({
  stock_id: 0,
  price_min: '',
  price_max: '',
  rise_threshold: '',
  fall_threshold: ''
})

onLoad((options) => {
  console.log('monitor-edit 页面参数:', options)
  
  if (options?.stockId) {
    stockId.value = parseInt(options.stockId)
    form.stock_id = stockId.value
    loadData()
  } else {
    loading.value = false
    uni.showToast({ title: '参数错误', icon: 'none' })
  }
})

async function loadData() {
  loading.value = true
  try {
    // 先加载监测信息（包含股票信息和实时价格）
    await loadMonitorInfo()
    
    // 如果监测信息中没有股票信息，再单独获取
    if (!stockInfo.value.name) {
      await loadStockInfo()
    }
  } finally {
    loading.value = false
  }
}

async function loadStockInfo() {
  try {
    // 尝试从 getDetail 获取
    const res = await stockApi.getDetail(stockId.value)
    if (res && res.name) {
      stockInfo.value = res
    }
    
    // 获取实时价格
    if (!currentPrice.value) {
      try {
        const realtime = await stockApi.getRealtime(stockId.value)
        if (realtime && realtime.price) {
          currentPrice.value = realtime.price
          priceChange.value = realtime.change_percent
        }
      } catch (e) {
        console.error('获取实时价格失败:', e)
      }
    }
  } catch (error) {
    console.error('加载股票信息失败:', error)
    // 不显示错误提示，因为可能已经从监测列表获取了信息
  }
}

async function loadMonitorInfo() {
  try {
    const res = await monitorApi.getList()
    console.log('监测列表:', res)
    const monitor = res.find((m: any) => m.stock_id === stockId.value)
    console.log('找到的监测:', monitor)
    
    if (monitor) {
      // 设置监测ID
      monitorId.value = monitor.id
      
      // 从监测数据中获取股票信息
      if (monitor.stock) {
        stockInfo.value = {
          id: monitor.stock.id,
          code: monitor.stock.code,
          name: monitor.stock.name,
          market: monitor.stock.market || '',
          full_code: monitor.stock.full_code || ''
        } as StockInfo
      }
      
      // 从监测数据中获取实时价格
      if (monitor.current_price || monitor.price) {
        currentPrice.value = monitor.current_price || monitor.price
        priceChange.value = monitor.change_percent
      }
      
      // 设置表单数据
      form.price_min = monitor.price_min?.toString() || ''
      form.price_max = monitor.price_max?.toString() || ''
      form.rise_threshold = monitor.rise_threshold?.toString() || ''
      form.fall_threshold = monitor.fall_threshold?.toString() || ''
      console.log('表单数据:', form)
    } else {
      console.log('未找到该股票的监测配置，这是新增监测')
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
@import '../../styles/variables.scss';

.edit-page {
  min-height: 100vh;
  background: var(--bg-primary);
  padding-bottom: 200rpx;
}

// 加载状态
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.loading-spinner {
  width: 60rpx;
  height: 60rpx;
  border: 4rpx solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 24rpx;
  font-size: 28rpx;
  color: var(--text-secondary);
}

// 股票头部
.stock-header {
  display: flex;
  align-items: center;
  padding: 48rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  gap: 24rpx;
}

.stock-icon {
  width: 88rpx;
  height: 88rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 24rpx;
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
  font-size: 36rpx;
  font-weight: 700;
  color: #ffffff;
}

.stock-code {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

.stock-price {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4rpx;
}

.price-value {
  font-size: 44rpx;
  font-weight: 700;
  color: #ffffff;
}

.price-change {
  font-size: 24rpx;
  padding: 4rpx 12rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8rpx;
  color: #ffffff;
}

// 表单区域
.form-section {
  margin: 32rpx;
  background: var(--bg-card);
  border-radius: 32rpx;
  padding: 32rpx;
  box-shadow: var(--shadow-sm);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 32rpx;
  padding-bottom: 24rpx;
  border-bottom: 1rpx solid var(--border-color);
}

.section-icon {
  font-size: 36rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: var(--text-primary);
}

// 表单组
.form-group {
  margin-bottom: 48rpx;
  
  &:last-of-type {
    margin-bottom: 32rpx;
  }
}

.group-title {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 24rpx;
}

.title-icon {
  font-size: 28rpx;
}

.title-text {
  font-size: 28rpx;
  font-weight: 500;
  color: var(--text-primary);
}

.form-row {
  display: flex;
  gap: 24rpx;
}

.form-item {
  flex: 1;
}

.form-label {
  display: block;
  font-size: 24rpx;
  color: var(--text-secondary);
  margin-bottom: 8rpx;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: var(--bg-primary);
  border-radius: 16rpx;
  padding: 0 24rpx;
  height: 88rpx;
  margin-bottom: 8rpx;
}

.form-input {
  flex: 1;
  font-size: 28rpx;
  color: var(--text-primary);
  
  &::placeholder {
    color: var(--text-muted);
  }
}

.input-unit {
  font-size: 24rpx;
  color: var(--text-secondary);
  margin-left: 8rpx;
}

.form-hint {
  font-size: 22rpx;
  color: var(--text-muted);
}

// 提示信息
.form-tips {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
  padding: 24rpx;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 16rpx;
}

.tip-icon {
  font-size: 28rpx;
  flex-shrink: 0;
}

.tip-text {
  font-size: 24rpx;
  color: var(--info-color);
  line-height: 1.5;
}

// 操作按钮
.actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  gap: 24rpx;
  padding: 32rpx;
  padding-bottom: calc(32rpx + env(safe-area-inset-bottom));
  background: var(--bg-card);
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.08);
}

.btn {
  flex: 1;
  height: 96rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  border-radius: 24rpx;
  font-weight: 500;
  transition: all 0.15s ease;
  
  &:active {
    transform: scale(0.98);
  }
}

.btn-icon {
  font-size: 32rpx;
}

.btn-text {
  font-size: 32rpx;
}

.btn-delete {
  background: rgba(239, 68, 68, 0.1);
  
  .btn-text {
    color: var(--danger-color);
  }
}

.btn-save {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

// 暗黑模式适配
@media (prefers-color-scheme: dark) {
  .stock-header {
    background: linear-gradient(135deg, #1e1e2e 0%, #313244 100%);
  }
  
  .btn-save {
    background: linear-gradient(135deg, #89b4fa 0%, #b4befe 100%);
  }
  
  .actions {
    box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.3);
  }
}
</style>
