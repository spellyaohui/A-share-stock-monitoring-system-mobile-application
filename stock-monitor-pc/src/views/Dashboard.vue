<template>
  <el-container class="dashboard-container">
    <!-- 现代化头部 -->
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
        <el-button type="primary" :icon="Plus" @click="showAddDialog = true" class="add-btn">
          添加监测
        </el-button>
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
              <el-dropdown-item command="users"><el-icon><User /></el-icon>用户管理</el-dropdown-item>
              <el-dropdown-item command="settings"><el-icon><Setting /></el-icon>设置</el-dropdown-item>
              <el-dropdown-item command="logout" divided><el-icon><SwitchButton /></el-icon>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-main class="dashboard-main">
      <!-- 统计卡片 -->
      <div class="stats-grid fade-in">
        <div class="stat-card gradient-primary">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <div class="stat-value">{{ monitors.length }}</div>
            <div class="stat-label">监测中</div>
          </div>
        </div>
        <div class="stat-card gradient-success">
          <div class="stat-icon">✅</div>
          <div class="stat-info">
            <div class="stat-value">{{ activeCount }}</div>
            <div class="stat-label">活跃中</div>
          </div>
        </div>
        <div class="stat-card gradient-warning">
          <div class="stat-icon">🔔</div>
          <div class="stat-info">
            <div class="stat-value">{{ todayTriggered }}</div>
            <div class="stat-label">今日触发</div>
          </div>
        </div>
        <div class="stat-card gradient-info">
          <div class="stat-icon">📈</div>
          <div class="stat-info">
            <div class="stat-value">{{ upCount }}</div>
            <div class="stat-label">上涨</div>
          </div>
        </div>
      </div>

      <!-- 监测列表 -->
      <div class="monitor-section fade-in">
        <div class="section-header">
          <h3>我的监测列表</h3>
          <el-button text :icon="Refresh" @click="loadMonitors" :loading="loading">刷新</el-button>
        </div>
        
        <div class="monitor-grid" v-if="monitors.length > 0">
          <div class="monitor-card card-hover" v-for="monitor in monitors" :key="monitor.id" @click="goToDetail(monitor)">
            <div class="monitor-header">
              <div class="stock-info">
                <span class="stock-name">{{ monitor.stock?.name }}</span>
                <span class="stock-code">{{ monitor.stock?.code }}</span>
              </div>
              <el-switch v-model="monitor.is_active" @change="toggleMonitor(monitor)" @click.stop size="small" />
            </div>
            
            <div class="monitor-price" :class="getChangeClass(monitor)">
              <span class="current-price">{{ formatPrice(monitor.current_price) }}</span>
              <span class="change-percent">{{ formatChange(monitor.change_percent) }}</span>
            </div>
            
            <div class="monitor-conditions">
              <el-tag v-if="monitor.price_min" type="success" size="small" effect="light">
                ≥{{ monitor.price_min }}
              </el-tag>
              <el-tag v-if="monitor.price_max" type="warning" size="small" effect="light">
                ≤{{ monitor.price_max }}
              </el-tag>
              <el-tag v-if="monitor.rise_threshold" type="danger" size="small" effect="light">
                涨{{ monitor.rise_threshold }}%
              </el-tag>
              <el-tag v-if="monitor.fall_threshold" type="info" size="small" effect="light">
                跌{{ monitor.fall_threshold }}%
              </el-tag>
            </div>
            
            <div class="monitor-actions">
              <el-button type="danger" size="small" text :icon="Delete" @click.stop="deleteMonitor(monitor.id!)">
                删除
              </el-button>
            </div>
          </div>
        </div>
        
        <el-empty v-else-if="!loading" description="暂无监测，点击右上角添加" class="empty-state" />
        
        <div v-if="loading" class="loading-grid">
          <div class="skeleton-card" v-for="i in 4" :key="i">
            <div class="skeleton skeleton-title"></div>
            <div class="skeleton skeleton-price"></div>
            <div class="skeleton skeleton-tags"></div>
          </div>
        </div>
      </div>
    </el-main>

    <!-- 添加监测对话框 -->
    <el-dialog v-model="showAddDialog" title="添加股票监测" width="480px" class="modern-dialog">
      <el-form :model="monitorForm" label-width="100px" class="monitor-form">
        <el-form-item label="搜索股票">
          <el-autocomplete
            v-model="searchKeyword"
            :fetch-suggestions="searchStocks"
            placeholder="输入股票代码或名称"
            @select="selectStock"
            :debounce="300"
            :trigger-on-focus="false"
            :highlight-first-item="true"
            style="width: 100%"
            clearable
            class="stock-search"
          >
            <template #default="{ item }">
              <div class="stock-suggestion">
                <span class="stock-name">{{ item.name }}</span>
                <span class="stock-code">{{ item.code }}</span>
              </div>
            </template>
          </el-autocomplete>
        </el-form-item>
        <el-divider content-position="left">价格条件</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="最低价">
              <el-input-number v-model="monitorForm.price_min" :min="0" :precision="2" style="width: 100%" placeholder="触发买入" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最高价">
              <el-input-number v-model="monitorForm.price_max" :min="0" :precision="2" style="width: 100%" placeholder="触发卖出" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider content-position="left">涨跌幅条件</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="涨幅阈值">
              <el-input-number v-model="monitorForm.rise_threshold" :min="0" :max="100" :precision="2" style="width: 100%" placeholder="%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="跌幅阈值">
              <el-input-number v-model="monitorForm.fall_threshold" :min="0" :max="100" :precision="2" style="width: 100%" placeholder="%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addMonitor" :loading="adding">确定添加</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Delete, Monitor, TrendCharts, ArrowDown, Setting, SwitchButton, User } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { api } from '@/api'
import type { MonitorConfig } from '@/types'

const router = useRouter()
const userStore = useUserStore()

const monitors = ref<MonitorConfig[]>([])
const loading = ref(false)
const refreshing = ref(false)  // 区分首次加载和刷新
const showAddDialog = ref(false)
const adding = ref(false)
const searchKeyword = ref('')
const selectedStock = ref<any>(null)
let refreshTimer: number | null = null

const monitorForm = ref({
  stock_id: 0,
  price_min: undefined,
  price_max: undefined,
  rise_threshold: undefined,
  fall_threshold: undefined
})

const activeCount = computed(() => monitors.value.filter(m => m.is_active !== false).length)
const upCount = computed(() => monitors.value.filter(m => (m.change_percent || 0) > 0).length)
const todayTriggered = ref(0)

onMounted(() => {
  loadMonitors()
  // 使用 setTimeout 递归代替 setInterval，避免请求堆积
  startAutoRefresh()
})

onUnmounted(() => {
  // 清理定时器，避免内存泄漏
  if (refreshTimer) {
    clearTimeout(refreshTimer)
    refreshTimer = null
  }
})

function startAutoRefresh() {
  refreshTimer = window.setTimeout(async () => {
    // 只有在页面可见时才刷新
    if (document.visibilityState === 'visible') {
      await refreshMonitors()
    }
    startAutoRefresh()
  }, 15000)  // 缩短到 15 秒，因为后端已优化
}

async function loadMonitors() {
  loading.value = true
  try {
    const res = await api.monitors.getList()
    monitors.value = res
  } catch (error) {
    console.error('加载监测列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 静默刷新，不显示 loading 状态
async function refreshMonitors() {
  if (refreshing.value) return  // 防止重复请求
  refreshing.value = true
  try {
    const res = await api.monitors.getList()
    monitors.value = res
  } catch (error) {
    console.error('刷新监测列表失败:', error)
  } finally {
    refreshing.value = false
  }
}

async function searchStocks(queryString: string, cb: any) {
  if (!queryString || queryString.trim().length < 1) {
    cb([])
    return
  }
  try {
    const res = await api.stocks.search(queryString)
    if (res && res.length > 0) {
      cb(res.map((s: any) => ({ value: s.name, name: s.name, code: s.code, id: s.id })))
    } else {
      cb([])
    }
  } catch (error) {
    console.error('搜索失败:', error)
    cb([])
  }
}

function selectStock(item: any) {
  selectedStock.value = item
  monitorForm.value.stock_id = item.id
}

async function addMonitor() {
  if (!monitorForm.value.stock_id) {
    ElMessage.warning('请选择股票')
    return
  }
  adding.value = true
  try {
    await api.monitors.create(monitorForm.value)
    ElMessage.success('添加成功')
    showAddDialog.value = false
    monitorForm.value = { stock_id: 0, price_min: undefined, price_max: undefined, rise_threshold: undefined, fall_threshold: undefined }
    searchKeyword.value = ''
    await loadMonitors()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '添加失败')
  } finally {
    adding.value = false
  }
}

async function toggleMonitor(monitor: MonitorConfig) {
  try {
    await api.monitors.update(monitor.id!, { is_active: monitor.is_active })
    ElMessage.success(monitor.is_active ? '已启用' : '已禁用')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function deleteMonitor(id: number) {
  await ElMessageBox.confirm('确定删除该监测吗？', '提示', { type: 'warning' })
  try {
    await api.monitors.delete(id)
    ElMessage.success('删除成功')
    await loadMonitors()
  } catch (error) {
    ElMessage.error('删除失败')
  }
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

function getChangeClass(row: MonitorConfig): string {
  const change = row.change_percent || 0
  return change >= 0 ? 'text-up' : 'text-down'
}

function goToDetail(row: MonitorConfig) {
  router.push(`/enhanced-stock/${row.stock_id}`)
}

function handleCommand(command: string) {
  if (command === 'users') {
    router.push('/users')
  } else if (command === 'settings') {
    router.push('/settings')
  } else if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
  background: var(--bg-primary);
}

/* 头部样式 */
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

.add-btn {
  border-radius: 20px;
  padding: 10px 24px;
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

/* 主内容区 */
.dashboard-main {
  padding: 24px;
  overflow-y: auto;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  color: white;
  box-shadow: var(--shadow-md);
  transition: all var(--transition-normal);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
}

.gradient-primary { background: var(--gradient-primary); }
.gradient-success { background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); }
.gradient-warning { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.gradient-info { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); }

.stat-icon {
  font-size: 40px;
  opacity: 0.9;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
  margin-top: 8px;
}

/* 监测列表区域 */
.monitor-section {
  background: white;
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* 监测卡片网格 */
.monitor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.monitor-card {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 20px;
  cursor: pointer;
  border: 1px solid transparent;
}

.monitor-card:hover {
  border-color: var(--primary-light);
  background: white;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.stock-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stock-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.stock-code {
  font-size: 13px;
  color: var(--text-secondary);
}

.monitor-price {
  margin-bottom: 16px;
}

.current-price {
  font-size: 28px;
  font-weight: 700;
  margin-right: 12px;
}

.change-percent {
  font-size: 16px;
  font-weight: 500;
}

.monitor-conditions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.monitor-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

/* 加载骨架屏 */
.loading-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.skeleton-card {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 20px;
}

.skeleton-title { height: 24px; width: 60%; margin-bottom: 16px; }
.skeleton-price { height: 36px; width: 80%; margin-bottom: 16px; }
.skeleton-tags { height: 24px; width: 100%; }

/* 空状态 */
.empty-state {
  padding: 60px 0;
}

/* 涨跌颜色 */
.text-up { color: var(--up-color) !important; }
.text-down { color: var(--down-color) !important; }

/* 对话框样式 */
.modern-dialog {
  --el-dialog-border-radius: var(--radius-xl);
}

.stock-suggestion {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.stock-suggestion .stock-name {
  font-weight: 500;
  color: var(--text-primary);
}

.stock-suggestion .stock-code {
  color: var(--text-secondary);
  font-size: 12px;
}
</style>
