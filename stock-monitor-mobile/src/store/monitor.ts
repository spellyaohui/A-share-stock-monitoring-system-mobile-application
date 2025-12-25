// ============================================
// 股票监测系统移动端 - 监测状态管理
// ============================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { monitorApi } from '@/api'
import type { MonitorConfig, CreateMonitorRequest, UpdateMonitorRequest } from '@/types'

// 自动刷新间隔（毫秒）
const REFRESH_INTERVAL = 30000

export const useMonitorStore = defineStore('monitor', () => {
  // 状态
  const monitors = ref<MonitorConfig[]>([])
  const loading = ref(false)
  const lastUpdated = ref<Date | null>(null)
  
  // 定时器
  let refreshTimer: number | null = null
  
  // 计算属性
  const monitorCount = computed(() => monitors.value.length)
  const activeCount = computed(() => monitors.value.filter(m => m.is_active !== false).length)
  const upCount = computed(() => monitors.value.filter(m => (m.change || 0) > 0).length)
  const downCount = computed(() => monitors.value.filter(m => (m.change || 0) < 0).length)
  
  /**
   * 加载监测列表
   */
  async function loadMonitors(): Promise<void> {
    loading.value = true
    try {
      const list = await monitorApi.getList()
      monitors.value = list
      lastUpdated.value = new Date()
    } catch (error) {
      console.error('加载监测列表失败:', error)
      throw error
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
   */
  function startAutoRefresh(): void {
    stopAutoRefresh()
    refreshTimer = setInterval(() => {
      loadMonitors().catch(console.error)
    }, REFRESH_INTERVAL) as unknown as number
  }
  
  /**
   * 停止自动刷新
   */
  function stopAutoRefresh(): void {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
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
    
    // 计算属性
    monitorCount,
    activeCount,
    upCount,
    downCount,
    
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
    clear
  }
})
