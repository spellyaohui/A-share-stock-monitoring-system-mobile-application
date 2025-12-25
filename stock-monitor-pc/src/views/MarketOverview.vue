<template>
  <el-container class="market-overview-container">
    <!-- 头部导航 - 与监测中心一致 -->
    <el-header class="dashboard-header">
      <div class="header-left">
        <div class="logo-section">
          <div class="logo-icon">📈</div>
          <h2>股票监测系统</h2>
        </div>
        <el-menu mode="horizontal" class="nav-menu" router :default-active="$route.path" :ellipsis="false">
          <el-menu-item index="/dashboard">
            <el-icon><Monitor /></el-icon>监测中心
          </el-menu-item>
          <el-menu-item index="/market">
            <el-icon><TrendCharts /></el-icon>市场概况
          </el-menu-item>
        </el-menu>
      </div>
      <div class="header-right">
        <el-button :icon="Refresh" @click="refreshData" :loading="loading">刷新数据</el-button>
        <el-dropdown @command="handleCommand" trigger="click">
          <div class="user-avatar">
            <el-avatar :size="36" class="avatar">
              {{ userStore.userInfo?.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <span class="username">{{ userStore.userInfo?.username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout"><el-icon><SwitchButton /></el-icon>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-main class="market-overview">
    <!-- 市场统计卡片 -->
    <div class="stats-grid fade-in">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-value">{{ marketStats.total_stocks }}</div>
          <div class="stat-label">总股票数</div>
        </div>
      </div>
      <div class="stat-card up-card">
        <div class="stat-icon">📈</div>
        <div class="stat-content">
          <div class="stat-value text-up">{{ marketStats.up_stocks }}</div>
          <div class="stat-label">上涨 ({{ marketStats.up_ratio }}%)</div>
        </div>
      </div>
      <div class="stat-card down-card">
        <div class="stat-icon">📉</div>
        <div class="stat-content">
          <div class="stat-value text-down">{{ marketStats.down_stocks }}</div>
          <div class="stat-label">下跌 ({{ marketStats.down_ratio }}%)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">➖</div>
        <div class="stat-content">
          <div class="stat-value">{{ marketStats.flat_stocks }}</div>
          <div class="stat-label">平盘</div>
        </div>
      </div>
    </div>

    <!-- 涨跌停统计 -->
    <div class="limit-grid fade-in">
      <div class="limit-card limit-up">
        <div class="limit-icon">🔥</div>
        <div class="limit-info">
          <span class="limit-value">{{ marketStats.limit_up }}</span>
          <span class="limit-label">涨停</span>
        </div>
      </div>
      <div class="limit-card limit-down">
        <div class="limit-icon">❄️</div>
        <div class="limit-info">
          <span class="limit-value">{{ marketStats.limit_down }}</span>
          <span class="limit-label">跌停</span>
        </div>
      </div>
    </div>

    <!-- 标签页内容 -->
    <el-tabs v-model="activeTab" class="market-tabs fade-in">
      <el-tab-pane label="热门股票" name="hot">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="ranking-card" v-loading="loading">
              <div class="ranking-header">
                <span class="ranking-title">💰 成交额排行</span>
              </div>
              <div class="ranking-list">
                <div class="ranking-item" v-for="(item, index) in topVolume" :key="item.代码">
                  <span class="rank-num" :class="getRankClass(index)">{{ index + 1 }}</span>
                  <div class="stock-info">
                    <span class="name">{{ item.名称 }}</span>
                    <span class="code">{{ item.代码 }}</span>
                  </div>
                  <div class="stock-data">
                    <span class="price">{{ item.最新价 }}</span>
                    <span class="change" :class="item.涨跌幅 >= 0 ? 'text-up' : 'text-down'">
                      {{ item.涨跌幅?.toFixed(2) }}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="ranking-card" v-loading="loading">
              <div class="ranking-header">
                <span class="ranking-title">🚀 涨幅排行</span>
              </div>
              <div class="ranking-list">
                <div class="ranking-item" v-for="(item, index) in topGainers" :key="item.代码">
                  <span class="rank-num" :class="getRankClass(index)">{{ index + 1 }}</span>
                  <div class="stock-info">
                    <span class="name">{{ item.名称 }}</span>
                    <span class="code">{{ item.代码 }}</span>
                  </div>
                  <div class="stock-data">
                    <span class="price">{{ item.最新价 }}</span>
                    <span class="change text-up">{{ item.涨跌幅?.toFixed(2) }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="ranking-card" v-loading="loading">
              <div class="ranking-header">
                <span class="ranking-title">📉 跌幅排行</span>
              </div>
              <div class="ranking-list">
                <div class="ranking-item" v-for="(item, index) in topLosers" :key="item.代码">
                  <span class="rank-num" :class="getRankClass(index)">{{ index + 1 }}</span>
                  <div class="stock-info">
                    <span class="name">{{ item.名称 }}</span>
                    <span class="code">{{ item.代码 }}</span>
                  </div>
                  <div class="stock-data">
                    <span class="price">{{ item.最新价 }}</span>
                    <span class="change text-down">{{ item.涨跌幅?.toFixed(2) }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-tab-pane>

      <el-tab-pane label="行业板块" name="sectors">
        <el-row :gutter="24">
          <el-col :span="12">
            <div class="sector-card industry-card" v-loading="sectorLoading">
              <div class="sector-header">
                <span class="sector-icon">🏭</span>
                <span class="sector-title">行业板块</span>
                <el-tag type="warning" size="small" effect="light">TOP 15</el-tag>
              </div>
              <el-table :data="industries.slice(0, 15)" size="small" class="modern-table" :row-class-name="tableRowClassName">
                <el-table-column prop="板块名称" label="板块名称" min-width="120" />
                <el-table-column prop="涨跌幅" label="涨跌幅" width="100">
                  <template #default="{ row }">
                    <span :class="row.涨跌幅 >= 0 ? 'text-up' : 'text-down'">
                      {{ row.涨跌幅?.toFixed(2) }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="上涨家数" label="上涨" width="70" />
                <el-table-column prop="下跌家数" label="下跌" width="70" />
                <el-table-column prop="领涨股票" label="领涨股票" width="100" />
              </el-table>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="sector-card concept-card" v-loading="sectorLoading">
              <div class="sector-header">
                <span class="sector-icon">💡</span>
                <span class="sector-title">概念板块</span>
                <el-tag type="primary" size="small" effect="light">TOP 15</el-tag>
              </div>
              <el-table :data="concepts.slice(0, 15)" size="small" class="modern-table" :row-class-name="tableRowClassName">
                <el-table-column prop="板块名称" label="板块名称" min-width="120" />
                <el-table-column prop="涨跌幅" label="涨跌幅" width="100">
                  <template #default="{ row }">
                    <span :class="row.涨跌幅 >= 0 ? 'text-up' : 'text-down'">
                      {{ row.涨跌幅?.toFixed(2) }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="上涨家数" label="上涨" width="70" />
                <el-table-column prop="下跌家数" label="下跌" width="70" />
                <el-table-column prop="领涨股票" label="领涨股票" width="100" />
              </el-table>
            </div>
          </el-col>
        </el-row>
      </el-tab-pane>

      <el-tab-pane label="龙虎榜" name="lhb">
        <el-row :gutter="24">
          <el-col :span="12">
            <div class="lhb-card" v-loading="lhbLoading">
              <div class="lhb-header">
                <span class="sector-icon">🐉</span>
                <span class="lhb-title">龙虎榜 TOP 1-25</span>
                <el-tag type="danger" size="small" effect="light">近一月</el-tag>
              </div>
              <el-table :data="lhbData.slice(0, 25)" size="small" class="modern-table lhb-table" max-height="550" :row-class-name="lhbRowClassName">
                <el-table-column prop="序号" label="#" width="45" align="center" />
                <el-table-column prop="代码" label="代码" width="75" />
                <el-table-column prop="名称" label="名称" min-width="80" />
                <el-table-column label="涨跌幅" width="80" align="right">
                  <template #default="{ row }">
                    <span :class="(row.涨跌幅 || 0) >= 0 ? 'text-up' : 'text-down'">
                      {{ row.涨跌幅?.toFixed(2) || '--' }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="上榜次数" label="次数" width="55" align="center" />
                <el-table-column label="净买额" min-width="90" align="right">
                  <template #default="{ row }">
                    <span :class="(row.龙虎榜净买额 || 0) >= 0 ? 'text-up' : 'text-down'" class="money-cell">
                      {{ formatMoney(row.龙虎榜净买额) }}
                    </span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="lhb-card lhb-card-right" v-loading="lhbLoading">
              <div class="lhb-header">
                <span class="sector-icon">🐉</span>
                <span class="lhb-title">龙虎榜 TOP 26-50</span>
                <el-tag type="warning" size="small" effect="light">近一月</el-tag>
              </div>
              <el-table :data="lhbData.slice(25, 50)" size="small" class="modern-table lhb-table" max-height="550">
                <el-table-column prop="序号" label="#" width="45" align="center" />
                <el-table-column prop="代码" label="代码" width="75" />
                <el-table-column prop="名称" label="名称" min-width="80" />
                <el-table-column label="涨跌幅" width="80" align="right">
                  <template #default="{ row }">
                    <span :class="(row.涨跌幅 || 0) >= 0 ? 'text-up' : 'text-down'">
                      {{ row.涨跌幅?.toFixed(2) || '--' }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="上榜次数" label="次数" width="55" align="center" />
                <el-table-column label="净买额" min-width="90" align="right">
                  <template #default="{ row }">
                    <span :class="(row.龙虎榜净买额 || 0) >= 0 ? 'text-up' : 'text-down'" class="money-cell">
                      {{ formatMoney(row.龙虎榜净买额) }}
                    </span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-col>
        </el-row>
        <el-empty v-if="lhbData.length === 0 && !lhbLoading" description="暂无龙虎榜数据" />
      </el-tab-pane>
    </el-tabs>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh, Monitor, TrendCharts, ArrowDown, SwitchButton } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { api } from '@/api'

const router = useRouter()
const userStore = useUserStore()
const activeTab = ref('hot')
const loading = ref(false)
const sectorLoading = ref(false)
const lhbLoading = ref(false)

const marketStats = ref({
  total_stocks: 0, up_stocks: 0, down_stocks: 0, flat_stocks: 0,
  limit_up: 0, limit_down: 0, up_ratio: 0, down_ratio: 0
})

const topVolume = ref([])
const topGainers = ref([])
const topLosers = ref([])
const industries = ref([])
const concepts = ref([])
const lhbData = ref([])

onMounted(async () => {
  await loadMarketOverview()
  await loadSectors()
  await loadLhbData()
})

async function loadMarketOverview() {
  loading.value = true
  try {
    const data = await api.enhanced.getMarketOverview()
    marketStats.value = data.market_stats
    topVolume.value = data.top_volume
    topGainers.value = data.top_gainers
    topLosers.value = data.top_losers
  } catch (error) {
    console.error('加载市场概况失败:', error)
  } finally {
    loading.value = false
  }
}

async function loadSectors() {
  sectorLoading.value = true
  try {
    const data = await api.enhanced.getSectors()
    industries.value = data.industries
    concepts.value = data.concepts
  } catch (error) {
    console.error('加载板块数据失败:', error)
  } finally {
    sectorLoading.value = false
  }
}

async function loadLhbData() {
  lhbLoading.value = true
  try {
    const response = await fetch('/api/enhanced/market/lhb')
    const data = await response.json()
    lhbData.value = data.lhb_data
  } catch (error) {
    console.error('加载龙虎榜数据失败:', error)
  } finally {
    lhbLoading.value = false
  }
}

async function refreshData() {
  await Promise.all([loadMarketOverview(), loadSectors(), loadLhbData()])
}

function handleCommand(command: string) {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}

function formatMoney(amount?: number): string {
  if (!amount) return '--'
  if (amount >= 100000000) return (amount / 100000000).toFixed(2) + '亿'
  if (amount >= 10000) return (amount / 10000).toFixed(2) + '万'
  return amount.toFixed(2)
}

function getRankClass(index: number): string {
  if (index === 0) return 'rank-gold'
  if (index === 1) return 'rank-silver'
  if (index === 2) return 'rank-bronze'
  return ''
}

function tableRowClassName({ rowIndex }: { rowIndex: number }): string {
  if (rowIndex < 3) return 'top-row'
  return ''
}

function lhbRowClassName({ rowIndex }: { rowIndex: number }): string {
  if (rowIndex < 3) return 'lhb-top-row'
  return ''
}
</script>

<style scoped>
.market-overview-container {
  height: 100vh;
  background: var(--bg-primary);
}

/* 头部样式 - 与监测中心一致 */
.dashboard-header {
  background: white;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
  box-shadow: var(--shadow-sm);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 48px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 28px;
}

.logo-section h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-menu {
  border: none;
  background: transparent;
}

:deep(.nav-menu .el-menu-item) {
  font-weight: 500;
  border-radius: var(--radius-md);
  margin: 0 4px;
}

:deep(.nav-menu .el-menu-item.is-active) {
  background: var(--bg-primary);
  color: var(--primary-color);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-avatar {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.user-avatar:hover {
  background: var(--bg-primary);
}

.avatar {
  background: var(--gradient-primary);
  color: white;
  font-weight: 600;
}

.username {
  font-weight: 500;
  color: var(--text-primary);
}

.market-overview {
  padding: 24px;
  background: var(--bg-primary);
  overflow-y: auto;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.up-card { border-left: 4px solid var(--up-color); }
.down-card { border-left: 4px solid var(--down-color); }

.stat-icon {
  font-size: 36px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* 涨跌停卡片 */
.limit-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.limit-card {
  border-radius: var(--radius-lg);
  padding: 20px 32px;
  display: flex;
  align-items: center;
  gap: 20px;
  color: white;
  box-shadow: var(--shadow-md);
}

.limit-up { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
.limit-down { background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); }

.limit-icon { font-size: 32px; }
.limit-value { font-size: 36px; font-weight: 700; }
.limit-label { font-size: 16px; opacity: 0.9; margin-left: 8px; }

/* 标签页样式 */
.market-tabs {
  background: transparent;
}

:deep(.market-tabs .el-tabs__header) {
  background: white;
  border-radius: var(--radius-lg);
  padding: 4px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
}

:deep(.market-tabs .el-tabs__nav-wrap::after) { display: none; }

:deep(.market-tabs .el-tabs__active-bar) { display: none; }

:deep(.market-tabs .el-tabs__item) {
  padding: 12px 28px !important;
  height: auto !important;
  line-height: 1 !important;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

:deep(.market-tabs .el-tabs__item.is-active) {
  background: var(--gradient-primary);
  color: white;
}

/* 排行卡片 */
.ranking-card, .sector-card, .lhb-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  height: 100%;
}

.ranking-header, .sector-header, .lhb-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.ranking-title, .sector-title, .lhb-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 排行列表 */
.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.ranking-item:hover {
  background: var(--bg-secondary);
  transform: translateX(4px);
}

.rank-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--text-muted);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.rank-gold { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.rank-silver { background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%); }
.rank-bronze { background: linear-gradient(135deg, #d97706 0%, #b45309 100%); }

.stock-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stock-info .name {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 14px;
}

.stock-info .code {
  font-size: 12px;
  color: var(--text-secondary);
}

.stock-data {
  text-align: right;
}

.stock-data .price {
  display: block;
  font-weight: 600;
  color: var(--text-primary);
}

.stock-data .change {
  font-size: 13px;
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

/* 行业板块和龙虎榜卡片美化 */
.sector-card, .lhb-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
}

.sector-card:hover, .lhb-card:hover {
  box-shadow: var(--shadow-md);
}

.sector-header, .lhb-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--bg-primary);
}

.sector-icon {
  font-size: 24px;
}

.sector-title, .lhb-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
}

/* 美化表格 */
:deep(.modern-table) {
  --el-table-border-color: var(--border-color);
  --el-table-header-bg-color: var(--bg-primary);
  border-radius: var(--radius-md);
  overflow: hidden;
}

:deep(.modern-table .el-table__header th) {
  background: var(--bg-primary) !important;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 13px;
  padding: 14px 0;
}

:deep(.modern-table .el-table__body td) {
  padding: 12px 0;
  font-size: 13px;
}

:deep(.modern-table .el-table__row) {
  transition: all var(--transition-fast);
}

:deep(.modern-table .el-table__row:hover > td) {
  background: var(--bg-primary) !important;
}

/* 前三名高亮 */
:deep(.modern-table .top-row) {
  background: linear-gradient(90deg, rgba(99, 102, 241, 0.05) 0%, transparent 100%);
}

:deep(.modern-table .lhb-top-row) {
  background: linear-gradient(90deg, rgba(239, 68, 68, 0.05) 0%, transparent 100%);
}

:deep(.modern-table .lhb-top-row td:nth-child(1)) {
  font-weight: 700;
  color: var(--primary-color);
}

/* 龙虎榜特殊样式 */
.lhb-card {
  border-left: 4px solid var(--up-color);
}

.lhb-card-right {
  border-left: 4px solid #f59e0b;
}

.money-cell {
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
  font-size: 12px;
}

/* 行业板块特殊样式 */
.industry-card {
  border-left: 4px solid #f59e0b;
}

.concept-card {
  border-left: 4px solid #8b5cf6;
}
</style>
