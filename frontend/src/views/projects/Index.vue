<template>
  <div class="page-container">
    <div class="page-card">
      <h2 class="page-title">项目管理</h2>
      <a-table :columns="columns" :data-source="projects" :loading="loading" row-key="id" :scroll="{ x: 800 }">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'recruit_status'">
            <a-tag :color="getStatusColor(record.recruit_status)">{{ record.recruit_status }}</a-tag>
          </template>
          <template v-if="column.key === 'progress'">
            <a-progress :percent="getProgress(record)" :size="'small'" />
          </template>
        </template>
      </a-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '@/api/request'

const projects = ref<any[]>([])
const loading = ref(false)

const columns = [
  { title: '项目名称', dataIndex: 'name', key: 'name' },
  { title: '城市', dataIndex: 'city', key: 'city' },
  { title: '目标人数', dataIndex: 'target_count', key: 'target_count' },
  { title: '当前人数', dataIndex: 'current_count', key: 'current_count' },
  { title: '进度', key: 'progress', width: 150 },
  { title: '招聘状态', dataIndex: 'recruit_status', key: 'recruit_status' },
  { title: '开始日期', dataIndex: 'start_date', key: 'start_date' }
]

async function fetchProjects() {
  loading.value = true
  try {
    const res = await request.get('/projects', { params: { limit: 50 } })
    projects.value = res
  } finally {
    loading.value = false
  }
}

function getProgress(record: any) {
  if (!record.target_count) return 0
  return Math.round((record.current_count / record.target_count) * 100)
}

function getStatusColor(status: string) {
  const map: Record<string, string> = {
    pending: 'default',
    recruiting: 'blue',
    filled: 'green',
    replacing: 'orange',
    stopped: 'red'
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
</style>
