<template>
  <el-container class="stock-detail-container">
    <el-header class="detail-header">
      <el-button :icon="ArrowLeft" @click="router.back()">返回</el-button>
      <h2>{{ stockInfo.name }} ({{ stockInfo.code }})</h2>
    </el-header>

    <el-main class="detail-main">
      <el-row :gutter="20" class="info-row">
        <el-col :span="6">
          <el-card>
            <div class="info-label">当前价格</div>
            <div class="info-value" :class="getChangeClass(realtime)">{{ formatPrice(realtime.price) }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="info-label">涨跌幅</div>
            <div class="info-value" :class="getChangeClass(realtime)">{{ formatChange(realtime.change_percent) }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="info-label">今开</div>
            <div class="info-value">{{ formatPrice(realtime.open) }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="info-label">昨收</div>
            <div class="info-value">{{ formatPrice(realtime.pre_close) }}</div>
          </el-card>
        </el-col>
      </el-row>

      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>K线图</span>
            <el-radio-group v-model="period" @change="loadKline">
              <el-radio-button label="day">日K</el-radio-button>
              <el-radio-button label="week">周K</el-radio-button>
              <el-radio-button label="month">月K</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        <div ref="chartRef" style="width: 100%; height: 400px"></div>
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { api } from '@/api'
import type { StockInfo, StockRealtime, KlineData } from '@/types'

const router = useRouter()
const route = useRoute()

const stockId = parseInt(route.params.id as string)
const stockInfo = ref<StockInfo>({} as StockInfo)
const realtime = ref<StockRealtime>({} as StockRealtime)
const klineData = ref<KlineData>({ dates: [], data: [], volumes: [] })
const period = ref('day')

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null
let timer: number | null = null

onMounted(async () => {
  await loadStockInfo()
  await loadRealtime()
  await loadKline()
  await initChart()
  timer = window.setInterval(async () => {
    await loadRealtime()
  }, 30000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (chart) chart.dispose()
})

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
  try {
    const res = await api.charts.getKline(stockId, period.value)
    // 转换数据格式
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
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['K线', 'MA5', 'MA10', 'MA20', 'MA60', '成交量']
    },
    grid: [
      { left: '10%', right: '8%', height: '50%' },
      { left: '10%', right: '8%', top: '70%', height: '15%' }
    ],
    xAxis: [
      {
        type: 'category',
        data: klineData.value.dates,
        gridIndex: 0,
        axisLabel: { show: false }
      },
      {
        type: 'category',
        data: klineData.value.dates,
        gridIndex: 1,
        axisLabel: { show: false }
      }
    ],
    yAxis: [
      {
        scale: true,
        gridIndex: 0,
        splitNumber: 4
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLabel: { show: false }
      }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 70, end: 100 },
      { type: 'slider', xAxisIndex: [0, 1], start: 70, end: 100 }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: klineData.value.data,
        itemStyle: {
          color: '#ef5350',
          color0: '#26a69a',
          borderColor: '#ef5350',
          borderColor0: '#26a69a'
        }
      },
      {
        name: 'MA5',
        type: 'line',
        data: klineData.value.ma?.ma5 || [],
        smooth: true,
        lineStyle: { opacity: 0.8 }
      },
      {
        name: 'MA10',
        type: 'line',
        data: klineData.value.ma?.ma10 || [],
        smooth: true,
        lineStyle: { opacity: 0.8 }
      },
      {
        name: 'MA20',
        type: 'line',
        data: klineData.value.ma?.ma20 || [],
        smooth: true,
        lineStyle: { opacity: 0.8 }
      },
      {
        name: 'MA60',
        type: 'line',
        data: klineData.value.ma?.ma60 || [],
        smooth: true,
        lineStyle: { opacity: 0.8 }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: klineData.value.volumes,
        itemStyle: {
          color: (params: any) => {
            const idx = params.dataIndex
            const open = klineData.value.data[idx][0]
            const close = klineData.value.data[idx][1]
            return close >= open ? '#ef5350' : '#26a69a'
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
  if (!change) return '--'
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

function getChangeClass(data: StockRealtime): string {
  const change = data.change_percent || 0
  return change >= 0 ? 'text-up' : 'text-down'
}
</script>

<style scoped>
.stock-detail-container {
  height: 100vh;
}

.detail-header {
  background: #fff;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 20px;
}

.detail-main {
  background: #f5f5f5;
  padding: 20px;
}

.info-row {
  margin-bottom: 20px;
}

.info-label {
  color: #999;
  font-size: 12px;
  margin-bottom: 5px;
}

.info-value {
  font-size: 24px;
  font-weight: bold;
}

.chart-card {
  height: calc(100% - 140px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text-up {
  color: #f56c6c;
}

.text-down {
  color: #67c23a;
}
</style>
