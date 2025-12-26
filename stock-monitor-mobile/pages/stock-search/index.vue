<template>
  <view class="search-page">
    <!-- 搜索栏 -->
    <view class="search-header">
      <view class="search-bar">
        <view class="search-icon">🔍</view>
        <input
          class="search-input"
          v-model="keyword"
          placeholder="搜索股票代码或名称"
          :focus="true"
          @input="onSearchInput"
          @confirm="doSearch"
        />
        <view v-if="keyword" class="clear-btn" @click="clearSearch">
          <text>✕</text>
        </view>
      </view>
    </view>

    <!-- 搜索结果 -->
    <scroll-view 
      class="search-results" 
      scroll-y
      :refresher-enabled="false"
    >
      <!-- 加载中 -->
      <view class="loading-state" v-if="loading">
        <view class="loading-spinner"></view>
        <text class="loading-text">搜索中...</text>
      </view>
      
      <!-- 搜索结果列表 -->
      <view class="results-list" v-else-if="searchResults.length > 0">
        <view
          class="stock-item"
          v-for="item in searchResults"
          :key="item.id"
          @click="selectStock(item)"
        >
          <view class="stock-icon">
            <text>📈</text>
          </view>
          <view class="stock-info">
            <text class="stock-name">{{ item.name }}</text>
            <view class="stock-meta">
              <text class="stock-code">{{ item.code }}</text>
              <text class="stock-market" v-if="item.market">{{ item.market }}</text>
            </view>
          </view>
          <view class="stock-arrow">
            <text>›</text>
          </view>
        </view>
      </view>

      <!-- 空状态 - 无结果 -->
      <view class="empty-state" v-else-if="keyword && !loading">
        <text class="empty-icon">🔍</text>
        <text class="empty-title">未找到相关股票</text>
        <text class="empty-desc">请尝试其他关键词</text>
      </view>

      <!-- 空状态 - 初始 -->
      <view class="empty-state initial" v-else>
        <text class="empty-icon">💡</text>
        <text class="empty-title">搜索股票</text>
        <text class="empty-desc">输入股票代码或名称进行搜索</text>
        <view class="search-tips">
          <view class="tip-item">
            <text class="tip-label">代码搜索</text>
            <text class="tip-example">如：600519、000001</text>
          </view>
          <view class="tip-item">
            <text class="tip-label">名称搜索</text>
            <text class="tip-example">如：贵州茅台、平安银行</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 添加监测弹窗 -->
    <view class="popup-overlay" v-if="showAddPopup" @click="showAddPopup = false">
      <view class="popup-container" @click.stop>
        <!-- 弹窗头部 -->
        <view class="popup-header">
          <text class="popup-title">添加监测</text>
          <view class="popup-close" @click="showAddPopup = false">
            <text>✕</text>
          </view>
        </view>

        <!-- 选中的股票 -->
        <view class="selected-stock">
          <view class="stock-badge">📊</view>
          <view class="stock-detail">
            <text class="stock-name">{{ selectedStock?.name }}</text>
            <text class="stock-code">{{ selectedStock?.code }}</text>
          </view>
        </view>

        <!-- 表单 -->
        <view class="form-section">
          <view class="form-group">
            <view class="form-row">
              <view class="form-item">
                <text class="form-label">最低价</text>
                <view class="input-wrapper">
                  <input 
                    class="form-input" 
                    type="digit" 
                    v-model="monitorForm.price_min" 
                    placeholder="选填"
                  />
                  <text class="input-unit">元</text>
                </view>
              </view>
              <view class="form-item">
                <text class="form-label">最高价</text>
                <view class="input-wrapper">
                  <input 
                    class="form-input" 
                    type="digit" 
                    v-model="monitorForm.price_max" 
                    placeholder="选填"
                  />
                  <text class="input-unit">元</text>
                </view>
              </view>
            </view>
            <view class="form-row">
              <view class="form-item">
                <text class="form-label">涨幅阈值</text>
                <view class="input-wrapper">
                  <input 
                    class="form-input" 
                    type="digit" 
                    v-model="monitorForm.rise_threshold" 
                    placeholder="选填"
                  />
                  <text class="input-unit">%</text>
                </view>
              </view>
              <view class="form-item">
                <text class="form-label">跌幅阈值</text>
                <view class="input-wrapper">
                  <input 
                    class="form-input" 
                    type="digit" 
                    v-model="monitorForm.fall_threshold" 
                    placeholder="选填"
                  />
                  <text class="input-unit">%</text>
                </view>
              </view>
            </view>
          </view>
          
          <view class="form-tips">
            <text class="tip-icon">💡</text>
            <text class="tip-text">至少设置一个监测条件</text>
          </view>
        </view>

        <!-- 按钮 -->
        <view class="popup-actions">
          <view class="btn btn-cancel" @click="showAddPopup = false">
            <text>取消</text>
          </view>
          <view class="btn btn-confirm" @click="addMonitor">
            <text>确认添加</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { stockApi, monitorApi } from '../../api'
import type { StockInfo } from '../../types'

const keyword = ref('')
const searchResults = ref<StockInfo[]>([])
const showAddPopup = ref(false)
const selectedStock = ref<StockInfo | null>(null)
const loading = ref(false)

const monitorForm = reactive({
  stock_id: 0,
  price_min: '',
  price_max: '',
  rise_threshold: '',
  fall_threshold: ''
})

let searchTimer: number | null = null

function onSearchInput(e: any) {
  keyword.value = e.detail.value
  if (searchTimer) clearTimeout(searchTimer)
  
  if (!keyword.value.trim()) {
    searchResults.value = []
    return
  }
  
  loading.value = true
  searchTimer = setTimeout(() => {
    doSearch()
  }, 300) as unknown as number
}

async function doSearch() {
  if (!keyword.value.trim()) {
    searchResults.value = []
    loading.value = false
    return
  }

  try {
    const res = await stockApi.search(keyword.value)
    searchResults.value = res
  } catch (error) {
    console.error('搜索失败:', error)
    uni.showToast({ title: '搜索失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function clearSearch() {
  keyword.value = ''
  searchResults.value = []
}

function selectStock(item: StockInfo) {
  selectedStock.value = item
  monitorForm.stock_id = item.id
  // 重置表单
  monitorForm.price_min = ''
  monitorForm.price_max = ''
  monitorForm.rise_threshold = ''
  monitorForm.fall_threshold = ''
  showAddPopup.value = true
}

function validateForm(): string | null {
  const { price_min, price_max, rise_threshold, fall_threshold } = monitorForm
  
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

async function addMonitor() {
  const error = validateForm()
  if (error) {
    uni.showToast({ title: error, icon: 'none' })
    return
  }
  
  const data = {
    stock_id: monitorForm.stock_id,
    price_min: monitorForm.price_min ? parseFloat(monitorForm.price_min) : undefined,
    price_max: monitorForm.price_max ? parseFloat(monitorForm.price_max) : undefined,
    rise_threshold: monitorForm.rise_threshold ? parseFloat(monitorForm.rise_threshold) : undefined,
    fall_threshold: monitorForm.fall_threshold ? parseFloat(monitorForm.fall_threshold) : undefined
  }

  try {
    await monitorApi.create(data)
    uni.showToast({ title: '添加成功', icon: 'success' })
    showAddPopup.value = false
    
    // 跳转到监测中心
    setTimeout(() => {
      uni.switchTab({ url: '/pages/dashboard/index' })
    }, 1500)
  } catch (error: any) {
    uni.showToast({ title: error.detail || '添加失败', icon: 'none' })
  }
}
</script>


<style lang="scss" scoped>
@import '../../styles/variables.scss';

.search-page {
  min-height: 100vh;
  background: var(--bg-primary);
  padding-bottom: calc(100rpx + env(safe-area-inset-bottom));
}

// 搜索头部
.search-header {
  padding: 32rpx;
  background: var(--bg-card);
  box-shadow: var(--shadow-sm);
}

.search-bar {
  display: flex;
  align-items: center;
  padding: 0 32rpx;
  height: 88rpx;
  background: var(--bg-primary);
  border-radius: 9999rpx;
  gap: 16rpx;
}

.search-icon {
  font-size: 36rpx;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
  color: var(--text-primary);
  
  &::placeholder {
    color: var(--text-muted);
  }
}

.clear-btn {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--text-muted);
  border-radius: 50%;
  flex-shrink: 0;
  
  text {
    font-size: 24rpx;
    color: #ffffff;
  }
}

// 搜索结果
.search-results {
  height: calc(100vh - 150rpx - 100rpx);
  padding: 32rpx;
}

// 加载状态
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64rpx;
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

// 结果列表
.results-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.stock-item {
  display: flex;
  align-items: center;
  padding: 32rpx;
  background: var(--bg-card);
  border-radius: 24rpx;
  box-shadow: var(--shadow-sm);
  gap: 24rpx;
  transition: all 0.15s ease;
  
  &:active {
    transform: scale(0.98);
    background: var(--bg-secondary);
  }
}

.stock-icon {
  width: 80rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
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
  font-size: 32rpx;
  font-weight: 600;
  color: var(--text-primary);
}

.stock-meta {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.stock-code {
  font-size: 24rpx;
  color: var(--text-secondary);
}

.stock-market {
  padding: 4rpx 12rpx;
  background: rgba(102, 126, 234, 0.1);
  color: var(--primary-color);
  font-size: 22rpx;
  border-radius: 8rpx;
}

.stock-arrow {
  font-size: 40rpx;
  color: var(--text-muted);
  flex-shrink: 0;
}

// 空状态
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64rpx;
  
  &.initial {
    padding-top: 100rpx;
  }
}

.empty-icon {
  font-size: 100rpx;
  margin-bottom: 32rpx;
}

.empty-title {
  font-size: 36rpx;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16rpx;
}

.empty-desc {
  font-size: 28rpx;
  color: var(--text-secondary);
}

.search-tips {
  margin-top: 48rpx;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.tip-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 32rpx;
  background: var(--bg-card);
  border-radius: 16rpx;
}

.tip-label {
  font-size: 28rpx;
  color: var(--text-primary);
  font-weight: 500;
}

.tip-example {
  font-size: 24rpx;
  color: var(--text-secondary);
}

// 弹窗
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
}

.popup-container {
  width: 100%;
  max-width: 100vw;
  background: var(--bg-card);
  border-radius: 32rpx 32rpx 0 0;
  padding: 32rpx;
  padding-bottom: calc(32rpx + env(safe-area-inset-bottom));
  animation: slideUp 0.3s ease;
  box-sizing: border-box;
  overflow: hidden;
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32rpx;
}

.popup-title {
  font-size: 36rpx;
  font-weight: 700;
  color: var(--text-primary);
}

.popup-close {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  border-radius: 50%;
  
  text {
    font-size: 28rpx;
    color: var(--text-secondary);
  }
}

// 选中的股票
.selected-stock {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 32rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 24rpx;
  margin-bottom: 32rpx;
}

.stock-badge {
  width: 72rpx;
  height: 72rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
}

.stock-detail {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
  
  .stock-name {
    font-size: 32rpx;
    font-weight: 600;
    color: #ffffff;
  }
  
  .stock-code {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.8);
  }
}

// 表单
.form-section {
  margin-bottom: 32rpx;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.form-row {
  display: flex;
  gap: 24rpx;
  width: 100%;
}

.form-item {
  flex: 1;
  min-width: 0;
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
  width: 100%;
  box-sizing: border-box;
}

.form-input {
  flex: 1;
  min-width: 0;
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
  flex-shrink: 0;
}

.form-tips {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-top: 24rpx;
  padding: 16rpx 24rpx;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 12rpx;
}

.tip-icon {
  font-size: 28rpx;
}

.tip-text {
  font-size: 24rpx;
  color: var(--info-color);
}

// 按钮
.popup-actions {
  display: flex;
  gap: 24rpx;
}

.btn {
  flex: 1;
  height: 96rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 24rpx;
  font-size: 32rpx;
  font-weight: 500;
  transition: all 0.15s ease;
  
  &:active {
    transform: scale(0.98);
  }
}

.btn-cancel {
  background: var(--bg-primary);
  color: var(--text-secondary);
}

.btn-confirm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
}

// 暗黑模式适配
@media (prefers-color-scheme: dark) {
  .stock-icon {
    background: linear-gradient(135deg, #89b4fa 0%, #b4befe 100%);
  }
  
  .stock-market {
    background: rgba(137, 180, 250, 0.15);
  }
  
  .selected-stock {
    background: linear-gradient(135deg, #1e1e2e 0%, #313244 100%);
  }
  
  .btn-confirm {
    background: linear-gradient(135deg, #89b4fa 0%, #b4befe 100%);
  }
}
</style>
