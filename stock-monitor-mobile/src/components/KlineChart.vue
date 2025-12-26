<template>
  <view class="kline-chart">
    <canvas 
      canvas-id="klineCanvas" 
      id="klineCanvas"
      class="chart-canvas"
      @touchstart="onTouchStart"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
    ></canvas>
    <!-- 十字光标信息 -->
    <view class="crosshair-info" v-if="showCrosshair && selectedData">
      <text class="info-date">{{ selectedData.date }}</text>
      <text class="info-item">开: {{ selectedData.open.toFixed(2) }}</text>
      <text class="info-item">高: {{ selectedData.high.toFixed(2) }}</text>
      <text class="info-item">低: {{ selectedData.low.toFixed(2) }}</text>
      <text class="info-item">收: {{ selectedData.close.toFixed(2) }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'

interface KlineItem {
  date: string
  open: number
  close: number
  high: number
  low: number
  volume?: number
}

interface Props {
  data: KlineItem[]
  width?: number
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  width: 350,
  height: 200
})

const showCrosshair = ref(false)
const selectedData = ref<KlineItem | null>(null)
let ctx: any = null
let canvasWidth = 0
let canvasHeight = 0
let candleWidth = 6
let candleGap = 2
let startIndex = 0

// 颜色配置
const colors = {
  up: '#ef4444',      // 涨 - 红色
  down: '#22c55e',    // 跌 - 绿色
  grid: '#e5e7eb',    // 网格线
  text: '#6b7280',    // 文字
  bg: '#ffffff'       // 背景
}

onMounted(() => {
  nextTick(() => {
    initCanvas()
  })
})

watch(() => props.data, () => {
  if (props.data.length > 0) {
    nextTick(() => {
      drawChart()
    })
  }
}, { deep: true })

function initCanvas() {
  ctx = uni.createCanvasContext('klineCanvas')
  
  // 获取设备信息计算画布大小
  const systemInfo = uni.getSystemInfoSync()
  canvasWidth = systemInfo.windowWidth - 32 // 减去边距
  canvasHeight = props.height
  
  // 计算可显示的蜡烛数量
  const visibleCandles = Math.floor(canvasWidth / (candleWidth + candleGap))
  startIndex = Math.max(0, props.data.length - visibleCandles)
  
  if (props.data.length > 0) {
    drawChart()
  }
}

function drawChart() {
  if (!ctx || props.data.length === 0) return
  
  // 清空画布
  ctx.setFillStyle(colors.bg)
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)
  
  // 获取可见数据
  const visibleCandles = Math.floor(canvasWidth / (candleWidth + candleGap))
  const visibleData = props.data.slice(startIndex, startIndex + visibleCandles)
  
  if (visibleData.length === 0) return
  
  // 计算价格范围
  let minPrice = Infinity
  let maxPrice = -Infinity
  visibleData.forEach(item => {
    minPrice = Math.min(minPrice, item.low)
    maxPrice = Math.max(maxPrice, item.high)
  })
  
  // 添加边距
  const priceRange = maxPrice - minPrice
  const padding = priceRange * 0.1
  minPrice -= padding
  maxPrice += padding
  
  // 绘制网格线
  drawGrid(minPrice, maxPrice)
  
  // 绘制K线
  const chartHeight = canvasHeight - 30 // 底部留空显示日期
  visibleData.forEach((item, index) => {
    const x = index * (candleWidth + candleGap) + candleGap
    const isUp = item.close >= item.open
    const color = isUp ? colors.up : colors.down
    
    // 计算Y坐标
    const highY = ((maxPrice - item.high) / (maxPrice - minPrice)) * chartHeight
    const lowY = ((maxPrice - item.low) / (maxPrice - minPrice)) * chartHeight
    const openY = ((maxPrice - item.open) / (maxPrice - minPrice)) * chartHeight
    const closeY = ((maxPrice - item.close) / (maxPrice - minPrice)) * chartHeight
    
    // 绘制影线
    ctx.setStrokeStyle(color)
    ctx.setLineWidth(1)
    ctx.beginPath()
    ctx.moveTo(x + candleWidth / 2, highY)
    ctx.lineTo(x + candleWidth / 2, lowY)
    ctx.stroke()
    
    // 绘制实体
    ctx.setFillStyle(color)
    const bodyTop = Math.min(openY, closeY)
    const bodyHeight = Math.max(Math.abs(closeY - openY), 1)
    ctx.fillRect(x, bodyTop, candleWidth, bodyHeight)
  })
  
  ctx.draw()
}

function drawGrid(minPrice: number, maxPrice: number) {
  const chartHeight = canvasHeight - 30
  
  // 绘制水平网格线和价格标签
  ctx.setStrokeStyle(colors.grid)
  ctx.setLineWidth(0.5)
  ctx.setFontSize(10)
  ctx.setFillStyle(colors.text)
  
  for (let i = 0; i <= 4; i++) {
    const y = (chartHeight / 4) * i
    const price = maxPrice - ((maxPrice - minPrice) / 4) * i
    
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(canvasWidth, y)
    ctx.stroke()
    
    // 价格标签
    ctx.fillText(price.toFixed(2), 2, y + 10)
  }
}

function onTouchStart(e: any) {
  showCrosshair.value = true
  updateCrosshair(e)
}

function onTouchMove(e: any) {
  updateCrosshair(e)
}

function onTouchEnd() {
  showCrosshair.value = false
  selectedData.value = null
}

function updateCrosshair(e: any) {
  const touch = e.touches[0]
  const x = touch.x
  
  // 计算选中的蜡烛索引
  const candleIndex = Math.floor(x / (candleWidth + candleGap))
  const dataIndex = startIndex + candleIndex
  
  if (dataIndex >= 0 && dataIndex < props.data.length) {
    selectedData.value = props.data[dataIndex]
  }
}
</script>

<style lang="scss" scoped>
.kline-chart {
  position: relative;
  width: 100%;
}

.chart-canvas {
  width: 100%;
  height: 200px;
}

.crosshair-info {
  position: absolute;
  top: 8rpx;
  right: 8rpx;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 8rpx;
  padding: 12rpx 16rpx;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.info-date {
  color: #fff;
  font-size: 22rpx;
  font-weight: 600;
  margin-bottom: 4rpx;
}

.info-item {
  color: #e5e7eb;
  font-size: 20rpx;
}
</style>
