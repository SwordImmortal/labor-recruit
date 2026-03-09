<template>
  <div class="page-container">
    <div class="page-card">
      <h2 class="page-title">渠道管理</h2>
      
      <!-- 操作按钮 -->
      <div class="table-actions">
        <a-button type="primary" @click="showAddModal">新增渠道</a-button>
      </div>

      <a-table
        :columns="columns"
        :data-source="channels"
        :loading="loading"
        :pagination="false"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'type'">
            <a-tag :color="getTypeColor(record.type)">{{ getTypeText(record.type) }}</a-tag>
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
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 新增/编辑弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑渠道' : '新增渠道'"
      @ok="handleSubmit"
      :confirm-loading="submitting"
    >
      <a-form :model="form" :rules="rules" ref="formRef" layout="vertical">
        <a-form-item label="渠道名称" name="name">
          <a-input v-model:value="form.name" placeholder="请输入渠道名称" />
        </a-form-item>
        <a-form-item label="渠道类型" name="type">
          <a-select v-model:value="form.type" placeholder="请选择">
            <a-select-option value="boss">BOSS直聘</a-select-option>
            <a-select-option value="kuaishou">快手</a-select-option>
            <a-select-option value="wuba">58同城</a-select-option>
            <a-select-option value="douyin">抖音</a-select-option>
            <a-select-option value="offline">线下</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="渠道账号">
          <a-input v-model:value="form.account" placeholder="请输入渠道账号" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="form.description" :rows="2" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import type { FormInstance } from 'ant-design-vue'
import request from '@/api/request'

const loading = ref(false)
const channels = ref<any[]>([])
const modalVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const currentId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const columns = [
  { title: '渠道名称', dataIndex: 'name', key: 'name', width: 150 },
  { title: '渠道类型', dataIndex: 'type', key: 'type', width: 120 },
  { title: '渠道账号', dataIndex: 'account', key: 'account', width: 150 },
  { title: '状态', dataIndex: 'is_active', key: 'is_active', width: 100 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 150 },
  { title: '操作', key: 'action', width: 80 }
]

const form = reactive({
  name: '',
  type: undefined as string | undefined,
  account: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入渠道名称' }],
  type: [{ required: true, message: '请选择渠道类型' }]
}

function resetForm() {
  Object.assign(form, {
    name: '',
    type: undefined,
    account: '',
    description: ''
  })
}

async function fetchChannels() {
  loading.value = true
  try {
    const res = await request.get('/channels')
    channels.value = res
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
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
    name: record.name,
    type: record.type,
    account: record.account,
    description: record.description
  })
  modalVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    submitting.value = true
    
    if (isEdit.value && currentId.value) {
      await request.put(`/channels/${currentId.value}`, form)
      message.success('更新成功')
    } else {
      await request.post('/channels', form)
      message.success('创建成功')
    }
    
    modalVisible.value = false
    fetchChannels()
  } catch (error) {
    console.error(error)
  } finally {
    submitting.value = false
  }
}

async function toggleStatus(record: any, checked: boolean) {
  try {
    await request.put(`/channels/${record.id}`, { is_active: checked })
    message.success(checked ? '已启用' : '已停用')
    fetchChannels()
  } catch (error) {
    console.error(error)
  }
}

function getTypeText(type: string) {
  const map: Record<string, string> = {
    boss: 'BOSS直聘',
    kuaishou: '快手',
    wuba: '58同城',
    douyin: '抖音',
    offline: '线下'
  }
  return map[type] || type
}

function getTypeColor(type: string) {
  const map: Record<string, string> = {
    boss: 'blue',
    kuaishou: 'orange',
    wuba: 'red',
    douyin: 'magenta',
    offline: 'green'
  }
  return map[type] || 'default'
}

onMounted(() => {
  fetchChannels()
})
</script>

<style scoped>
.page-container { padding: 16px; }
.page-card { background: #fff; border-radius: 8px; padding: 16px; }
.table-actions { margin-bottom: 16px; }
</style>
