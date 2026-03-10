<template>
  <div class="page-container">
    <div class="page-card">
      <h2 class="page-title">客户管理</h2>
      
      <!-- 搜索和操作 -->
      <div class="table-actions">
        <a-space>
          <a-input-search
            v-model:value="keyword"
            placeholder="搜索客户名称/联系人/电话"
            style="width: 250px"
            @search="fetchCustomers"
            allow-clear
          />
          <a-select v-model:value="isActiveFilter" placeholder="状态" style="width: 120px" allow-clear @change="fetchCustomers">
            <a-select-option :value="true">启用</a-select-option>
            <a-select-option :value="false">禁用</a-select-option>
          </a-select>
        </a-space>
        <a-button type="primary" @click="showAddModal">新增客户</a-button>
      </div>
      
      <a-table
        :columns="columns"
        :data-source="customers"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'is_active'">
            <a-tag :color="record.is_active ? 'green' : 'default'">
              {{ record.is_active ? '启用' : '禁用' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'stats'">
            <a-space>
              <span>{{ record.project_count || 0 }} 项目</span>
              <span>{{ record.onboarded_count || 0 }} 入职</span>
            </a-space>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="showEditModal(record)">编辑</a-button>
              <a-popconfirm
                title="确定删除该客户吗？"
                @confirm="handleDelete(record.id)"
                v-if="!record.project_count"
              >
                <a-button type="link" size="small" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 新增/编辑弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑客户' : '新增客户'"
      @ok="handleSubmit"
      :confirm-loading="submitting"
    >
      <a-form :model="form" :rules="rules" ref="formRef" layout="vertical">
        <a-form-item label="客户名称" name="name">
          <a-input v-model:value="form.name" placeholder="请输入客户名称" />
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="联系人">
              <a-input v-model:value="form.contact" placeholder="请输入联系人" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="联系电话">
              <a-input v-model:value="form.phone" placeholder="请输入联系电话" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="地址">
          <a-input v-model:value="form.address" placeholder="请输入地址" />
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea v-model:value="form.remark" :rows="3" placeholder="请输入备注" />
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
const customers = ref<any[]>([])
const keyword = ref('')
const isActiveFilter = ref<boolean | undefined>(undefined)
const modalVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const currentId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const columns = [
  { title: '客户名称', dataIndex: 'name', key: 'name', width: 150 },
  { title: '联系人', dataIndex: 'contact', key: 'contact', width: 100 },
  { title: '联系电话', dataIndex: 'phone', key: 'phone', width: 120 },
  { title: '地址', dataIndex: 'address', key: 'address', width: 200 },
  { title: '统计', key: 'stats', width: 150 },
  { title: '状态', dataIndex: 'is_active', key: 'is_active', width: 80 },
  { title: '操作', key: 'action', fixed: 'right', width: 120 }
]

const form = reactive({
  name: '',
  contact: '',
  phone: '',
  address: '',
  remark: ''
})

const rules = {
  name: [{ required: true, message: '请输入客户名称' }]
}

function resetForm() {
  Object.assign(form, {
    name: '',
    contact: '',
    phone: '',
    address: '',
    remark: ''
  })
}

async function fetchCustomers() {
  loading.value = true
  try {
    const res = await request.get('/customers', {
      params: {
        page: pagination.current,
        page_size: pagination.pageSize,
        keyword: keyword.value || undefined,
        is_active: isActiveFilter.value
      }
    })
    customers.value = res.items
    
    // Fetch stats for each customer
    for (const customer of customers.value) {
      try {
        const stats = await request.get(`/customers/${customer.id}/stats`)
        customer.project_count = stats.project_count
        customer.onboarded_count = stats.onboarded_count
      } catch (e) {
        console.error(e)
      }
    }
    
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
  fetchCustomers()
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
    contact: record.contact || '',
    phone: record.phone || '',
    address: record.address || '',
    remark: record.remark || ''
  })
  modalVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    submitting.value = true
    
    if (isEdit.value && currentId.value) {
      await request.put(`/customers/${currentId.value}`, form)
      message.success('更新成功')
    } else {
      await request.post('/customers', form)
      message.success('创建成功')
    }
    
    modalVisible.value = false
    fetchCustomers()
  } catch (error: any) {
    if (error.response?.data?.detail) {
      message.error(error.response.data.detail)
    }
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await request.delete(`/customers/${id}`)
    message.success('删除成功')
    fetchCustomers()
  } catch (error: any) {
    if (error.response?.data?.detail) {
      message.error(error.response.data.detail)
    }
  }
}

onMounted(() => {
  fetchCustomers()
})
</script>

<style scoped>
.page-container { padding: 16px; }
.page-card { background: #fff; border-radius: 8px; padding: 16px; }
.page-title { margin: 0 0 16px 0; font-size: 18px; }
.table-actions { display: flex; justify-content: space-between; margin-bottom: 16px; }
</style>
