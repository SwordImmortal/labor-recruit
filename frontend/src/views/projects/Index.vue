<template>
  <div class="page-container">
    <div class="page-card">
      <h2 class="page-title">项目管理</h2>
      
      <!-- 操作按钮 -->
      <div class="table-actions">
        <a-button type="primary" @click="showAddModal">新增项目</a-button>
      </div>
      
      <a-table
        :columns="columns"
        :data-source="projects"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        :scroll="{ x: 1000 }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'business_type'">
            <a-tag :color="record.business_type === 'rpo' ? 'blue' : 'green'">
              {{ record.business_type === 'rpo' ? 'RPO' : 'BPO' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'recruit_status'">
            <a-tag :color="getRecruitStatusColor(record.recruit_status)">
              {{ getRecruitStatusText(record.recruit_status) }}
            </a-tag>
          </template>
          <template v-if="column.key === 'operation_status'">
            <a-tag :color="getOperationStatusColor(record.operation_status)">
              {{ getOperationStatusText(record.operation_status) }}
            </a-tag>
          </template>
          <template v-if="column.key === 'progress'">
            <a-progress 
              :percent="getProgress(record)" 
              :size="'small'" 
              :status="getProgressStatus(record)"
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
      :title="isEdit ? '编辑项目' : '新增项目'"
      @ok="handleSubmit"
      :confirm-loading="submitting"
      :width="700"
    >
      <a-form :model="form" :rules="rules" ref="formRef" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="项目名称" name="name">
              <a-input v-model:value="form.name" placeholder="请输入项目名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="业务类型" name="business_type">
              <a-select v-model:value="form.business_type" placeholder="请选择">
                <a-select-option value="rpo">RPO（招聘流程外包）</a-select-option>
                <a-select-option value="bpo">BPO（业务流程外包）</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="城市" name="city">
              <a-input v-model:value="form.city" placeholder="请输入城市" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="目标人数" name="target_count">
              <a-input-number v-model:value="form.target_count" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="开始日期" name="start_date">
              <a-date-picker v-model:value="form.start_date" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="结束日期">
              <a-date-picker v-model:value="form.end_date" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="招聘状态" name="recruit_status">
              <a-select v-model:value="form.recruit_status" placeholder="请选择">
                <a-select-option value="pending">待启动</a-select-option>
                <a-select-option value="recruiting">招聘中</a-select-option>
                <a-select-option value="filled">已招满</a-select-option>
                <a-select-option value="replacing">补招中</a-select-option>
                <a-select-option value="stopped">停招</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="运营状态" name="operation_status">
              <a-select v-model:value="form.operation_status" placeholder="请选择">
                <a-select-option value="pending">待履约</a-select-option>
                <a-select-option value="serving">服务中</a-select-option>
                <a-select-option value="paused">暂停服务</a-select-option>
                <a-select-option value="terminated">已终止</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="入职口径">
              <a-select v-model:value="form.onboard_criteria" placeholder="请选择">
                <a-select-option value="onboard">入职</a-select-option>
                <a-select-option value="buy_pack">购包</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="试单天数">
              <a-input-number v-model:value="form.trial_days" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="是否需要培训">
              <a-switch v-model:checked="form.need_training" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="是否需要购包">
              <a-switch v-model:checked="form.need_buy_pack" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="项目描述">
          <a-textarea v-model:value="form.description" :rows="3" placeholder="请输入项目描述" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import type { FormInstance } from 'ant-design-vue'
import dayjs from 'dayjs'
import request from '@/api/request'

const loading = ref(false)
const projects = ref<any[]>([])
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
  { title: '项目名称', dataIndex: 'name', key: 'name', width: 150 },
  { title: '业务类型', dataIndex: 'business_type', key: 'business_type', width: 80 },
  { title: '城市', dataIndex: 'city', key: 'city', width: 80 },
  { title: '目标人数', dataIndex: 'target_count', key: 'target_count', width: 80 },
  { title: '当前人数', dataIndex: 'current_count', key: 'current_count', width: 80 },
  { title: '进度', key: 'progress', width: 150 },
  { title: '招聘状态', dataIndex: 'recruit_status', key: 'recruit_status', width: 90 },
  { title: '运营状态', dataIndex: 'operation_status', key: 'operation_status', width: 90 },
  { title: '开始日期', dataIndex: 'start_date', key: 'start_date', width: 100 },
  { title: '操作', key: 'action', fixed: 'right', width: 80 }
]

const form = reactive({
  name: '',
  business_type: 'rpo',
  city: '',
  target_count: 0,
  start_date: null as any,
  end_date: null as any,
  recruit_status: 'pending',
  operation_status: 'pending',
  onboard_criteria: 'onboard',
  trial_days: 0,
  need_training: false,
  need_buy_pack: false,
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入项目名称' }],
  business_type: [{ required: true, message: '请选择业务类型' }],
  city: [{ required: true, message: '请输入城市' }],
  start_date: [{ required: true, message: '请选择开始日期' }]
}

function resetForm() {
  Object.assign(form, {
    name: '',
    business_type: 'rpo',
    city: '',
    target_count: 0,
    start_date: null,
    end_date: null,
    recruit_status: 'pending',
    operation_status: 'pending',
    onboard_criteria: 'onboard',
    trial_days: 0,
    need_training: false,
    need_buy_pack: false,
    description: ''
  })
}

async function fetchProjects() {
  loading.value = true
  try {
    const res = await request.get('/projects', {
      params: {
        skip: (pagination.current - 1) * pagination.pageSize,
        limit: pagination.pageSize
      }
    })
    projects.value = res
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

function handleTableChange(pag: any) {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchProjects()
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
    ...record,
    start_date: record.start_date ? dayjs(record.start_date) : null,
    end_date: record.end_date ? dayjs(record.end_date) : null
  })
  modalVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    submitting.value = true
    
    const data = {
      ...form,
      start_date: form.start_date ? dayjs(form.start_date).format('YYYY-MM-DD') : null,
      end_date: form.end_date ? dayjs(form.end_date).format('YYYY-MM-DD') : null
    }
    
    if (isEdit.value && currentId.value) {
      await request.put(`/projects/${currentId.value}`, data)
      message.success('更新成功')
    } else {
      await request.post('/projects', data)
      message.success('创建成功')
    }
    
    modalVisible.value = false
    fetchProjects()
  } catch (error) {
    console.error(error)
  } finally {
    submitting.value = false
  }
}

function getProgress(record: any) {
  if (!record.target_count) return 0
  return Math.round((record.current_count / record.target_count) * 100)
}

function getProgressStatus(record: any) {
  const progress = getProgress(record)
  if (progress >= 100) return 'success'
  if (progress >= 80) return 'normal'
  return 'active'
}

function getRecruitStatusText(status: string) {
  const map: Record<string, string> = {
    pending: '待启动',
    recruiting: '招聘中',
    filled: '已招满',
    replacing: '补招中',
    stopped: '停招'
  }
  return map[status] || status
}

function getRecruitStatusColor(status: string) {
  const map: Record<string, string> = {
    pending: 'default',
    recruiting: 'processing',
    filled: 'success',
    replacing: 'warning',
    stopped: 'error'
  }
  return map[status] || 'default'
}

function getOperationStatusText(status: string) {
  const map: Record<string, string> = {
    pending: '待履约',
    serving: '服务中',
    paused: '暂停服务',
    terminated: '已终止'
  }
  return map[status] || status
}

function getOperationStatusColor(status: string) {
  const map: Record<string, string> = {
    pending: 'default',
    serving: 'processing',
    paused: 'warning',
    terminated: 'error'
  }
  return map[status] || 'default'
}

onMounted(() => {
  fetchProjects()
})
</script>

<style scoped>
.page-container { padding: 16px; }
.page-card { background: #fff; border-radius: 8px; padding: 16px; }
.table-actions { margin-bottom: 16px; }
</style>
