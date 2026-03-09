<template>
  <div class="page-container">
    <div class="page-card">
      <a-page-header
        title="候选人详情"
        @back="$router.back()"
      >
        <template #extra>
          <a-space>
            <a-button @click="showEditModal">编辑</a-button>
            <a-button type="primary" @click="showFollowModal">添加跟进</a-button>
          </a-space>
        </template>
      </a-page-header>

      <a-spin :spinning="loading">
        <!-- 基本信息 -->
        <a-descriptions title="基本信息" :column="{ xs: 1, sm: 2, md: 3 }" bordered>
          <a-descriptions-item label="姓名">{{ candidate.name }}</a-descriptions-item>
          <a-descriptions-item label="手机号">
            <span class="phone-mask">{{ maskPhone(candidate.phone) }}</span>
            <a-button type="link" size="small" @click="showPhone = !showPhone">
              {{ showPhone ? '隐藏' : '查看' }}
            </a-button>
          </a-descriptions-item>
          <a-descriptions-item label="微信号">{{ candidate.wechat || '-' }}</a-descriptions-item>
          <a-descriptions-item label="年龄">{{ candidate.age || '-' }}</a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="getStatusColor(candidate.status)">{{ getStatusText(candidate.status) }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="应聘项目">{{ candidate.project?.name || '-' }}</a-descriptions-item>
          <a-descriptions-item label="渠道">{{ candidate.channel?.name || '-' }}</a-descriptions-item>
          <a-descriptions-item label="跟进人">{{ candidate.owner?.real_name || candidate.owner?.username || '-' }}</a-descriptions-item>
          <a-descriptions-item label="录入时间">{{ formatTime(candidate.created_at) }}</a-descriptions-item>
        </a-descriptions>

        <!-- 面试信息 -->
        <a-descriptions title="面试信息" :column="{ xs: 1, sm: 2 }" bordered style="margin-top: 16px">
          <a-descriptions-item label="面试时间">{{ candidate.interview_time || '-' }}</a-descriptions-item>
          <a-descriptions-item label="面试反馈">{{ candidate.interview_feedback || '-' }}</a-descriptions-item>
          <a-descriptions-item label="备注" :span="2">{{ candidate.note || '-' }}</a-descriptions-item>
        </a-descriptions>

        <!-- 跟进记录时间线 -->
        <a-divider>跟进记录</a-divider>
        <a-spin :spinning="followLoading">
          <div v-if="followRecords.length" class="follow-timeline">
            <a-timeline mode="left">
              <a-timeline-item 
                v-for="record in followRecords" 
                :key="record.id"
                :color="getTimelineColor(record.status_to)"
              >
                <template #dot v-if="record.status_to">
                  <check-circle-filled v-if="record.status_to === 'onboarded'" style="font-size: 16px" />
                  <clock-circle-filled v-else-if="record.status_to === 'interview'" style="font-size: 16px" />
                  <minus-circle-filled v-else-if="record.status_to === 'lost'" style="font-size: 16px; color: #ff4d4f" />
                </template>
                <div class="follow-item">
                  <div class="follow-header">
                    <span class="follow-time">{{ record.follow_at }}</span>
                    <span class="follow-operator">{{ record.operator_name }}</span>
                  </div>
                  <div v-if="record.status_from || record.status_to" class="follow-status">
                    <a-tag v-if="record.status_from" :color="getStatusColor(record.status_from)">
                      {{ getStatusText(record.status_from) }}
                    </a-tag>
                    <arrow-right-outlined />
                    <a-tag v-if="record.status_to" :color="getStatusColor(record.status_to)">
                      {{ getStatusText(record.status_to) }}
                    </a-tag>
                  </div>
                  <div v-if="record.content" class="follow-content">{{ record.content }}</div>
                </div>
              </a-timeline-item>
            </a-timeline>
          </div>
          <a-empty v-else description="暂无跟进记录" />
        </a-spin>
      </a-spin>
    </div>

    <!-- 跟进弹窗 -->
    <a-modal
      v-model:open="followModalVisible"
      title="添加跟进"
      @ok="handleFollow"
      :confirm-loading="followSubmitting"
    >
      <a-form :model="followForm" layout="vertical">
        <a-form-item label="变更状态">
          <a-select v-model:value="followForm.status_to" placeholder="请选择（可选）">
            <a-select-option value="wechat">已加微信</a-select-option>
            <a-select-option value="interview">已约面</a-select-option>
            <a-select-option value="interviewed">已到面</a-select-option>
            <a-select-option value="onboarded">已入职</a-select-option>
            <a-select-option value="lost">流失</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="跟进内容" required>
          <a-textarea v-model:value="followForm.content" :rows="3" placeholder="请输入跟进内容" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 编辑弹窗 -->
    <a-modal
      v-model:open="editModalVisible"
      title="编辑候选人"
      @ok="handleEdit"
      :confirm-loading="editSubmitting"
      :width="600"
    >
      <a-form :model="editForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="姓名" required>
              <a-input v-model:value="editForm.name" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="手机号" required>
              <a-input v-model:value="editForm.phone" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="微信号">
              <a-input v-model:value="editForm.wechat" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="年龄">
              <a-input-number v-model:value="editForm.age" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="应聘项目">
              <a-select v-model:value="editForm.project_id" placeholder="请选择" style="width: 100%">
                <a-select-option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="渠道">
              <a-select v-model:value="editForm.channel_id" placeholder="请选择" style="width: 100%">
                <a-select-option v-for="c in channels" :key="c.id" :value="c.id">{{ c.name }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="备注">
          <a-textarea v-model:value="editForm.note" :rows="2" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { CheckCircleFilled, ClockCircleFilled, MinusCircleFilled, ArrowRightOutlined } from '@ant-design/icons-vue'
import request from '@/api/request'

const route = useRoute()
const router = useRouter()
const candidateId = route.params.id as string

const loading = ref(false)
const followLoading = ref(false)
const candidate = ref<any>({})
const followRecords = ref<any[]>([])
const projects = ref<any[]>([])
const channels = ref<any[]>([])
const showPhone = ref(false)

const followModalVisible = ref(false)
const followSubmitting = ref(false)
const followForm = reactive({
  status_to: undefined as string | undefined,
  content: ''
})

const editModalVisible = ref(false)
const editSubmitting = ref(false)
const editForm = reactive({
  name: '',
  phone: '',
  wechat: '',
  age: undefined as number | undefined,
  project_id: undefined as number | undefined,
  channel_id: undefined as number | undefined,
  note: ''
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

async function fetchFollowRecords() {
  followLoading.value = true
  try {
    const res = await request.get(`/candidates/${candidateId}/follows`)
    followRecords.value = res
  } catch (error) {
    console.error(error)
  } finally {
    followLoading.value = false
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

function showFollowModal() {
  followForm.status_to = undefined
  followForm.content = ''
  followModalVisible.value = true
}

async function handleFollow() {
  if (!followForm.content) {
    message.warning('请输入跟进内容')
    return
  }
  
  followSubmitting.value = true
  try {
    await request.post(`/candidates/${candidateId}/follow`, null, { params: followForm })
    message.success('跟进成功')
    followModalVisible.value = false
    fetchCandidate()
    fetchFollowRecords()
  } catch (error) {
    console.error(error)
  } finally {
    followSubmitting.value = false
  }
}

function showEditModal() {
  Object.assign(editForm, {
    name: candidate.value.name,
    phone: candidate.value.phone,
    wechat: candidate.value.wechat,
    age: candidate.value.age,
    project_id: candidate.value.project_id,
    channel_id: candidate.value.channel_id,
    note: candidate.value.note
  })
  editModalVisible.value = true
}

async function handleEdit() {
  if (!editForm.name || !editForm.phone) {
    message.warning('请填写必填项')
    return
  }
  
  editSubmitting.value = true
  try {
    await request.put(`/candidates/${candidateId}`, editForm)
    message.success('更新成功')
    editModalVisible.value = false
    fetchCandidate()
  } catch (error) {
    console.error(error)
  } finally {
    editSubmitting.value = false
  }
}

function maskPhone(phone: string) {
  if (!phone) return ''
  if (showPhone.value) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

function formatTime(time: string) {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
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
  return map[status] || status || '-'
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

function getTimelineColor(status: string) {
  const map: Record<string, string> = {
    wechat: 'blue',
    interview: 'orange',
    interviewed: 'green',
    onboarded: 'green',
    lost: 'red'
  }
  return map[status] || 'gray'
}

onMounted(() => {
  fetchCandidate()
  fetchFollowRecords()
  fetchProjects()
  fetchChannels()
})
</script>

<style scoped>
.page-container { padding: 16px; }
.page-card { background: #fff; border-radius: 8px; padding: 16px; }
.phone-mask { font-family: monospace; }

.follow-timeline { padding: 16px 0; }
.follow-item { padding-bottom: 8px; }
.follow-header { margin-bottom: 8px; }
.follow-time { color: #666; margin-right: 16px; }
.follow-operator { color: #1890ff; }
.follow-status { margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
.follow-content { color: #333; background: #f5f5f5; padding: 8px 12px; border-radius: 4px; }

@media (max-width: 768px) {
  .page-container { padding: 12px; }
}
</style>
