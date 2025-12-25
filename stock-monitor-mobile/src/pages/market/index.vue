<template>
  <view class="market-page">
    <!-- 市场统计卡片 -->
    <view class="stats-section">
      <view class="stats-grid">
        <StatCard 
          icon="📊" 
          :value="marketStats.total_stocks" 
          label="总股票数" 
          gradient="primary"
        />
        <StatCard 
          icon="📈" 
          :value="marketStats.up_stocks" 
          :label="`上涨 (${marketStats.up_ratio}%)`" 
          gradient="danger"
        />
        <StatCard 
          icon="📉" 
          :value="marketStats.down_stocks" 
          :label="`下跌 (${marketStats.down_ratio}%)`" 
          gradient="success"
        />
        <StatCard 
          icon="➖" 
          :value="marketStats.flat_stocks" 
          label="平盘" 
          gradient="info"
        />
      </view>
      
      <!-- 涨跌停统计 -->
      <view class="limit-grid">
        <view class="limit-card limit-up">
          <text class="limit-icon">🔥</text>
          <view class="limit-info">
            <text class="limit-value">{{ marketStats.limit_up }}</text>
            <text class="limit-label">涨停</text>
          </view>
        </view>
        <view class="limit-card limit-down">
          <text class="limit-icon">❄️</text>
          <view class="limit-info">
            <text class="limit-value">{{ marketStats.limit_down }}</text>
            <text class="limit-label">跌停</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 标签页 -->
    <view class="tabs-section">
      <view class="tabs-header">
        <view 
          class="tab-item" 
          :class="{ active: activeTab === 'hot' }"
          @click="activeTab = 'hot'"
        >
          <text>热门股票</text>
        </view>
        <view 
          class="tab-item" 
          :class="{ active: activeTab === 'sectors' }"
          @click="activeTab = 'sectors'"
        >
          <text>行业板块</text>
        </view>
        <view 
          class="tab-item" 
          :class="{ active: activeTab === 'lhb' }"
          @click="activeTab = 'lhb'"
        >
          <text>龙虎榜</text>
        </view>
      </view>
      
      <!-- 热门股票内容 -->
      <scroll-view 
        v-show="activeTab === 'hot'" 
        class="tab-content"
        scroll-y
        :refresher-enabled="true"
        :refresher-triggered="refreshing"
        @refresherrefresh="onRefresh"
      >
        <LoadingSkeleton v-if="loading" type="ranking" :count="3" />
        <view v-else class="hot-stocks">
          <!-- 涨幅榜 -->
          <RankingList 
            title="涨幅排行" 
            icon="🚀" 
            :items="topGainers"
            @itemClick="handleStockClick"
          />
          
          <!-- 跌幅榜 -->
          <RankingList 
            title="跌幅排行" 
            icon="📉" 
            :items="topLosers"
            @itemClick="handleStockClick"
          />
          
          <!-- 成交额榜 -->
          <RankingList 
            title="成交额排行" 
            icon="💰" 
            :items="topVolume"
            @itemClick="handleStockClick"
          />
        </view>
      </scroll-view>
      
      <!-- 行业板块内容 -->
      <scroll-view 
        v-show="activeTab === 'sectors'" 
        class="tab-content"
        scroll-y
        :refresher-enabled="true"
        :refresher-triggered="refreshing"
        @refresherrefresh="onRefresh"
      >
        <LoadingSkeleton v-if="sectorLoading" type="list" :count="10" />
        <view v-else class="sectors-content">
          <!-- 行业板块 -->
          <view class="sector-card">
            <view class="sector-header">
              <text class="sector-icon">🏭</text>
              <text class="sector-title">行业板块</text>
              <view class="sector-tag">TOP 10</view>
            </view>
            <view class="sector-list">
              <view 
                class="sector-item" 
                v-for="(item, index) in industries.slice(0, 10)" 
                :key="index"
              >
                <view class="sector-rank" :class="getRankClass(index)">
                  {{ index + 1 }}
                </view>
                <view class="sector-info">
                  <text class="sector-name">{{ item.板块名称 }}</text>
                  <text class="sector-leader">领涨: {{ item.领涨股票 || '--' }}</text>
                </view>
                <view class="sector-data">
                  <text class="sector-change" :class="getChangeClass(item.涨跌幅)">
                    {{ formatChange(item.涨跌幅) }}
                  </text>
                  <text class="sector-count">
                    <text class="up-count">↑{{ item.上涨家数 || 0 }}</text>
                    <text class="down-count">↓{{ item.下跌家数 || 0 }}</text>
                  </text>
                </view>
              </view>
            </view>
          </view>
          
          <!-- 概念板块 -->
          <view class="sector-card">
            <view class="sector-header">
              <text class="sector-icon">💡</text>
              <text class="sector-title">概念板块</text>
              <view class="sector-tag concept">TOP 10</view>
            </view>
            <view class="sector-list">
              <view 
                class="sector-item" 
                v-for="(item, index) in concepts.slice(0, 10)" 
                :key="index"
              >
                <view class="sector-rank" :class="getRankClass(index)">
                  {{ index + 1 }}
                </view>
                <view class="sector-info">
                  <text class="sector-name">{{ item.板块名称 }}</text>
                  <text class="sector-leader">领涨: {{ item.领涨股票 || '--' }}</text>
                </view>
                <view class="sector-data">
                  <text class="sector-change" :class="getChangeClass(item.涨跌幅)">
                    {{ formatChange(item.涨跌幅) }}
                  </text>
                  <text class="sector-count">
                    <text class="up-count">↑{{ item.上涨家数 || 0 }}</text>
                    <text class="down-count">↓{{ item.下跌家数 || 0 }}</text>
                  </text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>
      
      <!-- 龙虎榜内容 -->
      <scroll-view 
        v-show="activeTab === 'lhb'" 
        class="tab-content"
        scroll-y
        :refresher-enabled="true"
        :refresher-triggered="refreshing"
        @refresherrefresh="onRefresh"
      >
        <LoadingSkeleton v-if="lhbLoading" type="list" :count="10" />
        <view v-else class="lhb-content">
          <view class="lhb-card">
            <view class="lhb-header">
              <text class="lhb-icon">🐉</text>
              <text class="lhb-title">龙虎榜</text>
              <view class="lhb-tag">近一月</view>
            </view>
            <view class="lhb-list">
              <view 
                class="lhb-item" 
                v-for="(item, index) in lhbData.slice(0, 20)" 
                :key="index"
                @click="handleLhbClick(item)"
              >
                <view class="lhb-rank" :class="getRankClass(index)">
                  {{ index + 1 }}
                </view>
                <view class="lhb-info">
                  <text class="lhb-name">{{ item.名称 }}</text>
                  <text class="lhb-code">{{ item.代码 }}</text>
                </view>
                <view class="lhb-data">
                  <text class="lhb-change" :class="getChangeClass(item.涨跌幅)">
                    {{ formatChange(item.涨跌幅) }}
                  </text>
                  <text class="lhb-amount" :class="getChangeClass(item.龙虎榜净买额)">
                    {{ formatMoney(item.龙虎榜净买额) }}
                  </text>
                </view>
                <view class="lhb-times">
                  <text class="times-value">{{ item.上榜次数 }}</text>
                  <text class="times-label">次</text>
                </view>
              </view>
            </view>
          </view>
          
          <!-- 空状态 -->
          <view class="empty-state" v-if="lhbData.length === 0">
            <text class="empty-icon">📭</text>
            <text class="empty-text">暂无龙虎榜数据</text>
          </view>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import StatCard from '@/components/StatCard.vue'
import RankingList from '@/components/RankingList.vue'
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'
import { enhancedApi } from '@/api'
import type { RankingItem } from '@/types'

// 状态
const activeTab = ref('hot')
const loading = ref(false)
const sectorLoading = ref(false)
const lhbLoading = ref(false)
const refreshing = ref(false)

// 市场统计数据
const marketStats = ref({
  total_stocks: 0,
  up_stocks: 0,
  down_stocks: 0,
  flat_stocks: 0,
  limit_up: 0,
  limit_down: 0,
  up_ratio: 0,
  down_ratio: 0
})

// 热门股票数据
const topGainers = ref<RankingItem[]>([])
const topLosers = ref<RankingItem[]>([])
const topVolume = ref<RankingItem[]>([])

// 板块数据
const industries = ref<any[]>([])
const concepts = ref<any[]>([])

// 龙虎榜数据
const lhbData = ref<any[]>([])

// 自动刷新定时器
let refreshTimer: number | null = null

onMounted(async () => {
  await loadAllData()
  // 每60秒自动刷新
  refreshTimer = setInterval(() => {
    loadAllData()
  }, 60000) as unknown as number
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})

// 加载所有数据
async function loadAllData() {
  await Promise.all([
    loadMarketOverview(),
    loadSectors(),
    loadLhbData()
  ])
}

// 加载市场概况
async function loadMarketOverview() {
  loading.value = true
  try {
    const data = await enhancedApi.getMarketOverview()
    marketStats.value = data.market_stats || marketStats.value
    topGainers.value = data.top_gainers || []
    topLosers.value = data.top_losers || []
    topVolume.value = data.top_volume || []
  } catch (error) {
    console.error('加载市场概况失败:', error)
    uni.showToast({ title: '加载市场数据失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

// 加载板块数据
async function loadSectors() {
  sectorLoading.value = true
  try {
    const data = await enhancedApi.getSectors()
    industries.value = data.industries || []
    concepts.value = data.concepts || []
  } catch (error) {
    console.error('加载板块数据失败:', error)
  } finally {
    sectorLoading.value = false
  }
}

// 加载龙虎榜数据
async function loadLhbData() {
  lhbLoading.value = true
  try {
    const data = await enhancedApi.getLhb()
    lhbData.value = data.lhb_data || []
  } catch (error) {
    console.error('加载龙虎榜数据失败:', error)
  } finally {
    lhbLoading.value = false
  }
}

// 下拉刷新
async function onRefresh() {
  refreshing.value = true
  await loadAllData()
  refreshing.value = false
}

// 获取排名样式类
function getRankClass(index: number): string {
  if (index === 0) return 'rank-gold'
  if (index === 1) return 'rank-silver'
  if (index === 2) return 'rank-bronze'
  return ''
}

// 获取涨跌颜色类
function getChangeClass(value?: number): string {
  if (!value && value !== 0) return ''
  return value >= 0 ? 'text-up' : 'text-down'
}

// 格式化涨跌幅
function formatChange(value?: number): string {
  if (!value && value !== 0) return '--'
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

// 格式化金额
function formatMoney(amount?: number): string {
  if (!amount && amount !== 0) return '--'
  if (Math.abs(amount) >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  }
  if (Math.abs(amount) >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toFixed(2)
}

// 点击股票
function handleStockClick(item: RankingItem) {
  // 跳转到股票详情页
  uni.navigateTo({
    url: `/pages/stock-detail/index?code=${item.代码}&name=${encodeURIComponent(item.名称)}`
  })
}

// 点击龙虎榜项
function handleLhbClick(item: any) {
  uni.navigateTo({
    url: `/pages/stock-detail/index?code=${item.代码}&name=${encodeURIComponent(item.名称)}`
  })
}
</script>


<style lang="scss" scoped>
@import '@/styles/variables.scss';

.market-page {
  min-height: 100vh;
  background: var(--bg-primary);
  padding-bottom: calc($tabbar-height + $safe-area-bottom);
}

// 统计区域
.stats-section {
  padding: $spacing-lg;
  background: var(--bg-card);
  margin-bottom: $spacing-sm;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $spacing-md;
  margin-bottom: $spacing-lg;
}

// 涨跌停卡片
.limit-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $spacing-md;
}

.limit-card {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  padding: $spacing-lg;
  border-radius: $radius-lg;
  color: #ffffff;
}

.limit-up {
  background: linear-gradient(135deg, var(--up-color) 0%, #dc2626 100%);
}

.limit-down {
  background: linear-gradient(135deg, var(--down-color) 0%, #16a34a 100%);
}

.limit-icon {
  font-size: 48rpx;
}

.limit-info {
  display: flex;
  align-items: baseline;
  gap: $spacing-xs;
}

.limit-value {
  font-size: $font-2xl;
  font-weight: $font-bold;
}

.limit-label {
  font-size: $font-base;
  opacity: 0.9;
}

// 标签页区域
.tabs-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.tabs-header {
  display: flex;
  background: var(--bg-card);
  padding: $spacing-sm;
  gap: $spacing-xs;
}

.tab-item {
  flex: 1;
  padding: $spacing-md $spacing-sm;
  text-align: center;
  font-size: $font-base;
  font-weight: $font-medium;
  color: var(--text-secondary);
  border-radius: $radius-md;
  transition: all $transition-fast;
  
  &.active {
    background: $primary-gradient;
    color: #ffffff;
  }
}

.tab-content {
  flex: 1;
  height: calc(100vh - 500rpx - $tabbar-height);
}

// 热门股票
.hot-stocks {
  padding: $spacing-lg;
  display: flex;
  flex-direction: column;
  gap: $spacing-lg;
}

// 板块内容
.sectors-content {
  padding: $spacing-lg;
  display: flex;
  flex-direction: column;
  gap: $spacing-lg;
}

.sector-card {
  background: var(--bg-card);
  border-radius: $radius-lg;
  padding: $spacing-lg;
  box-shadow: var(--shadow-sm);
}

.sector-header {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-md;
  padding-bottom: $spacing-md;
  border-bottom: 1rpx solid var(--border-color);
}

.sector-icon {
  font-size: 40rpx;
}

.sector-title {
  flex: 1;
  font-size: $font-md;
  font-weight: $font-semibold;
  color: var(--text-primary);
}

.sector-tag {
  padding: 4rpx 16rpx;
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning-color);
  font-size: $font-xs;
  border-radius: $radius-full;
  
  &.concept {
    background: rgba(102, 126, 234, 0.1);
    color: var(--primary-color);
  }
}

.sector-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.sector-item {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  padding: $spacing-sm;
  background: var(--bg-primary);
  border-radius: $radius-md;
}

.sector-rank {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: var(--text-muted);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-sm;
  font-weight: $font-semibold;
  flex-shrink: 0;
}

.rank-gold {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
}

.rank-silver {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
}

.rank-bronze {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
}

.sector-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
  min-width: 0;
}

.sector-name {
  font-size: $font-base;
  font-weight: $font-medium;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sector-leader {
  font-size: $font-xs;
  color: var(--text-secondary);
}

.sector-data {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4rpx;
}

.sector-change {
  font-size: $font-base;
  font-weight: $font-semibold;
}

.sector-count {
  font-size: $font-xs;
  display: flex;
  gap: $spacing-xs;
}

.up-count {
  color: var(--up-color);
}

.down-count {
  color: var(--down-color);
}

// 龙虎榜内容
.lhb-content {
  padding: $spacing-lg;
}

.lhb-card {
  background: var(--bg-card);
  border-radius: $radius-lg;
  padding: $spacing-lg;
  box-shadow: var(--shadow-sm);
  border-left: 8rpx solid var(--up-color);
}

.lhb-header {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-md;
  padding-bottom: $spacing-md;
  border-bottom: 1rpx solid var(--border-color);
}

.lhb-icon {
  font-size: 40rpx;
}

.lhb-title {
  flex: 1;
  font-size: $font-md;
  font-weight: $font-semibold;
  color: var(--text-primary);
}

.lhb-tag {
  padding: 4rpx 16rpx;
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
  font-size: $font-xs;
  border-radius: $radius-full;
}

.lhb-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.lhb-item {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  padding: $spacing-sm;
  background: var(--bg-primary);
  border-radius: $radius-md;
  transition: all $transition-fast;
  
  &:active {
    background: var(--bg-secondary);
  }
}

.lhb-rank {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: var(--text-muted);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-sm;
  font-weight: $font-semibold;
  flex-shrink: 0;
}

.lhb-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
  min-width: 0;
}

.lhb-name {
  font-size: $font-base;
  font-weight: $font-medium;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lhb-code {
  font-size: $font-xs;
  color: var(--text-secondary);
}

.lhb-data {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4rpx;
}

.lhb-change {
  font-size: $font-base;
  font-weight: $font-semibold;
}

.lhb-amount {
  font-size: $font-xs;
}

.lhb-times {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 $spacing-sm;
  border-left: 1rpx solid var(--border-color);
}

.times-value {
  font-size: $font-md;
  font-weight: $font-bold;
  color: var(--primary-color);
}

.times-label {
  font-size: $font-xs;
  color: var(--text-secondary);
}

// 涨跌颜色
.text-up {
  color: var(--up-color);
}

.text-down {
  color: var(--down-color);
}

// 空状态
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $spacing-2xl;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: $spacing-md;
}

.empty-text {
  font-size: $font-base;
  color: var(--text-muted);
}
</style>
