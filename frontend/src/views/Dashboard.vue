<template>
  <div class="dashboard">
    <h2 class="page-title">工作台</h2>
    
    <!-- 快捷统计 -->
    <a-row :gutter="[16, 16]">
      <a-col :xs="12" :sm="6">
        <a-card :loading="loading">
          <a-statistic title="今日线索" :value="stats.todayLeads">
            <template #prefix>
              <UserAddOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="12" :sm="6">
        <a-card :loading="loading">
          <a-statistic title="待跟进" :value="stats.pendingFollow" :value-style="{ color: '#faad14' }">
            <template #prefix>
              <ClockCircleOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="12" :sm="6">
        <a-card :loading="loading">
          <a-statistic title="本月入职" :value="stats.monthOnboard" :value-style="{ color: '#52c41a' }">
            <template #prefix>
              <CheckCircleOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="12" :sm="6">
        <a-card :loading="loading">
          <a-statistic title="在职人数" :value="stats.currentOnline" :value-style="{ color: '#1890ff' }">
            <template #prefix>
              <TeamOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
    </a-row>

    <!-- 快捷操作 -->
    <a-card title="快捷操作" style="margin-top: 16px">
      <a-space wrap>
        <a-button type="primary" @click="$router.push('/candidates')">
          <template #icon><UserAddOutlined /></template>
          新增候选人
        </a-button>
        <a-button @click="$router.push('/onboardings')">
          <template #icon><SolutionOutlined /></template>
          入职登记
        </a-button>
        <a-button @click="$router.push('/projects')">
          <template #icon><ProjectOutlined /></template>
          查看项目
        </a-button>
      </a-space>
    </a-card>

    <!-- 最近候选人 -->
    <a-card title="最近候选人" style="margin-top: 16px" :loading="recentLoading">
      <a-table
        v-if="recentCandidates.length > 0"
        :columns="columns"
        :data-source="recentCandidates"
        :pagination="false"
        size="small"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <a @click="$router.push(`/candidates/${record.id}`)">{{ record.name }}</a>
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">{{ getStatusText(record.status) }}</a-tag>
          </template>
          <template v-if="column.key === 'created_at'">
            {{ formatTime(record.created_at) }}
          </template>
        </template>
      </a-table>
      <a-empty v-else description="暂无数据" />
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { UserAddOutlined, ClockCircleOutlined, CheckCircleOutlined, TeamOutlined, SolutionOutlined, ProjectOutlined } from '@ant-design/icons-vue'
import request from '@/api/request'

const loading = ref(true)
const recentLoading = ref(true)

const stats = reactive({
  todayLeads: 0,
  pendingFollow: 0,
  monthOnboard: 0,
  currentOnline: 0
})

const recentCandidates = ref<any[]>([])

const columns = [
  { title: '姓名', dataIndex: 'name', key: 'name', width: 100 },
  { title: '手机号', dataIndex: 'phone', key: 'phone', width: 120 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '录入时间', dataIndex: 'created_at', key: 'created_at', width: 150 }
]

async function fetchStats() {
  loading.value = true
  try {
    const res = await request.get('/dashboard/stats')
    Object.assign(stats, res)
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function fetchRecentCandidates() {
  recentLoading.value = true
  try {
    const res = await request.get('/dashboard/recent-candidates')
    recentCandidates.value = res
  } catch (error) {
    console.error(error)
  } finally {
    recentLoading.value = false
  }
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

function formatTime(time: string) {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchStats()
  fetchRecentCandidates()
})
</script>

<style scoped>
.dashboard {
  padding: 16px;
}

@media (max-width: 768px) {
  .dashboard {
    padding: 12px;
  }
}
</style>
