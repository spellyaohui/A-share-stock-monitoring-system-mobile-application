<template>
  <el-container class="enhanced-stock-detail">
    <!-- 现代化头部 -->
    <el-header class="detail-header">
      <el-button class="back-btn" :icon="ArrowLeft" @click="router.back()">返回</el-button>
      <div class="stock-title">
        <div class="stock-name-wrapper">
          <h2>{{ stockInfo.name }}</h2>
          <span class="stock-code">{{ stockInfo.code }}</span>
        </div>
        <div class="stock-price-wrapper" :class="getChangeClass(realtime)">
          <span class="price">{{ formatPrice(realtime.price) }}</span>
          <div class="change-info">
            <span class="change-amount">{{ formatChangeAmount(realtime) }}</span>
            <span class="change-percent">{{ formatChange(realtime.change_percent) }}</span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <el-button type="primary" :icon="Star" circle />
        <el-button :icon="Refresh" circle @click="refreshAll" :loading="refreshing" />
      </div>
    </el-header>

    <el-main class="detail-main">
      <el-tabs v-model="activeTab" class="detail-tabs">
        <!-- 基本信息 -->
        <el-tab-pane label="基本信息" name="basic">
          <div class="info-cards fade-in">
            <div class="info-card" v-for="item in basicInfo" :key="item.label">
              <div class="info-label">{{ item.label }}</div>
              <div class="info-value" :class="item.class">{{ item.value }}</div>
            </div>
          </div>

          <div class="chart-section">
            <div class="chart-header">
              <span class="chart-title">K线图</span>
              <el-radio-group v-model="period" @change="loadKline" class="period-selector">
                <el-radio-button label="day">日K</el-radio-button>
                <el-radio-button label="week">周K</el-radio-button>
                <el-radio-button label="month">月K</el-radio-button>
              </el-radio-group>
            </div>
            <div class="chart-container">
              <div v-if="chartLoading" class="loading-overlay">
                <div class="chart-loading">
                  <div class="loading-spinner"></div>
                  <span class="chart-loading-text">加载K线数据...</span>
                </div>
              </div>
              <div ref="chartRef" class="chart-canvas"></div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 技术指标 -->
        <el-tab-pane label="技术指标" name="technical">
          <el-row :gutter="20" class="fade-in">
            <el-col :span="12">
              <div class="modern-card">
                <div class="card-header-modern">
                  <span class="card-title">技术指标</span>
                  <el-tag type="info" size="small">实时</el-tag>
                </div>
                <div class="indicator-grid" v-loading="technicalLoading">
                  <div class="indicator-item" v-for="(value, key) in technicalIndicators" :key="key">
                    <span class="indicator-label">{{ key }}</span>
                    <span class="indicator-value">{{ value }}</span>
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="modern-card">
                <div class="card-header-modern">
                  <span class="card-title">资金流向</span>
                  <el-tag type="warning" size="small">近5日</el-tag>
                </div>
                <el-table :data="fundFlow.slice(0, 5)" size="small" v-loading="fundFlowLoading" class="modern-table">
                  <el-table-column prop="日期" label="日期" width="100" />
                  <el-table-column prop="主力净流入-净额" label="主力净流入" width="120">
                    <template #default="{ row }">
                      <span :class="row['主力净流入-净额'] >= 0 ? 'text-up' : 'text-down'">
                        {{ formatMoney(row['主力净流入-净额']) }}
                      </span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="主力净流入-净占比" label="净占比" width="80">
                    <template #default="{ row }">
                      <span :class="row['主力净流入-净占比'] >= 0 ? 'text-up' : 'text-down'">
                        {{ row['主力净流入-净占比']?.toFixed(2) }}%
                      </span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- 财务数据 -->
        <el-tab-pane label="财务数据" name="financial">
          <div class="fade-in" v-loading="financialLoading">
            <el-row :gutter="20" v-if="financial.basic_info">
              <el-col :span="24">
                <div class="modern-card highlight-card">
                  <div class="card-header-modern">
                    <span class="card-title">基本财务信息</span>
                  </div>
                  <el-descriptions :column="3" border class="modern-descriptions">
                    <el-descriptions-item label="股票代码">{{ financial.basic_info.股票代码 }}</el-descriptions-item>
                    <el-descriptions-item label="股票名称">{{ financial.basic_info.股票名称 }}</el-descriptions-item>
                    <el-descriptions-item label="最新价">{{ financial.basic_info.最新价 }}</el-descriptions-item>
                    <el-descriptions-item label="市盈率">{{ financial.basic_info.市盈率?.toFixed(2) }}</el-descriptions-item>
                    <el-descriptions-item label="市净率">{{ financial.basic_info.市净率?.toFixed(2) }}</el-descriptions-item>
                    <el-descriptions-item label="换手率">{{ financial.basic_info.换手率?.toFixed(2) }}%</el-descriptions-item>
                    <el-descriptions-item label="总市值">{{ formatMoney(financial.basic_info.总市值) }}</el-descriptions-item>
                    <el-descriptions-item label="流通市值">{{ formatMoney(financial.basic_info.流通市值) }}</el-descriptions-item>
                    <el-descriptions-item label="成交额">{{ formatMoney(financial.basic_info.成交额) }}</el-descriptions-item>
                  </el-descriptions>
                </div>
              </el-col>
            </el-row>
            
            <el-row :gutter="20" style="margin-top: 20px;">
              <el-col :span="12">
                <div class="modern-card">
                  <div class="card-header-modern"><span class="card-title">基本信息</span></div>
                  <el-descriptions :column="2" size="small" class="modern-descriptions">
                    <el-descriptions-item label="股票代码">{{ financial.basic_info?.股票代码 || '--' }}</el-descriptions-item>
                    <el-descriptions-item label="股票名称">{{ financial.basic_info?.股票名称 || '--' }}</el-descriptions-item>
                    <el-descriptions-item label="最新价">{{ formatPrice(financial.basic_info?.最新价) }}</el-descriptions-item>
                    <el-descriptions-item label="行业">{{ financial.basic_info?.行业 || '--' }}</el-descriptions-item>
                    <el-descriptions-item label="总股本">{{ formatVolume(financial.basic_info?.总股本) }}</el-descriptions-item>
                    <el-descriptions-item label="流通股">{{ formatVolume(financial.basic_info?.流通股) }}</el-descriptions-item>
                    <el-descriptions-item label="总市值">{{ formatMoney(financial.basic_info?.总市值) }}</el-descriptions-item>
                    <el-descriptions-item label="流通市值">{{ formatMoney(financial.basic_info?.流通市值) }}</el-descriptions-item>
                  </el-descriptions>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="modern-card">
                  <div class="card-header-modern"><span class="card-title">财务比率</span></div>
                  <el-descriptions :column="2" size="small" class="modern-descriptions">
                    <el-descriptions-item label="市盈率(动态)">{{ financial.financial_ratios?.市盈率_动态 || '--' }}</el-descriptions-item>
                    <el-descriptions-item label="市净率">{{ financial.financial_ratios?.市净率 || '--' }}</el-descriptions-item>
                    <el-descriptions-item label="换手率">{{ financial.financial_ratios?.换手率 || '--' }}%</el-descriptions-item>
                    <el-descriptions-item label="量比">{{ financial.financial_ratios?.量比 || '--' }}</el-descriptions-item>
                    <el-descriptions-item label="振幅">{{ financial.financial_ratios?.振幅 || '--' }}%</el-descriptions-item>
                    <el-descriptions-item label="60日涨跌幅">{{ financial.financial_ratios?.['60日涨跌幅'] || '--' }}%</el-descriptions-item>
                  </el-descriptions>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <!-- 新闻资讯 -->
        <el-tab-pane label="新闻资讯" name="news">
          <div class="news-container fade-in" v-loading="newsLoading">
            <div class="news-card" v-for="item in news" :key="item.新闻链接" @click="openNews(item.新闻链接)">
              <div class="news-time">{{ item.发布时间 }}</div>
              <h4 class="news-title">{{ item.新闻标题 }}</h4>
              <p class="news-content">{{ item.新闻内容?.substring(0, 150) }}...</p>
              <div class="news-footer">
                <span class="news-source">{{ item.文章来源 }}</span>
                <span class="news-link">查看详情 →</span>
              </div>
            </div>
            <el-empty v-if="news.length === 0" description="暂无相关新闻" />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, Star, Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { api } from '@/api'
import type { StockInfo, StockRealtime, KlineData } from '@/types'

const router = useRouter()
const route = useRoute()

const stockId = parseInt(route.params.id as string)
const stockInfo = ref<StockInfo>({} as StockInfo)
const realtime = ref<StockRealtime>({} as StockRealtime)
const klineData = ref<KlineData>({ dates: [], data: [], volumes: [] })
const technical = ref<any>({})
const financial = ref<any>({ balance_sheet: [], income_statement: [], cash_flow: [] })
const fundFlow = ref<any[]>([])
const news = ref<any[]>([])

const activeTab = ref('basic')
const period = ref('day')

// 加载状态
const chartLoading = ref(false)
const technicalLoading = ref(false)
const financialLoading = ref(false)
const fundFlowLoading = ref(false)
const newsLoading = ref(false)
const refreshing = ref(false)

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null
let timer: number | null = null

const technicalIndicators = computed(() => ({
  'MA5': technical.value.ma5 || '--',
  'MA10': technical.value.ma10 || '--',
  'MA20': technical.value.ma20 || '--',
  'MA60': technical.value.ma60 || '--',
  'RSI': technical.value.rsi || '--',
  '量比': technical.value.volume_ratio?.toFixed(2) || '--'
}))

const basicInfo = computed(() => [
  { label: '当前价格', value: formatPrice(realtime.value.price), class: getChangeClass(realtime.value) },
  { label: '涨跌幅', value: formatChange(realtime.value.change_percent), class: getChangeClass(realtime.value) },
  { label: '今开', value: formatPrice(realtime.value.open), class: '' },
  { label: '昨收', value: formatPrice(realtime.value.pre_close), class: '' },
  { label: '最高', value: formatPrice(realtime.value.high), class: 'text-up' },
  { label: '最低', value: formatPrice(realtime.value.low), class: 'text-down' },
  { label: '成交量', value: formatVolume(realtime.value.volume), class: '' },
  { label: '成交额', value: formatMoney(realtime.value.amount), class: '' },
])

onMounted(async () => {
  await loadStockInfo()
  await loadRealtime()
  await loadKline()
  loadTechnical()
  loadFinancial()
  loadFundFlow()
  loadNews()
  await initChart()
  
  timer = window.setInterval(async () => {
    await loadRealtime()
  }, 30000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (chart) chart.dispose()
})

async function refreshAll() {
  refreshing.value = true
  await Promise.all([loadRealtime(), loadKline()])
  refreshing.value = false
}

async function loadStockInfo() {
  try {
    const res = await api.stocks.getDetail(stockId)
    stockInfo.value = res
  } catch (error) {
    console.error('加载股票信息失败:', error)
  }
}

async function loadRealtime() {
  try {
    const res = await api.stocks.getRealtime(stockId)
    realtime.value = res
  } catch (error) {
    console.error('加载实时数据失败:', error)
  }
}

async function loadKline() {
  chartLoading.value = true
  try {
    const res = await api.stocks.getKline(stockId, period.value)
    if (res && res.klines) {
      klineData.value = {
        dates: res.klines.map((item: any) => item.date),
        data: res.klines.map((item: any) => [item.open, item.close, item.low, item.high]),
        volumes: res.klines.map((item: any) => item.volume)
      }
    }
    await nextTick()
    updateChart()
  } catch (error) {
    console.error('加载K线数据失败:', error)
  } finally {
    chartLoading.value = false
  }
}

async function loadTechnical() {
  technicalLoading.value = true
  try {
    const data = await api.enhanced.getStockTechnical(stockInfo.value.code)
    technical.value = data.technical || {}
  } catch (error) {
    console.error('加载技术指标失败:', error)
  } finally {
    technicalLoading.value = false
  }
}

async function loadFinancial() {
  financialLoading.value = true
  try {
    const data = await api.enhanced.getStockFinancial(stockInfo.value.code)
    financial.value = data
  } catch (error) {
    console.error('加载财务数据失败:', error)
  } finally {
    financialLoading.value = false
  }
}

async function loadFundFlow() {
  fundFlowLoading.value = true
  try {
    const data = await api.enhanced.getStockFundFlow(stockInfo.value.code)
    fundFlow.value = data.fund_flow || []
  } catch (error) {
    console.error('加载资金流向失败:', error)
  } finally {
    fundFlowLoading.value = false
  }
}

async function loadNews() {
  newsLoading.value = true
  try {
    const data = await api.enhanced.getStockNews(stockInfo.value.code)
    news.value = data.news || []
  } catch (error) {
    console.error('加载新闻失败:', error)
  } finally {
    newsLoading.value = false
  }
}

async function initChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)
  updateChart()
  window.addEventListener('resize', () => chart?.resize())
}

function updateChart() {
  if (!chart || !klineData.value.dates.length) return

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e2e8f0',
      textStyle: { color: '#1e293b' }
    },
    legend: {
      data: ['K线', '成交量'],
      top: 10,
      textStyle: { color: '#64748b' }
    },
    grid: [
      { left: '10%', right: '8%', top: '15%', height: '50%' },
      { left: '10%', right: '8%', top: '72%', height: '15%' }
    ],
    xAxis: [
      { type: 'category', data: klineData.value.dates, gridIndex: 0, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#e2e8f0' } } },
      { type: 'category', data: klineData.value.dates, gridIndex: 1, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#e2e8f0' } } }
    ],
    yAxis: [
      { scale: true, gridIndex: 0, splitNumber: 4, splitLine: { lineStyle: { color: '#f1f5f9' } }, axisLine: { lineStyle: { color: '#e2e8f0' } } },
      { scale: true, gridIndex: 1, splitNumber: 2, axisLabel: { show: false }, splitLine: { lineStyle: { color: '#f1f5f9' } } }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 70, end: 100 },
      { type: 'slider', xAxisIndex: [0, 1], start: 70, end: 100, height: 20, bottom: 10 }
    ],
    series: [
      {
        name: 'K线', type: 'candlestick', data: klineData.value.data,
        itemStyle: { color: '#ef4444', color0: '#22c55e', borderColor: '#ef4444', borderColor0: '#22c55e' }
      },
      {
        name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: klineData.value.volumes,
        itemStyle: {
          color: (params: any) => {
            const idx = params.dataIndex
            const open = klineData.value.data[idx][0]
            const close = klineData.value.data[idx][1]
            return close >= open ? '#ef4444' : '#22c55e'
          }
        }
      }
    ]
  }
  chart.setOption(option, true)
}

function formatPrice(price?: number): string {
  if (!price) return '--'
  return price.toFixed(2)
}

function formatChange(change?: number): string {
  if (change === undefined || change === null) return '--'
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

function formatChangeAmount(data: StockRealtime): string {
  if (!data.price || !data.pre_close) return '--'
  const diff = data.price - data.pre_close
  const sign = diff >= 0 ? '+' : ''
  return `${sign}${diff.toFixed(2)}`
}

function formatVolume(volume?: number): string {
  if (!volume) return '--'
  if (volume >= 100000000) return (volume / 100000000).toFixed(2) + '亿'
  if (volume >= 10000) return (volume / 10000).toFixed(2) + '万'
  return volume.toString()
}

function formatMoney(amount?: number): string {
  if (!amount) return '--'
  if (amount >= 100000000) return (amount / 100000000).toFixed(2) + '亿'
  if (amount >= 10000) return (amount / 10000).toFixed(2) + '万'
  return amount.toFixed(2)
}

function getChangeClass(data: StockRealtime): string {
  const change = data.change_percent || 0
  return change >= 0 ? 'text-up' : 'text-down'
}

function openNews(url: string) {
  window.open(url, '_blank')
}
</script>

<style scoped>
.enhanced-stock-detail {
  height: 100vh;
  background: var(--bg-primary);
}

/* 头部样式 */
.detail-header {
  background: var(--gradient-primary);
  border: none;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 24px;
  height: 80px;
}

.back-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.stock-title {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 32px;
}

.stock-name-wrapper h2 {
  color: white;
  font-size: 24px;
  margin: 0;
  font-weight: 600;
}

.stock-code {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.stock-price-wrapper {
  display: flex;
  align-items: baseline;
  gap: 16px;
}

.stock-price-wrapper .price {
  font-size: 36px;
  font-weight: 700;
  color: white;
}

.change-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.change-amount, .change-percent {
  font-size: 16px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.header-actions .el-button {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
}

.header-actions .el-button:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 主内容区 */
.detail-main {
  background: var(--bg-primary);
  padding: 24px;
  overflow-y: auto;
}

.detail-tabs {
  background: transparent;
}

:deep(.el-tabs__header) {
  background: white;
  border-radius: var(--radius-lg);
  padding: 8px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.el-tabs__item) {
  padding: 12px 24px;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

:deep(.el-tabs__item.is-active) {
  background: var(--gradient-primary);
  color: white;
}

/* 信息卡片网格 */
.info-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.info-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 20px;
  text-align: center;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
}

.info-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.info-label {
  color: var(--text-secondary);
  font-size: 13px;
  margin-bottom: 8px;
}

.info-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

/* K线图区域 */
.chart-section {
  background: white;
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.period-selector {
  --el-border-radius-base: 20px;
}

:deep(.period-selector .el-radio-button__inner) {
  border-radius: 20px;
  padding: 8px 20px;
  border: none;
  background: var(--bg-primary);
}

:deep(.period-selector .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: var(--gradient-primary);
  box-shadow: none;
}

.chart-container {
  position: relative;
  width: 100%;
  height: 450px;
  border-radius: var(--radius-md);
  overflow: hidden;
}

.chart-canvas {
  width: 100%;
  height: 100%;
}

/* 现代卡片 */
.modern-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  height: 100%;
}

.highlight-card {
  border-left: 4px solid var(--primary-color);
}

.card-header-modern {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 技术指标网格 */
.indicator-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.indicator-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-primary);
  border-radius: var(--radius-md);
}

.indicator-label {
  color: var(--text-secondary);
  font-size: 14px;
}

.indicator-value {
  font-weight: 600;
  color: var(--text-primary);
}

/* 新闻卡片 */
.news-container {
  display: grid;
  gap: 16px;
}

.news-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.news-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.news-time {
  color: var(--text-muted);
  font-size: 12px;
  margin-bottom: 8px;
}

.news-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  line-height: 1.5;
}

.news-content {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 16px;
}

.news-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.news-source {
  color: var(--text-muted);
  font-size: 12px;
}

.news-link {
  color: var(--primary-color);
  font-size: 14px;
  font-weight: 500;
}

/* 涨跌颜色 */
.text-up { color: var(--up-color) !important; }
.text-down { color: var(--down-color) !important; }

/* 表格样式 */
.modern-table {
  border-radius: var(--radius-md);
  overflow: hidden;
}

.modern-descriptions {
  --el-descriptions-item-bordered-label-background: var(--bg-primary);
}
</style>
