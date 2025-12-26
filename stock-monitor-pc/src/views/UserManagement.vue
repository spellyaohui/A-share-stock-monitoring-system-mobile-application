<template>
  <el-container class="user-management-container">
    <el-header class="page-header">
      <el-button :icon="ArrowLeft" @click="router.back()">返回</el-button>
      <h2>用户管理</h2>
      <el-button type="primary" :icon="Plus" @click="showAddDialog = true">添加用户</el-button>
    </el-header>

    <el-main class="page-main">
      <el-card>
        <el-table :data="users" v-loading="loading" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="email" label="邮箱">
            <template #default="{ row }">
              {{ row.email || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                :icon="Edit"
                @click="handleEditPassword(row)"
              >
                改密
              </el-button>
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="handleDelete(row)"
                :disabled="row.id === currentUser?.id"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && users.length === 0" description="暂无用户" />
      </el-card>
    </el-main>

    <!-- 添加用户对话框 -->
    <el-dialog v-model="showAddDialog" title="添加用户" width="400px">
      <el-form :model="addForm" :rules="formRules" ref="addFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="addForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="addForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="addForm.email" placeholder="请输入邮箱（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAdd" :loading="adding">确定</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="400px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="80px">
        <el-form-item label="用户">
          <el-input :value="editingUser?.username" disabled />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdatePassword" :loading="updating">确定</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { ArrowLeft, Plus, Delete, Edit } from '@element-plus/icons-vue'
import { api } from '@/api'
import { useUserStore } from '@/store/user'
import type { User } from '@/types'

const router = useRouter()
const userStore = useUserStore()
const currentUser = userStore.user

const users = ref<User[]>([])
const loading = ref(false)
const showAddDialog = ref(false)
const showPasswordDialog = ref(false)
const adding = ref(false)
const updating = ref(false)
const addFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()
const editingUser = ref<User | null>(null)

const addForm = ref({
  username: '',
  password: '',
  email: ''
})

const passwordForm = ref({
  newPassword: '',
  confirmPassword: ''
})

const formRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度为 2-50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 4, max: 50, message: '密码长度为 4-50 个字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

const passwordRules: FormRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 4, max: 50, message: '密码长度为 4-50 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.value.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 格式化日期
function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 加载用户列表
async function loadUsers() {
  loading.value = true
  try {
    users.value = await api.users.getList()
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

// 添加用户
async function handleAdd() {
  if (!addFormRef.value) return
  
  await addFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    adding.value = true
    try {
      await api.auth.register(
        addForm.value.username,
        addForm.value.password,
        addForm.value.email || undefined
      )
      ElMessage.success('用户添加成功')
      showAddDialog.value = false
      addForm.value = { username: '', password: '', email: '' }
      await loadUsers()
    } catch (error: any) {
      const message = error.response?.data?.detail || '添加用户失败'
      ElMessage.error(message)
    } finally {
      adding.value = false
    }
  })
}

// 打开修改密码对话框
function handleEditPassword(user: User) {
  editingUser.value = user
  passwordForm.value = { newPassword: '', confirmPassword: '' }
  showPasswordDialog.value = true
}

// 修改密码
async function handleUpdatePassword() {
  if (!passwordFormRef.value || !editingUser.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    updating.value = true
    try {
      await api.users.updatePassword(editingUser.value!.id, passwordForm.value.newPassword)
      ElMessage.success('密码修改成功')
      showPasswordDialog.value = false
    } catch (error: any) {
      const message = error.response?.data?.detail || '修改密码失败'
      ElMessage.error(message)
    } finally {
      updating.value = false
    }
  })
}

// 删除用户
async function handleDelete(user: User) {
  if (user.id === currentUser?.id) {
    ElMessage.warning('不能删除当前登录用户')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.users.delete(user.id)
    ElMessage.success('用户删除成功')
    await loadUsers()
  } catch (error: any) {
    if (error !== 'cancel') {
      const message = error.response?.data?.detail || '删除用户失败'
      ElMessage.error(message)
    }
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management-container {
  height: 100vh;
}

.page-header {
  background: #fff;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 20px;
}

.page-header h2 {
  flex: 1;
  margin: 0;
}

.page-main {
  background: #f5f5f5;
  padding: 20px;
}
</style>
