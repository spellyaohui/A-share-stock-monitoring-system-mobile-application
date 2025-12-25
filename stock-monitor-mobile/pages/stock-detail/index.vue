<template>
  <view class="detail-page">
    <!-- 自定义导航栏 -->
    <view class="nav-bar">
      <view class="nav-back" @click="goBack">
        <text>‹</text>
      </view>
      <view class="nav-title">股票详情</view>
      <view class="nav-action" @click="refreshData">
        <text>🔄</text>
      </view>
    </view>
    
    <!-- 股票头部信息 -->
    <view class="stock-header" :class="getHeaderClass()">
      <view class="header-main">
        <view class="stock-info">
          <text class="stock-name">{{ stockInfo.name || '加载中...' }}</text>
          <text class="stock-code">{{ stockInfo.code || '--' }}</text>
        </view>
        <view class="stock-price">
          <text class="price-value">{{ formatPrice(realtime.price) }}</text>
          <view class="price-change">
            <text class="change-amount">{{ formatChangeAmount() }}</text>
            <text class="change-percent">{{ formatChange(realtime.change_percent) }}</text>
          </view>
        </view>
      </view>
      <view class="header-stats">
        <view class="stat-item">
          <text class="stat-label">今开</text>
          <text class="stat-value">{{ formatPrice(realtime.open) }}</text>
        </view>
        <view class="stat-item">
          <text class="stat-label">最高</text>
          <text class="stat-value text-up">{{ formatPrice(realtime.high) }}</text>
        </view>
        <view class="stat-item">
          <text class="stat-label">最低</text>
          <text class="stat-value text-down">{{ formatPrice(realtime.low) }}</text>
        </view>
        <view class="stat-item">
          <text class="stat-label">昨收</text>
          <text class="stat-value">{{ formatPrice(realtime.pre_close) }}</text>
        </view>
      </view>
    </view>

    <!-- 标签页 -->
    <view class="tabs-section">
      <view class="tabs-header">
        <view 
          class="tab-item" 
          :class="{ active: activeTab === 'basic' }"
          @click="activeTab = 'basic'"
        >
          <text>基本信息</text>
        </view>
        <view 
          class="tab-item" 
          :class="{ active: activeTab === 'financial' }"
          @click="activeTab = 'financial'; loadFinancial()"
        >
          <text>财务数据</text>
        </view>
        <view 
          class="tab-item" 
          :class="{ active: activeTab === 'fund' }"
          @click="activeTab = 'fund'; loadFundFlow()"
        >
          <text>资金流向</text>
        </view>
      </view>
      
      <!-- 基本信息 -->
      <scroll-view 
        v-show="activeTab === 'basic'" 
        class="tab-content"
        scroll-y
      >
        <view class="basic-content">
          <!-- 行情数据 -->
          <view class="info-card">
            <view class="card-header">
              <text class="card-icon">📊</text>
              <text class="card-title">行情数据</text>
            </view>
            <view class="info-grid">
              <view class="info-item">
                <text class="info-label">成交量</text>
                <text class="info-value">{{ formatVolume(realtime.volume) }}</text>
              </view>
              <view class="info-item">
                <text class="info-label">成交额</text>
                <text class="info-value">{{ formatMoney(realtime.amount) }}</text>
              </view>
              <view class="info-item">
                <text class="info-label">振幅</text>
                <text class="info-value">{{ formatPercent(realtime.amplitude) }}</text>
              </view>
              <view class="info-item">
                <text class="info-label">换手率</text>
                <text class="info-value">{{ formatPercent(realtime.turnover_rate) }}</text>
              </view>
            </view>
          </view>
          
          <!-- K线周期选择 -->
          <view class="info-card">
            <view class="card-header">
              <text class="card-icon">📈</text>
              <text class="card-title">K线图</text>
              <view class="period-tabs">
                <view 
                  class="period-tab" 
                  :class="{ active: period === 'day' }"
                  @click="changePeriod('day')"
                >日K</view>
                <view 
                  class="period-tab" 
                  :class="{ active: period === 'week' }"
                  @click="changePeriod('week')"
                >周K</view>
                <view 
                  class="period-tab" 
                  :class="{ active: period === 'month' }"
                  @click="changePeriod('month')"
                >月K</view>
              </view>
            </view>
            <view class="chart-placeholder" v-if="chartLoading">
              <view class="loading-spinner"></view>
              <text class="loading-text">加载K线数据...</text>
            </view>
            <view class="kline-summary" v-else>
              <view class="kline-item" v-for="(item, index) in klineSummary" :key="index">
                <text class="kline-date">{{ item.date }}</text>
                <text class="kline-price" :class="item.change >= 0 ? 'text-up' : 'text-down'">
                  {{ item.close.toFixed(2) }}
                </text>
                <text class="kline-change" :class="item.change >= 0 ? 'text-up' : 'text-down'">
                  {{ item.change >= 0 ? '+' : '' }}{{ item.change.toFixed(2) }}%
                </text>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>
      
      <!-- 财务数据 -->
      <scroll-view 
        v-show="activeTab === 'financial'" 
        class="tab-content"
        scroll-y
      >
        <LoadingSkeleton v-if="financialLoading" type="detail" />
        <view v-else class="financial-content">
          <view class="info-card">
            <view class="card-header">
              <text class="card-icon">💰</text>
              <text class="card-title">估值指标</text>
            </view>
            <view class="info-grid">
              <view class="info-item">
                <text class="info-label">市盈率(动态)</text>
                <text class="info-value">{{ financial.basic_info?.市盈率?.toFixed(2) || '--' }}</text>
              </view>
              <view class="info-item">
                <text class="info-label">市净率</text>
                <text class="info-value">{{ financial.basic_info?.市净率?.toFixed(2) || '--' }}</text>
              </view>
              <view class="info-item">
                <text class="info-label">总市值</text>
                <text class="info-value">{{ formatMoney(financial.basic_info?.总市值) }}</text>
              </view>
              <view class="info-item">
                <text class="info-label">流通市值</text>
                <text class="info-value">{{ formatMoney(financial.basic_info?.流通市值) }}</text>
              </view>
            </view>
          </view>
          
          <view class="info-card">
            <view class="card-header">
              <text class="card-icon">📋</text>
              <text class="card-title">基本信息</text>
            </view>
            <view class="info-list">
              <view class="list-item">
                <text class="list-label">所属行业</text>
                <text class="list-value">{{ financial.basic_info?.行业 || '--' }}</text>
              </view>
              <view class="list-item">
                <text class="list-label">总股本</text>
                <text class="list-value">{{ formatVolume(financial.basic_info?.总股本) }}</text>
              </view>
              <view class="list-item">
                <text class="list-label">流通股</text>
                <text class="list-value">{{ formatVolume(financial.basic_info?.流通股) }}</text>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>
      
      <!-- 资金流向 -->
      <scroll-view 
        v-show="activeTab === 'fund'" 
        class="tab-content"
        scroll-y
      >
        <LoadingSkeleton v-if="fundFlowLoading" type="list" :count="5" />
        <view v-else class="fund-content">
          <view class="info-card">
            <view class="card-header">
              <text class="card-icon">💹</text>
              <text class="card-title">近5日资金流向</text>
            </view>
            <view class="fund-list" v-if="fundFlow.length > 0">
              <view class="fund-item" v-for="(item, index) in fundFlow.slice(0, 5)" :key="index">
                <view class="fund-date">{{ item.日期 }}</view>
                <view class="fund-data">
                  <view class="fund-row">
                    <text class="fund-label">主力净流入</text>
                    <text class="fund-value" :class="getFlowClass(item['主力净流入-净额'])">
                      {{ formatMoney(item['主力净流入-净额']) }}
                    </text>
                  </view>
                  <view class="fund-row">
                    <text class="fund-label">净占比</text>
                    <text class="fund-value" :class="getFlowClass(item['主力净流入-净占比'])">
                      {{ item['主力净流入-净占比']?.toFixed(2) || '--' }}%
                    </text>
                  </view>
                </view>
              </view>
            </view>
            <view class="empty-state" v-else>
              <text class="empty-icon">📭</text>
              <text class="empty-text">暂无资金流向数据</text>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar">
      <view class="btn btn-detail" @click="goToMonitorEdit">
        <text class="btn-icon">➕</text>
        <text class="btn-text">添加监测</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import LoadingSkeleton from '../../components/LoadingSkeleton.vue'
import { stockApi, enhancedApi } from '../../api'
import type { StockInfo, StockRealtime } from '../../types'

// 页面参数
const stockCode = ref('')
const stockName = ref('')
const stockId = ref(0)

// 数据
const stockInfo = ref<StockInfo>({} as StockInfo)
const realtime = ref<StockRealtime>({} as StockRealtime)
const financial = ref<any>({})
const fundFlow = ref<any[]>([])
const klineSummary = ref<any[]>([])

// 状态
const activeTab = ref('basic')
const period = ref('day')
const chartLoading = ref(false)
const financialLoading = ref(false)
const fundFlowLoading = ref(false)

// 定时器
let refreshTimer: number | null = null

onMounted(() => {
  // 获取页面参数
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  const options = currentPage.options || {}
  
  stockCode.value = options.code || ''
  stockName.value = decodeURIComponent(options.name || '')
  
  // 设置初始信息
  stockInfo.value = {
    id: 0,
    code: stockCode.value,
    name: stockName.value
  } as StockInfo
  
  loadData()
  
  // 每30秒刷新实时数据
  refreshTimer = setInterval(() => {
    loadRealtime()
  }, 30000) as unknown as number
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})

async function loadData() {
  await loadStockInfo()
  await loadRealtime()
  await loadKline()
}

async function loadStockInfo() {
  try {
    // 通过搜索获取股票ID
    const results = await stockApi.search(stockCode.value)
    if (results && results.length > 0) {
      const stock = results.find(s => s.code === stockCode.value) || results[0]
      stockInfo.value = stock
      stockId.value = stock.id
    }
  } catch (error) {
    console.error('加载股票信息失败:', error)
  }
}

async function loadRealtime() {
  if (!stockId.value) return
  try {
    const res = await stockApi.getRealtime(stockId.value)
    realtime.value = res
  } catch (error) {
    console.error('加载实时数据失败:', error)
  }
}

async function loadKline() {
  if (!stockId.value) return
  chartLoading.value = true
  try {
    const res = await stockApi.getKline(stockId.value, period.value, 10)
    if (res && res.klines) {
      klineSummary.value = res.klines.slice(-5).reverse().map((item: any) => ({
        date: item.date,
        close: item.close,
        change: ((item.close - item.open) / item.open) * 100
      }))
    }
  } catch (error) {
    console.error('加载K线数据失败:', error)
  } finally {
    chartLoading.value = false
  }
}

async function loadFinancial() {
  if (!stockCode.value || financial.value.basic_info) return
  financialLoading.value = true
  try {
    const res = await enhancedApi.getStockFinancial(stockCode.value)
    financial.value = res
  } catch (error) {
    console.error('加载财务数据失败:', error)
  } finally {
    financialLoading.value = false
  }
}

async function loadFundFlow() {
  if (!stockCode.value || fundFlow.value.length > 0) return
  fundFlowLoading.value = true
  try {
    const res = await enhancedApi.getStockFundFlow(stockCode.value)
    fundFlow.value = res.fund_flow || []
  } catch (error) {
    console.error('加载资金流向失败:', error)
  } finally {
    fundFlowLoading.value = false
  }
}

function changePeriod(p: string) {
  period.value = p
  loadKline()
}

function refreshData() {
  loadRealtime()
  loadKline()
  uni.showToast({ title: '刷新中...', icon: 'none', duration: 1000 })
}

function goBack() {
  uni.navigateBack()
}

function goToMonitorEdit() {
  if (!stockId.value) {
    uni.showToast({ title: '股票信息加载中', icon: 'none' })
    return
  }
  uni.navigateTo({
    url: `/pages/monitor-edit/index?stockId=${stockId.value}`
  })
}

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

function formatChangeAmount(): string {
  if (!realtime.value.price || !realtime.value.pre_close) return '--'
  const diff = realtime.value.price - realtime.value.pre_close
  const sign = diff >= 0 ? '+' : ''
  return `${sign}${diff.toFixed(2)}`
}

function formatVolume(volume?: number): string {
  if (!volume && volume !== 0) return '--'
  if (volume >= 100000000) return (volume / 100000000).toFixed(2) + '亿'
  if (volume >= 10000) return (volume / 10000).toFixed(2) + '万'
  return volume.toString()
}

function formatMoney(amount?: number): string {
  if (!amount && amount !== 0) return '--'
  if (Math.abs(amount) >= 100000000) return (amount / 100000000).toFixed(2) + '亿'
  if (Math.abs(amount) >= 10000) return (amount / 10000).toFixed(2) + '万'
  return amount.toFixed(2)
}

function formatPercent(value?: number): string {
  if (!value && value !== 0) return '--'
  return value.toFixed(2) + '%'
}

function getHeaderClass(): string {
  const change = realtime.value.change_percent || 0
  return change >= 0 ? 'header-up' : 'header-down'
}

function getFlowClass(value?: number): string {
  if (!value && value !== 0) return ''
  return value >= 0 ? 'text-up' : 'text-down'
}
</script>


<style lang="scss" scoped>
@import '../../styles/variables.scss';

.detail-page {
  min-height: 100vh;
  background: var(--bg-primary);
  padding-bottom: 160rpx;
}

// 自定义导航栏
.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  padding-top: calc(24rpx + 44rpx);
  background: transparent;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
}

.nav-back, .nav-action {
  width: 64rpx;
  height: 64rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  
  text {
    font-size: 40rpx;
    color: #ffffff;
  }
}

.nav-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #ffffff;
}

// 股票头部
.stock-header {
  padding: calc(44rpx + 100rpx) 32rpx 48rpx;
  transition: background 0.3s ease;
  
  &.header-up {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  }
  
  &.header-down {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  }
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32rpx;
}

.stock-info {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.stock-name {
  font-size: 44rpx;
  font-weight: 700;
  color: #ffffff;
}

.stock-code {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

.stock-price {
  text-align: right;
}

.price-value {
  font-size: 72rpx;
  font-weight: 700;
  color: #ffffff;
  display: block;
}

.price-change {
  display: flex;
  gap: 16rpx;
  justify-content: flex-end;
  margin-top: 8rpx;
}

.change-amount, .change-percent {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
  padding: 4rpx 12rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8rpx;
}

.header-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
  padding-top: 24rpx;
  border-top: 1rpx solid rgba(255, 255, 255, 0.2);
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.7);
  display: block;
  margin-bottom: 4rpx;
}

.stat-value {
  font-size: 28rpx;
  font-weight: 600;
  color: #ffffff;
}

// 标签页
.tabs-section {
  margin-top: -32rpx;
  background: var(--bg-primary);
  border-radius: 32rpx 32rpx 0 0;
  min-height: calc(100vh - 400rpx);
}

.tabs-header {
  display: flex;
  background: var(--bg-card);
  padding: 16rpx;
  border-radius: 32rpx 32rpx 0 0;
  gap: 8rpx;
}

.tab-item {
  flex: 1;
  padding: 24rpx 16rpx;
  text-align: center;
  font-size: 28rpx;
  font-weight: 500;
  color: var(--text-secondary);
  border-radius: 16rpx;
  transition: all 0.15s ease;
  
  &.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #ffffff;
  }
}

.tab-content {
  height: calc(100vh - 500rpx);
  padding: 32rpx;
}

// 信息卡片
.info-card {
  background: var(--bg-card);
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;
  box-shadow: var(--shadow-sm);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 24rpx;
  padding-bottom: 24rpx;
  border-bottom: 1rpx solid var(--border-color);
}

.card-icon {
  font-size: 36rpx;
}

.card-title {
  flex: 1;
  font-size: 32rpx;
  font-weight: 600;
  color: var(--text-primary);
}

// 信息网格
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24rpx;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
  padding: 16rpx;
  background: var(--bg-primary);
  border-radius: 16rpx;
}

.info-label {
  font-size: 22rpx;
  color: var(--text-secondary);
}

.info-value {
  font-size: 32rpx;
  font-weight: 600;
  color: var(--text-primary);
}

// 信息列表
.info-list {
  display: flex;
  flex-direction: column;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid var(--border-light);
  
  &:last-child {
    border-bottom: none;
  }
}

.list-label {
  font-size: 28rpx;
  color: var(--text-secondary);
}

.list-value {
  font-size: 28rpx;
  font-weight: 500;
  color: var(--text-primary);
}

// K线周期选择
.period-tabs {
  display: flex;
  gap: 8rpx;
}

.period-tab {
  padding: 8rpx 20rpx;
  font-size: 22rpx;
  color: var(--text-secondary);
  background: var(--bg-primary);
  border-radius: 9999rpx;
  
  &.active {
    background: var(--primary-color);
    color: #ffffff;
  }
}

// K线摘要
.kline-summary {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.kline-item {
  display: flex;
  align-items: center;
  padding: 16rpx;
  background: var(--bg-primary);
  border-radius: 16rpx;
}

.kline-date {
  flex: 1;
  font-size: 24rpx;
  color: var(--text-secondary);
}

.kline-price {
  font-size: 28rpx;
  font-weight: 600;
  margin-right: 24rpx;
}

.kline-change {
  font-size: 24rpx;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}

// 资金流向
.fund-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.fund-item {
  padding: 24rpx;
  background: var(--bg-primary);
  border-radius: 16rpx;
}

.fund-date {
  font-size: 24rpx;
  color: var(--text-secondary);
  margin-bottom: 16rpx;
}

.fund-data {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.fund-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fund-label {
  font-size: 24rpx;
  color: var(--text-secondary);
}

.fund-value {
  font-size: 28rpx;
  font-weight: 600;
}

// 加载状态
.chart-placeholder {
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
  font-size: 24rpx;
  color: var(--text-secondary);
}

// 空状态
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48rpx;
}

.empty-icon {
  font-size: 60rpx;
  margin-bottom: 16rpx;
}

.empty-text {
  font-size: 24rpx;
  color: var(--text-muted);
}

// 底部操作栏
.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 32rpx;
  padding-bottom: calc(32rpx + env(safe-area-inset-bottom));
  background: var(--bg-card);
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.08);
}

.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  height: 96rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 24rpx;
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
  font-weight: 500;
  color: #ffffff;
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
  .tab-item.active {
    background: linear-gradient(135deg, #89b4fa 0%, #b4befe 100%);
  }
  
  .btn {
    background: linear-gradient(135deg, #89b4fa 0%, #b4befe 100%);
  }
  
  .bottom-bar {
    box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.3);
  }
  
  .period-tab.active {
    background: #89b4fa;
  }
}
</style>
