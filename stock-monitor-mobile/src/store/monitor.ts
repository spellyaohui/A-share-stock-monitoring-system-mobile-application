// ============================================
// 股票监测系统移动端 - 监测状态管理
// ============================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { monitorApi, realtimeApi } from '@/api'
import type { MonitorConfig, CreateMonitorRequest, UpdateMonitorRequest } from '@/types'

// 交易时间内使用短间隔（15秒），非交易时间使用长间隔（60秒）
const REFRESH_INTERVAL_TRADING = 15000  // 15秒（考虑后端缓存10秒+网络延迟）
const REFRESH_INTERVAL_NON_TRADING = 60000  // 60秒

export const useMonitorStore = defineStore('monitor', () => {
  // 状态
  const monitors = ref<MonitorConfig[]>([])
  const loading = ref(false)
  const lastUpdated = ref<Date | null>(null)
  const isTrading = ref(false)  // 是否交易时间
  const cacheTtl = ref(10)  // 后端缓存时间
  const currentInterval = ref(REFRESH_INTERVAL_NON_TRADING)  // 当前刷新间隔
  
  // 定时器
  let refreshTimer: number | null = null
  let isStoreActive = true  // 标记 store 是否活跃
  
  // 计算属性
  const monitorCount = computed(() => monitors.value.length)
  const activeCount = computed(() => monitors.value.filter(m => m.is_active !== false).length)
  const upCount = computed(() => monitors.value.filter(m => (m.change_percent || m.change || 0) > 0).length)
  const downCount = computed(() => monitors.value.filter(m => (m.change_percent || m.change || 0) < 0).length)
  const alertCount = computed(() => monitors.value.filter(m => m.has_alert).length)
  
  /**
   * 加载监测列表 - 使用实时监测 API
   */
  async function loadMonitors(): Promise<void> {
    loading.value = true
    try {
      // 使用新的实时监测 API
      const result = await realtimeApi.getRealtimeMonitors()
      monitors.value = result.monitors || []
      
      // 检查交易状态是否变化，动态调整刷新间隔
      const wasTrading = isTrading.value
      isTrading.value = result.is_trading || false
      cacheTtl.value = result.cache_ttl || 10
      lastUpdated.value = new Date()
      
      // 如果交易状态变化，重新设置定时器
      if (wasTrading !== isTrading.value && refreshTimer) {
        console.log(`交易状态变化: ${wasTrading} -> ${isTrading.value}，调整刷新间隔`)
        restartAutoRefresh()
      }
    } catch (error) {
      console.error('加载监测列表失败:', error)
      // 如果实时 API 失败，回退到普通 API
      try {
        const list = await monitorApi.getList()
        monitors.value = list
        lastUpdated.value = new Date()
      } catch (fallbackError) {
        console.error('回退 API 也失败:', fallbackError)
        throw fallbackError
      }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 创建监测
   */
  async function createMonitor(data: CreateMonitorRequest): Promise<MonitorConfig> {
    try {
      const monitor = await monitorApi.create(data)
      // 重新加载列表以获取完整数据
      await loadMonitors()
      return monitor
    } catch (error) {
      console.error('创建监测失败:', error)
      throw error
    }
  }
  
  /**
   * 更新监测
   */
  async function updateMonitor(id: number, data: UpdateMonitorRequest): Promise<void> {
    try {
      await monitorApi.update(id, data)
      // 更新本地状态
      const index = monitors.value.findIndex(m => m.id === id)
      if (index !== -1) {
        monitors.value[index] = { ...monitors.value[index], ...data }
      }
    } catch (error) {
      console.error('更新监测失败:', error)
      throw error
    }
  }
  
  /**
   * 切换监测状态
   */
  async function toggleMonitor(id: number, isActive: boolean): Promise<void> {
    await updateMonitor(id, { is_active: isActive })
  }
  
  /**
   * 删除监测
   */
  async function deleteMonitor(id: number): Promise<void> {
    try {
      await monitorApi.delete(id)
      // 从本地列表中移除
      monitors.value = monitors.value.filter(m => m.id !== id)
    } catch (error) {
      console.error('删除监测失败:', error)
      throw error
    }
  }
  
  /**
   * 根据 ID 获取监测
   */
  function getMonitorById(id: number): MonitorConfig | undefined {
    return monitors.value.find(m => m.id === id)
  }
  
  /**
   * 根据股票 ID 获取监测
   */
  function getMonitorByStockId(stockId: number): MonitorConfig | undefined {
    return monitors.value.find(m => m.stock_id === stockId)
  }
  
  /**
   * 检查股票是否已被监测
   */
  function isStockMonitored(stockId: number): boolean {
    return monitors.value.some(m => m.stock_id === stockId)
  }
  
  /**
   * 开始自动刷新
   * 交易时间内每 15 秒刷新，非交易时间每 60 秒刷新
   */
  function startAutoRefresh(): void {
    stopAutoRefresh()
    isStoreActive = true
    
    // 根据是否交易时间选择刷新间隔
    currentInterval.value = isTrading.value ? REFRESH_INTERVAL_TRADING : REFRESH_INTERVAL_NON_TRADING
    
    refreshTimer = setInterval(() => {
      if (isStoreActive) {
        loadMonitors().catch(console.error)
      }
    }, currentInterval.value) as unknown as number
    
    console.log(`监测自动刷新已启动，交易时间: ${isTrading.value}，间隔: ${currentInterval.value / 1000}秒`)
  }
  
  /**
   * 重启自动刷新（用于交易状态变化时）
   */
  function restartAutoRefresh(): void {
    if (refreshTimer) {
      startAutoRefresh()
    }
  }
  
  /**
   * 停止自动刷新
   */
  function stopAutoRefresh(): void {
    isStoreActive = false
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }
  
  /**
   * 根据交易状态调整刷新间隔（已废弃，使用 restartAutoRefresh）
   */
  function adjustRefreshInterval(): void {
    restartAutoRefresh()
  }
  
  /**
   * 清空状态
   */
  function clear(): void {
    monitors.value = []
    lastUpdated.value = null
    stopAutoRefresh()
  }
  
  return {
    // 状态
    monitors,
    loading,
    lastUpdated,
    isTrading,
    cacheTtl,
    currentInterval,
    
    // 计算属性
    monitorCount,
    activeCount,
    upCount,
    downCount,
    alertCount,
    
    // 方法
    loadMonitors,
    createMonitor,
    updateMonitor,
    toggleMonitor,
    deleteMonitor,
    getMonitorById,
    getMonitorByStockId,
    isStockMonitored,
    startAutoRefresh,
    stopAutoRefresh,
    adjustRefreshInterval,
    clear
  }
})
