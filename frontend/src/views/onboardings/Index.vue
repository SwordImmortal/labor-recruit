<template>
  <div class="page-container">
    <div class="page-card">
      <h2 class="page-title">入职管理</h2>
      
      <!-- 搜索表单 -->
      <div class="search-form">
        <a-form layout="inline">
          <a-form-item label="状态">
            <a-select v-model:value="searchForm.status" placeholder="全部" allowClear style="width: 120px">
              <a-select-option value="pending">待上线</a-select-option>
              <a-select-option value="online">在职</a-select-option>
              <a-select-option value="offline">已离职</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="项目">
            <a-select v-model:value="searchForm.project_id" placeholder="全部" allowClear style="width: 150px">
              <a-select-option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item>
            <a-space>
              <a-button type="primary" @click="fetchOnboardings">查询</a-button>
              <a-button @click="resetSearch">重置</a-button>
            </a-space>
          </a-form-item>
        </a-form>
      </div>

      <!-- 操作按钮 -->
      <div class="table-actions">
        <a-button type="primary" @click="showAddModal">入职登记</a-button>
      </div>

      <a-table
        :columns="columns"
        :data-source="onboardings"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        :scroll="{ x: 1000 }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            {{ record.candidate?.name || '-' }}
          </template>
          <template v-if="column.key === 'phone'">
            <span class="phone-mask">{{ maskPhone(record.candidate?.phone) }}</span>
          </template>
          <template v-if="column.key === 'project'">
            {{ record.project?.name || '-' }}
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">{{ getStatusText(record.status) }}</a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="showEditModal(record)">编辑</a-button>
              <a-button 
                v-if="record.status !== 'offline'" 
                type="link" 
                size="small" 
                danger
                @click="showResignModal(record)"
              >离职</a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 入职登记弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑入职信息' : '入职登记'"
      @ok="handleSubmit"
      :confirm-loading="submitting"
      :width="600"
    >
      <a-form :model="form" :rules="rules" ref="formRef" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="候选人" name="candidate_id" v-if="!isEdit">
              <a-select
                v-model:value="form.candidate_id"
                show-search
                placeholder="搜索候选人"
                :filter-option="false"
                @search="searchCandidates"
                style="width: 100%"
              >
                <a-select-option v-for="c in candidateOptions" :key="c.id" :value="c.id">
                  {{ c.name }} - {{ c.phone }}
                </a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="候选人" v-else>
              <a-input :value="currentOnboarding?.candidate?.name" disabled />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="入职项目" name="project_id">
              <a-select v-model:value="form.project_id" placeholder="请选择项目" style="width: 100%">
                <a-select-option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="入职城市" name="city">
              <a-input v-model:value="form.city" placeholder="请输入城市" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="身份证号">
              <a-input v-model:value="form.id_card" placeholder="请输入身份证号" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="入职日期" name="onboard_date">
              <a-date-picker v-model:value="form.onboard_date" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="上线日期">
              <a-date-picker v-model:value="form.online_date" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="购包日期">
              <a-date-picker v-model:value="form.buy_pack_date" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="状态">
              <a-select v-model:value="form.status" style="width: 100%">
                <a-select-option value="pending">待上线</a-select-option>
                <a-select-option value="online">在职</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="备注">
          <a-textarea v-model:value="form.note" :rows="2" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 离职登记弹窗 -->
    <a-modal
      v-model:open="resignModalVisible"
      title="离职登记"
      @ok="handleResign"
      :confirm-loading="resignSubmitting"
    >
      <a-form :model="resignForm" :rules="resignRules" ref="resignFormRef" layout="vertical">
        <a-form-item label="离职日期" name="resign_date">
          <a-date-picker v-model:value="resignForm.resign_date" style="width: 100%" />
        </a-form-item>
        <a-form-item label="离职原因" name="reason">
          <a-select v-model:value="resignForm.reason" placeholder="请选择" style="width: 100%">
            <a-select-option value="voluntary">主动离职</a-select-option>
            <a-select-option value="involuntary">被动离职</a-select-option>
            <a-select-option value="other">其他</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="离职原因详情">
          <a-textarea v-model:value="resignForm.reason_detail" :rows="2" />
        </a-form-item>
        <a-form-item label="是否需要补招">
          <a-radio-group v-model:value="resignForm.need_replace">
            <a-radio :value="true">需要补招</a-radio>
            <a-radio :value="false">不需要</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item v-if="resignForm.need_replace === false" label="不补招原因">
          <a-input v-model:value="resignForm.no_replace_reason" />
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
const onboardings = ref<any[]>([])
const projects = ref<any[]>([])
const candidateOptions = ref<any[]>([])

const modalVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const currentId = ref<number | null>(null)
const currentOnboarding = ref<any>(null)
const formRef = ref<FormInstance>()

const resignModalVisible = ref(false)
const resignSubmitting = ref(false)
const resignFormRef = ref<FormInstance>()

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})

const searchForm = reactive({
  status: undefined as string | undefined,
  project_id: undefined as number | undefined
})

const columns = [
  { title: '姓名', key: 'name', width: 100 },
  { title: '手机号', key: 'phone', width: 120 },
  { title: '项目', key: 'project', width: 150 },
  { title: '入职城市', dataIndex: 'city', key: 'city', width: 100 },
  { title: '入职日期', dataIndex: 'onboard_date', key: 'onboard_date', width: 100 },
  { title: '状态', key: 'status', width: 90 },
  { title: '操作', key: 'action', fixed: 'right', width: 120 }
]

const form = reactive({
  candidate_id: undefined as number | undefined,
  project_id: undefined as number | undefined,
  city: '',
  id_card: '',
  onboard_date: null as any,
  online_date: null as any,
  buy_pack_date: null as any,
  status: 'pending',
  note: ''
})

const rules = {
  candidate_id: [{ required: true, message: '请选择候选人' }],
  project_id: [{ required: true, message: '请选择项目' }],
  city: [{ required: true, message: '请输入城市' }],
  onboard_date: [{ required: true, message: '请选择入职日期' }]
}

const resignForm = reactive({
  resign_date: null as any,
  reason: undefined as string | undefined,
  reason_detail: '',
  need_replace: undefined as boolean | undefined,
  no_replace_reason: ''
})

const resignRules = {
  resign_date: [{ required: true, message: '请选择离职日期' }],
  reason: [{ required: true, message: '请选择离职原因' }]
}

function resetForm() {
  Object.assign(form, {
    candidate_id: undefined,
    project_id: undefined,
    city: '',
    id_card: '',
    onboard_date: null,
    online_date: null,
    buy_pack_date: null,
    status: 'pending',
    note: ''
  })
}

function resetResignForm() {
  Object.assign(resignForm, {
    resign_date: null,
    reason: undefined,
    reason_detail: '',
    need_replace: undefined,
    no_replace_reason: ''
  })
}

async function fetchOnboardings() {
  loading.value = true
  try {
    const res = await request.get('/onboardings', {
      params: {
        skip: (pagination.current - 1) * pagination.pageSize,
        limit: pagination.pageSize,
        ...searchForm
      }
    })
    onboardings.value = res
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function fetchProjects() {
  try {
    const res = await request.get('/projects', { params: { limit: 100 } })
    projects.value = res
  } catch (error) {
    console.error(error)
  }
}

async function searchCandidates(keyword: string) {
  if (!keyword) return
  try {
    const res = await request.get('/candidates', {
      params: { keyword, limit: 10 }
    })
    candidateOptions.value = res
  } catch (error) {
    console.error(error)
  }
}

function resetSearch() {
  searchForm.status = undefined
  searchForm.project_id = undefined
  fetchOnboardings()
}

function handleTableChange(pag: any) {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchOnboardings()
}

function showAddModal() {
  isEdit.value = false
  currentId.value = null
  currentOnboarding.value = null
  resetForm()
  modalVisible.value = true
}

function showEditModal(record: any) {
  isEdit.value = true
  currentId.value = record.id
  currentOnboarding.value = record
  Object.assign(form, {
    ...record,
    candidate_id: record.candidate_id,
    project_id: record.project_id,
    onboard_date: record.onboard_date ? dayjs(record.onboard_date) : null,
    online_date: record.online_date ? dayjs(record.online_date) : null,
    buy_pack_date: record.buy_pack_date ? dayjs(record.buy_pack_date) : null
  })
  modalVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    submitting.value = true
    
    const data = {
      ...form,
      onboard_date: form.onboard_date ? dayjs(form.onboard_date).format('YYYY-MM-DD') : null,
      online_date: form.online_date ? dayjs(form.online_date).format('YYYY-MM-DD') : null,
      buy_pack_date: form.buy_pack_date ? dayjs(form.buy_pack_date).format('YYYY-MM-DD') : null
    }
    
    if (isEdit.value && currentId.value) {
      await request.put(`/onboardings/${currentId.value}`, data)
      message.success('更新成功')
    } else {
      await request.post('/onboardings', data)
      message.success('入职登记成功')
    }
    
    modalVisible.value = false
    fetchOnboardings()
  } catch (error) {
    console.error(error)
  } finally {
    submitting.value = false
  }
}

function showResignModal(record: any) {
  currentId.value = record.id
  currentOnboarding.value = record
  resetResignForm()
  resignForm.resign_date = dayjs()
  resignModalVisible.value = true
}

async function handleResign() {
  try {
    await resignFormRef.value?.validate()
    resignSubmitting.value = true
    
    await request.post(`/onboardings/${currentId.value}/resign`, {
      resign_date: dayjs(resignForm.resign_date).format('YYYY-MM-DD'),
      reason: resignForm.reason,
      reason_detail: resignForm.reason_detail,
      need_replace: resignForm.need_replace,
      no_replace_reason: resignForm.no_replace_reason
    })
    
    message.success('离职登记成功')
    resignModalVisible.value = false
    fetchOnboardings()
  } catch (error) {
    console.error(error)
  } finally {
    resignSubmitting.value = false
  }
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    pending: '待上线',
    online: '在职',
    offline: '已离职'
  }
  return map[status] || status
}

function getStatusColor(status: string) {
  const map: Record<string, string> = {
    pending: 'warning',
    online: 'success',
    offline: 'default'
  }
  return map[status] || 'default'
}

function maskPhone(phone: string) {
  if (!phone) return ''
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

onMounted(() => {
  fetchOnboardings()
  fetchProjects()
})
</script>

<style scoped>
.page-container { padding: 16px; }
.page-card { background: #fff; border-radius: 8px; padding: 16px; }
.search-form { margin-bottom: 16px; padding: 16px; background: #fafafa; border-radius: 8px; }
.table-actions { margin-bottom: 16px; }
</style>
