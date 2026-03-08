<template>
  <div class="page-container">
    <div class="page-card">
      <h2 class="page-title">候选人管理</h2>
      
      <!-- 搜索表单 -->
      <div class="search-form">
        <a-form layout="inline" :model="searchForm">
          <a-row :gutter="16" style="width: 100%">
            <a-col :xs="24" :sm="8" :md="6">
              <a-form-item label="关键词">
                <a-input v-model:value="searchForm.keyword" placeholder="姓名/手机/微信" allowClear />
              </a-form-item>
            </a-col>
            <a-col :xs="24" :sm="8" :md="6">
              <a-form-item label="状态">
                <a-select v-model:value="searchForm.status" placeholder="全部" allowClear style="width: 100%">
                  <a-select-option value="lead">线索</a-select-option>
                  <a-select-option value="wechat">已加微信</a-select-option>
                  <a-select-option value="interview">已约面</a-select-option>
                  <a-select-option value="interviewed">已到面</a-select-option>
                  <a-select-option value="onboarded">已入职</a-select-option>
                  <a-select-option value="lost">流失</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :xs="24" :sm="8" :md="6">
              <a-form-item label="项目">
                <a-select v-model:value="searchForm.project_id" placeholder="全部" allowClear style="width: 100%">
                  <a-select-option v-for="p in projects" :key="p.id" :value="p.id">
                    {{ p.name }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :xs="24" :sm="24" :md="6">
              <a-space>
                <a-button type="primary" @click="fetchCandidates">查询</a-button>
                <a-button @click="resetSearch">重置</a-button>
              </a-space>
            </a-col>
          </a-row>
        </a-form>
      </div>

      <!-- 操作按钮 -->
      <div class="table-actions">
        <a-button type="primary" @click="showAddModal">新增候选人</a-button>
      </div>

      <!-- 候选人列表 -->
      <a-table
        :columns="columns"
        :data-source="candidates"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        :scroll="{ x: 800 }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'phone'">
            <span class="phone-mask">{{ maskPhone(record.phone) }}</span>
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">{{ getStatusText(record.status) }}</a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="viewDetail(record)">详情</a-button>
              <a-button type="link" size="small" @click="showFollowModal(record)">跟进</a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 新增候选人弹窗 -->
    <a-modal
      v-model:open="addModalVisible"
      title="新增候选人"
      @ok="handleAdd"
      :width="600"
    >
      <a-form :model="addForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="姓名" required>
              <a-input v-model:value="addForm.name" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="手机号" required>
              <a-input v-model:value="addForm.phone" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="微信号">
              <a-input v-model:value="addForm.wechat" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="年龄">
              <a-input-number v-model:value="addForm.age" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="渠道">
              <a-select v-model:value="addForm.channel_id" placeholder="请选择" style="width: 100%">
                <a-select-option v-for="c in channels" :key="c.id" :value="c.id">
                  {{ c.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="应聘项目">
              <a-select v-model:value="addForm.project_id" placeholder="请选择" style="width: 100%">
                <a-select-option v-for="p in projects" :key="p.id" :value="p.id">
                  {{ p.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="备注">
          <a-textarea v-model:value="addForm.note" :rows="3" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 跟进弹窗 -->
    <a-modal
      v-model:open="followModalVisible"
      title="添加跟进"
      @ok="handleFollow"
    >
      <a-form :model="followForm" layout="vertical">
        <a-form-item label="变更状态">
          <a-select v-model:value="followForm.status_to" placeholder="请选择">
            <a-select-option value="wechat">已加微信</a-select-option>
            <a-select-option value="interview">已约面</a-select-option>
            <a-select-option value="interviewed">已到面</a-select-option>
            <a-select-option value="onboarded">已入职</a-select-option>
            <a-select-option value="lost">流失</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="跟进内容">
          <a-textarea v-model:value="followForm.content" :rows="3" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import request from '@/api/request'

const router = useRouter()

// 数据
const candidates = ref<any[]>([])
const projects = ref<any[]>([])
const channels = ref<any[]>([])
const loading = ref(false)

// 分页
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: undefined as string | undefined,
  project_id: undefined as number | undefined
})

// 新增表单
const addModalVisible = ref(false)
const addForm = reactive({
  name: '',
  phone: '',
  wechat: '',
  age: undefined as number | undefined,
  channel_id: undefined as number | undefined,
  project_id: undefined as number | undefined,
  note: ''
})

// 跟进表单
const followModalVisible = ref(false)
const currentCandidate = ref<any>(null)
const followForm = reactive({
  status_to: undefined as string | undefined,
  content: ''
})

// 表格列
const columns = [
  { title: '姓名', dataIndex: 'name', key: 'name', width: 100 },
  { title: '手机号', dataIndex: 'phone', key: 'phone', width: 120 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '应聘项目', dataIndex: 'project_name', key: 'project_name', width: 150 },
  { title: '渠道', dataIndex: 'channel_name', key: 'channel_name', width: 100 },
  { title: '最后跟进', dataIndex: 'last_follow_at', key: 'last_follow_at', width: 150 },
  { title: '操作', key: 'action', fixed: 'right', width: 120 }
]

// 方法
async function fetchCandidates() {
  loading.value = true
  try {
    const res = await request.get('/candidates', {
      params: {
        skip: (pagination.current - 1) * pagination.pageSize,
        limit: pagination.pageSize,
        ...searchForm
      }
    })
    candidates.value = res
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

async function fetchChannels() {
  try {
    const res = await request.get('/channels')
    channels.value = res
  } catch (error) {
    console.error(error)
  }
}

function resetSearch() {
  searchForm.keyword = ''
  searchForm.status = undefined
  searchForm.project_id = undefined
  fetchCandidates()
}

function handleTableChange(pag: any) {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchCandidates()
}

function showAddModal() {
  Object.assign(addForm, {
    name: '',
    phone: '',
    wechat: '',
    age: undefined,
    channel_id: undefined,
    project_id: undefined,
    note: ''
  })
  addModalVisible.value = true
}

async function handleAdd() {
  try {
    await request.post('/candidates', addForm)
    message.success('添加成功')
    addModalVisible.value = false
    fetchCandidates()
  } catch (error) {
    console.error(error)
  }
}

function showFollowModal(record: any) {
  currentCandidate.value = record
  followForm.status_to = undefined
  followForm.content = ''
  followModalVisible.value = true
}

async function handleFollow() {
  try {
    await request.post(`/candidates/${currentCandidate.value.id}/follow`, null, {
      params: followForm
    })
    message.success('跟进成功')
    followModalVisible.value = false
    fetchCandidates()
  } catch (error) {
    console.error(error)
  }
}

function viewDetail(record: any) {
  router.push(`/candidates/${record.id}`)
}

function maskPhone(phone: string) {
  if (!phone) return ''
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    lead: '线索',
    wechat: '已加微信',
    interview: '已约面',
    interviewed: '已到面',
    onboarded: '已入职',
    lost: '流失'
  }
  return map[status] || status
}

function getStatusColor(status: string) {
  const map: Record<string, string> = {
    lead: 'default',
    wechat: 'blue',
    interview: 'orange',
    interviewed: 'green',
    onboarded: 'success',
    lost: 'red'
  }
  return map[status] || 'default'
}

onMounted(() => {
  fetchCandidates()
  fetchProjects()
  fetchChannels()
})
</script>

<style scoped>
.page-container {
  padding: 16px;
}

.page-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.search-form {
  margin-bottom: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.table-actions {
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .page-container {
    padding: 12px;
  }
  
  .search-form .ant-form-item {
    margin-bottom: 12px;
  }
}
</style>
