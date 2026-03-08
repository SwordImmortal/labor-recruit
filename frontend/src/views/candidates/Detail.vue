<template>
  <div class="page-container">
    <div class="page-card">
      <a-page-header
        title="候选人详情"
        @back="$router.back()"
      >
        <template #extra>
          <a-button type="primary" @click="showFollowModal">添加跟进</a-button>
        </template>
      </a-page-header>

      <a-spin :spinning="loading">
        <a-descriptions :column="{ xs: 1, sm: 2, md: 3 }" bordered>
          <a-descriptions-item label="姓名">{{ candidate.name }}</a-descriptions-item>
          <a-descriptions-item label="手机号">{{ maskPhone(candidate.phone) }}</a-descriptions-item>
          <a-descriptions-item label="微信号">{{ candidate.wechat || '-' }}</a-descriptions-item>
          <a-descriptions-item label="年龄">{{ candidate.age || '-' }}</a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="getStatusColor(candidate.status)">{{ getStatusText(candidate.status) }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="应聘项目">{{ candidate.project_name || '-' }}</a-descriptions-item>
          <a-descriptions-item label="渠道">{{ candidate.channel_name || '-' }}</a-descriptions-item>
          <a-descriptions-item label="面试时间">{{ candidate.interview_time || '-' }}</a-descriptions-item>
          <a-descriptions-item label="面试反馈">{{ candidate.interview_feedback || '-' }}</a-descriptions-item>
          <a-descriptions-item label="备注" :span="3">{{ candidate.note || '-' }}</a-descriptions-item>
        </a-descriptions>

        <!-- 跟进记录 -->
        <a-divider>跟进记录</a-divider>
        <a-timeline v-if="followRecords.length">
          <a-timeline-item v-for="record in followRecords" :key="record.id">
            <p><strong>{{ record.follow_at }}</strong> - {{ record.operator_name }}</p>
            <p v-if="record.status_from || record.status_to">
              状态变更: {{ getStatusText(record.status_from) }} → {{ getStatusText(record.status_to) }}
            </p>
            <p v-if="record.content">{{ record.content }}</p>
          </a-timeline-item>
        </a-timeline>
        <a-empty v-else description="暂无跟进记录" />
      </a-spin>
    </div>

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
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import request from '@/api/request'

const route = useRoute()
const router = useRouter()
const candidateId = route.params.id as string

const loading = ref(false)
const candidate = ref<any>({})
const followRecords = ref<any[]>([])

const followModalVisible = ref(false)
const followForm = reactive({
  status_to: undefined as string | undefined,
  content: ''
})

async function fetchCandidate() {
  loading.value = true
  try {
    const res = await request.get(`/candidates/${candidateId}`)
    candidate.value = res
  } catch (error) {
    message.error('获取候选人信息失败')
    router.back()
  } finally {
    loading.value = false
  }
}

function showFollowModal() {
  followForm.status_to = undefined
  followForm.content = ''
  followModalVisible.value = true
}

async function handleFollow() {
  try {
    await request.post(`/candidates/${candidateId}/follow`, null, {
      params: followForm
    })
    message.success('跟进成功')
    followModalVisible.value = false
    fetchCandidate()
  } catch (error) {
    console.error(error)
  }
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
  fetchCandidate()
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

@media (max-width: 768px) {
  .page-container {
    padding: 12px;
  }
}
</style>
