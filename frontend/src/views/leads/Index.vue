<template>
  <div class="page-container">
    <div class="page-card">
      <h2 class="page-title">线索池</h2>
      
      <!-- Tab切换 -->
      <a-tabs v-model:activeKey="poolType" @change="fetchLeads">
        <a-tab-pane key="public" tab="公海线索">
          <template #tab>
            公海线索 <a-badge :count="publicCount" :number-style="{ backgroundColor: '#52c41a' }" />
          </template>
        </a-tab-pane>
        <a-tab-pane key="mine" tab="我的线索">
          <template #tab>
            我的线索 <a-badge :count="mineCount" :number-style="{ backgroundColor: '#1890ff' }" />
          </template>
        </a-tab-pane>
      </a-tabs>
      
      <!-- 操作栏 -->
      <div class="table-actions">
        <a-space>
          <a-input-search
            v-model:value="keyword"
            placeholder="搜索姓名/手机号"
            style="width: 200px"
            @search="fetchLeads"
            allow-clear
          />
          <a-select v-model:value="channelId" placeholder="渠道" style="width: 150px" allow-clear @change="fetchLeads">
            <a-select-option v-for="c in channels" :key="c.id" :value="c.id">{{ c.name }}</a-select-option>
          </a-select>
        </a-space>
        <a-space>
          <a-button v-if="poolType === 'public'" type="primary" @click="handleBatchClaim" :disabled="!selectedRowKeys.length">
            批量领取 ({{ selectedRowKeys.length }})
          </a-button>
          <a-button v-if="poolType === 'mine'" @click="showImportModal">导入线索</a-button>
        </a-space>
      </div>
      
      <a-table
        :columns="columns"
        :data-source="leads"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        :row-selection="poolType === 'public' ? rowSelection : undefined"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag color="blue">线索</a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button v-if="poolType === 'public'" type="link" size="small" @click="handleClaim(record.id)">领取</a-button>
              <a-button v-if="poolType === 'mine'" type="link" size="small" @click="goToCandidate(record.id)">跟进</a-button>
              <a-button v-if="isAdmin && poolType === 'public'" type="link" size="small" @click="showAssignModal(record)">分配</a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 分配弹窗 -->
    <a-modal
      v-model:open="assignModalVisible"
      title="分配线索"
      @ok="handleAssign"
      :confirm-loading="assigning"
    >
      <a-form layout="vertical">
        <a-form-item label="选择招聘专员">
          <a-select v-model:value="assignOwnerId" placeholder="请选择" style="width: 100%">
            <a-select-option v-for="u in recruiters" :key="u.id" :value="u.id">
              {{ u.real_name || u.username }}
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 导入弹窗 -->
    <a-modal
      v-model:open="importModalVisible"
      title="导入线索"
      @ok="handleImport"
      :confirm-loading="importing"
      :width="700"
    >
      <a-alert message="请粘贴线索数据，每行一条，格式：姓名,手机号,微信,年龄,渠道ID,项目ID,岗位,备注" type="info" style="margin-bottom: 16px" />
      <a-textarea
        v-model:value="importText"
        :rows="10"
        placeholder="张三,13800138000,wx123,25,1,1,普工,备注&#10;李四,13900139000,wx456,30,,,操作工,"
      />
      <div v-if="importResult" style="margin-top: 16px">
        <a-alert v-if="importResult.success_count" :message="`成功导入 ${importResult.success_count} 条`" type="success" />
        <a-alert v-if="importResult.failed_count" :message="`失败 ${importResult.failed_count} 条`" type="error" style="margin-top: 8px">
          <template #description>
            <div v-for="item in importResult.failed_items" :key="item.row">
              第{{ item.row }}行: {{ item.name }} {{ item.phone }} - {{ item.reason }}
            </div>
          </template>
        </a-alert>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import { useRouter } from 'vue-router'
import request from '@/api/request'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const leads = ref<any[]>([])
const poolType = ref('public')
const keyword = ref('')
const channelId = ref<number | undefined>(undefined)
const channels = ref<any[]>([])
const recruiters = ref<any[]>([])
const publicCount = ref(0)
const mineCount = ref(0)

const modalVisible = ref(false)
const assignModalVisible = ref(false)
const importModalVisible = ref(false)
const assigning = ref(false)
const importing = ref(false)
const currentLead = ref<any>(null)
const assignOwnerId = ref<number | undefined>(undefined)
const importText = ref('')
const importResult = ref<any>(null)

const selectedRowKeys = ref<number[]>([])

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})

const isAdmin = computed(() => ['admin', 'manager'].includes(userStore.user?.role || ''))

const columns = [
  { title: '姓名', dataIndex: 'name', key: 'name', width: 100 },
  { title: '手机号', dataIndex: 'phone', key: 'phone', width: 120 },
  { title: '微信', dataIndex: 'wechat', key: 'wechat', width: 120 },
  { title: '年龄', dataIndex: 'age', key: 'age', width: 60 },
  { title: '状态', key: 'status', width: 80 },
  { title: '备注', dataIndex: 'note', key: 'note', width: 200 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 160 },
  { title: '操作', key: 'action', fixed: 'right', width: 120 }
]

const rowSelection = computed(() => ({
  selectedRowKeys: selectedRowKeys.value,
  onChange: (keys: number[]) => {
    selectedRowKeys.value = keys
  }
}))

async function fetchLeads() {
  loading.value = true
  try {
    const res = await request.get('/candidates/leads/pool', {
      params: {
        pool_type: poolType.value,
        page: pagination.current,
        page_size: pagination.pageSize,
        keyword: keyword.value || undefined,
        channel_id: channelId.value
      }
    })
    leads.value = res.items
    pagination.total = res.total
    
    // Update counts
    if (poolType.value === 'public') {
      publicCount.value = res.total
    } else {
      mineCount.value = res.total
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function fetchCounts() {
  try {
    const [publicRes, mineRes] = await Promise.all([
      request.get('/candidates/leads/pool', { params: { pool_type: 'public', page_size: 1 } }),
      request.get('/candidates/leads/pool', { params: { pool_type: 'mine', page_size: 1 } })
    ])
    publicCount.value = publicRes.total
    mineCount.value = mineRes.total
  } catch (e) {
    console.error(e)
  }
}

async function fetchChannels() {
  try {
    const res = await request.get('/channels', { params: { page_size: 100 } })
    channels.value = res.items
  } catch (e) {
    console.error(e)
  }
}

async function fetchRecruiters() {
  try {
    const res = await request.get('/users', { params: { page_size: 100 } })
    recruiters.value = res.filter((u: any) => ['admin', 'manager', 'recruiter'].includes(u.role))
  } catch (e) {
    console.error(e)
  }
}

function handleTableChange(pag: any) {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchLeads()
}

async function handleClaim(id: number) {
  try {
    await request.post(`/candidates/leads/${id}/claim`)
    message.success('领取成功')
    fetchLeads()
    fetchCounts()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '领取失败')
  }
}

async function handleBatchClaim() {
  try {
    const res = await request.post('/candidates/leads/batch-claim', selectedRowKeys.value)
    message.success(`成功领取 ${res.success_count} 条线索`)
    selectedRowKeys.value = []
    fetchLeads()
    fetchCounts()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '批量领取失败')
  }
}

function showAssignModal(record: any) {
  currentLead.value = record
  assignOwnerId.value = undefined
  assignModalVisible.value = true
}

async function handleAssign() {
  if (!assignOwnerId.value) {
    message.warning('请选择招聘专员')
    return
  }
  assigning.value = true
  try {
    await request.post(`/candidates/leads/${currentLead.value.id}/assign?owner_id=${assignOwnerId.value}`)
    message.success('分配成功')
    assignModalVisible.value = false
    fetchLeads()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '分配失败')
  } finally {
    assigning.value = false
  }
}

function showImportModal() {
  importText.value = ''
  importResult.value = null
  importModalVisible.value = true
}

async function handleImport() {
  if (!importText.value.trim()) {
    message.warning('请输入线索数据')
    return
  }
  
  importing.value = true
  try {
    const lines = importText.value.trim().split('\n')
    const leads = lines.map(line => {
      const parts = line.split(',')
      return {
        name: parts[0]?.trim() || '',
        phone: parts[1]?.trim() || '',
        wechat: parts[2]?.trim() || undefined,
        age: parts[3] ? parseInt(parts[3]) : undefined,
        channel_id: parts[4] ? parseInt(parts[4]) : undefined,
        project_id: parts[5] ? parseInt(parts[5]) : undefined,
        position_name: parts[6]?.trim() || undefined,
        note: parts[7]?.trim() || undefined
      }
    })
    
    const res = await request.post('/candidates/leads/import', leads)
    importResult.value = res
    
    if (res.success_count > 0) {
      fetchLeads()
      fetchCounts()
    }
  } catch (error: any) {
    message.error(error.response?.data?.detail || '导入失败')
  } finally {
    importing.value = false
  }
}

function goToCandidate(id: number) {
  router.push(`/candidates/${id}`)
}

onMounted(() => {
  fetchLeads()
  fetchCounts()
  fetchChannels()
  if (isAdmin.value) {
    fetchRecruiters()
  }
})
</script>

<style scoped>
.page-container { padding: 16px; }
.page-card { background: #fff; border-radius: 8px; padding: 16px; }
.page-title { margin: 0 0 16px 0; font-size: 18px; }
.table-actions { display: flex; justify-content: space-between; margin-bottom: 16px; }
</style>
