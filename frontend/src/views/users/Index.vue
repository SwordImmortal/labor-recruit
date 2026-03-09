<template>
  <div class="page-container">
    <div class="page-card">
      <h2 class="page-title">用户管理</h2>
      
      <!-- 操作按钮 -->
      <div class="table-actions">
        <a-button type="primary" @click="showAddModal">新增用户</a-button>
      </div>

      <a-table
        :columns="columns"
        :data-source="users"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'role'">
            <a-tag :color="getRoleColor(record.role)">{{ getRoleText(record.role) }}</a-tag>
          </template>
          <template v-if="column.key === 'is_active'">
            <a-switch 
              :checked="record.is_active" 
              @change="(checked: boolean) => toggleStatus(record, checked)"
            />
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="showEditModal(record)">编辑</a-button>
              <a-button type="link" size="small" @click="resetPassword(record)">重置密码</a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 新增/编辑弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑用户' : '新增用户'"
      @ok="handleSubmit"
      :confirm-loading="submitting"
    >
      <a-form :model="form" :rules="rules" ref="formRef" layout="vertical">
        <a-form-item label="用户名" name="username">
          <a-input v-model:value="form.username" placeholder="请输入用户名" :disabled="isEdit" />
        </a-form-item>
        <a-form-item label="手机号" name="phone">
          <a-input v-model:value="form.phone" placeholder="请输入手机号" />
        </a-form-item>
        <a-form-item label="真实姓名" name="real_name">
          <a-input v-model:value="form.real_name" placeholder="请输入真实姓名" />
        </a-form-item>
        <a-form-item label="角色" name="role">
          <a-select v-model:value="form.role" placeholder="请选择">
            <a-select-option value="admin">管理员</a-select-option>
            <a-select-option value="supervisor">招聘主管</a-select-option>
            <a-select-option value="recruiter">招聘专员</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item v-if="!isEdit" label="密码" name="password">
          <a-input-password v-model:value="form.password" placeholder="请输入密码" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import type { FormInstance } from 'ant-design-vue'
import request from '@/api/request'

const loading = ref(false)
const users = ref<any[]>([])
const modalVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const currentId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})

const columns = [
  { title: '用户名', dataIndex: 'username', key: 'username', width: 120 },
  { title: '手机号', dataIndex: 'phone', key: 'phone', width: 120 },
  { title: '真实姓名', dataIndex: 'real_name', key: 'real_name', width: 100 },
  { title: '角色', dataIndex: 'role', key: 'role', width: 100 },
  { title: '状态', dataIndex: 'is_active', key: 'is_active', width: 80 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 150 },
  { title: '操作', key: 'action', width: 140 }
]

const form = reactive({
  username: '',
  phone: '',
  real_name: '',
  role: 'recruiter',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名' }],
  phone: [
    { required: true, message: '请输入手机号' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' }
  ],
  role: [{ required: true, message: '请选择角色' }],
  password: [{ required: true, message: '请输入密码' }]
}

function resetForm() {
  Object.assign(form, {
    username: '',
    phone: '',
    real_name: '',
    role: 'recruiter',
    password: ''
  })
}

async function fetchUsers() {
  loading.value = true
  try {
    const res = await request.get('/users', {
      params: {
        skip: (pagination.current - 1) * pagination.pageSize,
        limit: pagination.pageSize
      }
    })
    users.value = res
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

function handleTableChange(pag: any) {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchUsers()
}

function showAddModal() {
  isEdit.value = false
  currentId.value = null
  resetForm()
  modalVisible.value = true
}

function showEditModal(record: any) {
  isEdit.value = true
  currentId.value = record.id
  Object.assign(form, {
    username: record.username,
    phone: record.phone,
    real_name: record.real_name,
    role: record.role,
    password: ''
  })
  modalVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    submitting.value = true
    
    const data = { ...form }
    if (isEdit.value) {
      delete (data as any).password
    }
    
    if (isEdit.value && currentId.value) {
      await request.put(`/users/${currentId.value}`, data)
      message.success('更新成功')
    } else {
      await request.post('/users', data)
      message.success('创建成功')
    }
    
    modalVisible.value = false
    fetchUsers()
  } catch (error) {
    console.error(error)
  } finally {
    submitting.value = false
  }
}

async function toggleStatus(record: any, checked: boolean) {
  try {
    await request.put(`/users/${record.id}`, { is_active: checked })
    message.success(checked ? '已启用' : '已停用')
    fetchUsers()
  } catch (error) {
    console.error(error)
  }
}

function resetPassword(record: any) {
  Modal.confirm({
    title: '确认重置密码？',
    content: `将重置用户「${record.username}」的密码为默认密码`,
    okText: '确认',
    cancelText: '取消',
    onOk: async () => {
      try {
        await request.post(`/users/${record.id}/reset-password`)
        message.success('密码已重置')
      } catch (error) {
        console.error(error)
      }
    }
  })
}

function getRoleText(role: string) {
  const map: Record<string, string> = {
    admin: '管理员',
    supervisor: '招聘主管',
    recruiter: '招聘专员'
  }
  return map[role] || role
}

function getRoleColor(role: string) {
  const map: Record<string, string> = {
    admin: 'red',
    supervisor: 'blue',
    recruiter: 'green'
  }
  return map[role] || 'default'
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.page-container { padding: 16px; }
.page-card { background: #fff; border-radius: 8px; padding: 16px; }
.table-actions { margin-bottom: 16px; }
</style>
