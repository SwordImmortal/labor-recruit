<template>
  <div class="page-container">
    <div class="page-card">
      <h2 class="page-title">人才库</h2>
      
      <!-- 搜索栏 -->
      <div class="table-actions">
        <a-input-search
          v-model:value="keyword"
          placeholder="搜索姓名/手机号"
          style="width: 250px"
          @search="fetchTalents"
          allow-clear
        />
      </div>
      
      <a-table
        :columns="columns"
        :data-source="talents"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag color="purple">人才库</a-tag>
          </template>
          <template v-if="column.key === 'tags'">
            <a-tag v-for="tag in (record.tags || [])" :key="tag" color="blue">{{ tag }}</a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleActivate(record.id)">激活</a-button>
              <a-button type="link" size="small" @click="showTagsModal(record)">标签</a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 标签弹窗 -->
    <a-modal
      v-model:open="tagsModalVisible"
      title="管理标签"
      @ok="handleUpdateTags"
      :confirm-loading="updatingTags"
    >
      <div style="margin-bottom: 16px">
        <a-input
          v-model:value="newTag"
          placeholder="输入新标签"
          @pressEnter="addTag"
          style="width: 200px; margin-right: 8px"
        />
        <a-button @click="addTag">添加</a-button>
      </div>
      <div>
        <a-tag
          v-for="tag in currentTags"
          :key="tag"
          closable
          @close="removeTag(tag)"
          color="blue"
          style="margin-bottom: 8px"
        >
          {{ tag }}
        </a-tag>
      </div>
      <a-divider />
      <div>
        <span style="color: #999">常用标签：</span>
        <a-tag v-for="tag in commonTags" :key="tag" @click="selectCommonTag(tag)" style="cursor: pointer">
          {{ tag }}
        </a-tag>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import request from '@/api/request'

const loading = ref(false)
const talents = ref<any[]>([])
const keyword = ref('')

const tagsModalVisible = ref(false)
const updatingTags = ref(false)
const currentTalent = ref<any>(null)
const currentTags = ref<string[]>([])
const newTag = ref('')

const commonTags = ['熟练工', '新手', '推荐', '优先', '备选', '特殊技能']

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})

const columns = [
  { title: '姓名', dataIndex: 'name', key: 'name', width: 100 },
  { title: '手机号', dataIndex: 'phone', key: 'phone', width: 120 },
  { title: '微信', dataIndex: 'wechat', key: 'wechat', width: 120 },
  { title: '年龄', dataIndex: 'age', key: 'age', width: 60 },
  { title: '状态', key: 'status', width: 80 },
  { title: '标签', key: 'tags', width: 200 },
  { title: '备注', dataIndex: 'note', key: 'note', width: 200 },
  { title: '更新时间', dataIndex: 'updated_at', key: 'updated_at', width: 160 },
  { title: '操作', key: 'action', fixed: 'right', width: 120 }
]

async function fetchTalents() {
  loading.value = true
  try {
    const res = await request.get('/candidates/talents/pool', {
      params: {
        page: pagination.current,
        page_size: pagination.pageSize,
        keyword: keyword.value || undefined
      }
    })
    talents.value = res.items
    pagination.total = res.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

function handleTableChange(pag: any) {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchTalents()
}

async function handleActivate(id: number) {
  try {
    await request.post(`/candidates/talents/${id}/activate`)
    message.success('已激活为线索')
    fetchTalents()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '激活失败')
  }
}

function showTagsModal(record: any) {
  currentTalent.value = record
  currentTags.value = [...(record.tags || [])]
  tagsModalVisible.value = true
}

function addTag() {
  if (newTag.value.trim() && !currentTags.value.includes(newTag.value.trim())) {
    currentTags.value.push(newTag.value.trim())
    newTag.value = ''
  }
}

function removeTag(tag: string) {
  currentTags.value = currentTags.value.filter(t => t !== tag)
}

function selectCommonTag(tag: string) {
  if (!currentTags.value.includes(tag)) {
    currentTags.value.push(tag)
  }
}

async function handleUpdateTags() {
  updatingTags.value = true
  try {
    await request.post(`/candidates/talents/${currentTalent.value.id}/tags`, currentTags.value)
    message.success('标签更新成功')
    tagsModalVisible.value = false
    fetchTalents()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '更新失败')
  } finally {
    updatingTags.value = false
  }
}

onMounted(() => {
  fetchTalents()
})
</script>

<style scoped>
.page-container { padding: 16px; }
.page-card { background: #fff; border-radius: 8px; padding: 16px; }
.page-title { margin: 0 0 16px 0; font-size: 18px; }
.table-actions { display: flex; justify-content: space-between; margin-bottom: 16px; }
</style>
