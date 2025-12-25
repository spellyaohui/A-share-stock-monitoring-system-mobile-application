<template>
  <el-container class="settings-container">
    <el-header class="settings-header">
      <el-button :icon="ArrowLeft" @click="router.back()">返回</el-button>
      <h2>设置</h2>
    </el-header>

    <el-main class="settings-main">
      <el-card class="settings-card">
        <template #header>
          <span>通知配置</span>
        </template>
        <el-form :model="configForm" label-width="120px">
          <el-form-item label="启用通知">
            <el-switch v-model="configForm.is_enabled" />
          </el-form-item>
          <el-form-item label="API地址">
            <el-input v-model="configForm.api_url" placeholder="请输入Webhook地址" />
          </el-form-item>
          <el-form-item label="请求方法">
            <el-select v-model="configForm.api_method">
              <el-option label="POST" value="POST" />
              <el-option label="GET" value="GET" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveConfig" :loading="saving">保存</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="settings-card">
        <template #header>
          <span>通知历史</span>
        </template>
        <el-timeline>
          <el-timeline-item
            v-for="item in history"
            :key="item.id"
            :timestamp="item.created_at"
          >
            <div class="notification-content">{{ item.content }}</div>
            <el-tag :type="item.is_sent ? 'success' : 'danger'" size="small">
              {{ item.is_sent ? '已发送' : '未发送' }}
            </el-tag>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-if="history.length === 0" description="暂无通知记录" />
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { api } from '@/api'

const router = useRouter()

const configForm = ref({
  api_url: '',
  api_method: 'POST',
  api_headers: {},
  is_enabled: false
})

const history = ref<any[]>([])
const saving = ref(false)

onMounted(async () => {
  await loadConfig()
  await loadHistory()
})

async function loadConfig() {
  try {
    const res = await api.notifications.getConfig()
    configForm.value = {
      api_url: res.api_url || '',
      api_method: res.api_method || 'POST',
      api_headers: res.api_headers || {},
      is_enabled: res.is_enabled || false
    }
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

async function loadHistory() {
  try {
    const res = await api.notifications.getHistory()
    history.value = res
  } catch (error) {
    console.error('加载历史失败:', error)
  }
}

async function saveConfig() {
  saving.value = true
  try {
    await api.notifications.updateConfig(configForm.value)
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.settings-container {
  height: 100vh;
}

.settings-header {
  background: #fff;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 20px;
}

.settings-main {
  background: #f5f5f5;
  padding: 20px;
  display: flex;
  gap: 20px;
}

.settings-card {
  flex: 1;
}

.notification-content {
  white-space: pre-wrap;
  margin-bottom: 10px;
}
</style>
