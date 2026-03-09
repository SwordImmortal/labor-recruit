<template>
  <div class="page-container">
    <div class="page-card">
      <h2 class="page-title">字典管理</h2>
      
      <a-tabs v-model:activeKey="activeTab">
        <a-tab-pane key="types" tab="字典类型">
          <div class="table-actions">
            <a-button type="primary" @click="showTypeAddModal">新增类型</a-button>
          </div>
          <a-table
            :columns="typeColumns"
            :data-source="dictTypes"
            :loading="typeLoading"
            :pagination="false"
            row-key="id"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'is_active'">
                <a-tag :color="record.is_active ? 'green' : 'default'">
                  {{ record.is_active ? '启用' : '停用' }}
                </a-tag>
              </template>
              <template v-if="column.key === 'action'">
                <a-space>
                  <a-button type="link" size="small" @click="showItemsModal(record)">管理项</a-button>
                  <a-button type="link" size="small" @click="showTypeEditModal(record)">编辑</a-button>
                </a-space>
              </template>
            </template>
          </a-table>
        </a-tab-pane>
        
        <a-tab-pane key="items" tab="字典项">
          <div class="table-actions">
            <a-space>
              <a-select v-model:value="selectedTypeId" placeholder="选择字典类型" style="width: 200px" allowClear>
                <a-select-option v-for="t in dictTypes" :key="t.id" :value="t.id">{{ t.name }}</a-select-option>
              </a-select>
              <a-button type="primary" @click="showItemAddModal" :disabled="!selectedTypeId">新增字典项</a-button>
            </a-space>
          </div>
          <a-table
            :columns="itemColumns"
            :data-source="filteredItems"
            :loading="itemLoading"
            :pagination="false"
            row-key="id"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'is_active'">
                <a-tag :color="record.is_active ? 'green' : 'default'">
                  {{ record.is_active ? '启用' : '停用' }}
                </a-tag>
              </template>
              <template v-if="column.key === 'is_default'">
                <a-tag v-if="record.is_default" color="blue">默认</a-tag>
                <span v-else>-</span>
              </template>
              <template v-if="column.key === 'action'">
                <a-button type="link" size="small" @click="showItemEditModal(record)">编辑</a-button>
              </template>
            </template>
          </a-table>
        </a-tab-pane>
      </a-tabs>
    </div>

    <!-- 字典类型弹窗 -->
    <a-modal
      v-model:open="typeModalVisible"
      :title="isTypeEdit ? '编辑字典类型' : '新增字典类型'"
      @ok="handleTypeSubmit"
      :confirm-loading="typeSubmitting"
    >
      <a-form :model="typeForm" :rules="typeRules" ref="typeFormRef" layout="vertical">
        <a-form-item label="类型编码" name="code">
          <a-input v-model:value="typeForm.code" placeholder="如: city" :disabled="isTypeEdit" />
        </a-form-item>
        <a-form-item label="类型名称" name="name">
          <a-input v-model:value="typeForm.name" placeholder="如: 城市" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="typeForm.description" :rows="2" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 字典项弹窗 -->
    <a-modal
      v-model:open="itemModalVisible"
      :title="isItemEdit ? '编辑字典项' : '新增字典项'"
      @ok="handleItemSubmit"
      :confirm-loading="itemSubmitting"
    >
      <a-form :model="itemForm" :rules="itemRules" ref="itemFormRef" layout="vertical">
        <a-form-item label="字典项编码" name="code">
          <a-input v-model:value="itemForm.code" placeholder="如: beijing" />
        </a-form-item>
        <a-form-item label="字典项名称" name="name">
          <a-input v-model:value="itemForm.name" placeholder="如: 北京" />
        </a-form-item>
        <a-form-item label="排序">
          <a-input-number v-model:value="itemForm.sort_order" :min="0" style="width: 100%" />
        </a-form-item>
        <a-form-item label="是否默认">
          <a-switch v-model:checked="itemForm.is_default" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import type { FormInstance } from 'ant-design-vue'
import request from '@/api/request'

const activeTab = ref('types')
const typeLoading = ref(false)
const itemLoading = ref(false)
const dictTypes = ref<any[]>([])
const dictItems = ref<any[]>([])
const selectedTypeId = ref<number | undefined>(undefined)

// 类型弹窗
const typeModalVisible = ref(false)
const isTypeEdit = ref(false)
const typeSubmitting = ref(false)
const currentTypeId = ref<number | null>(null)
const typeFormRef = ref<FormInstance>()

// 字典项弹窗
const itemModalVisible = ref(false)
const isItemEdit = ref(false)
const itemSubmitting = ref(false)
const currentItemId = ref<number | null>(null)
const itemFormRef = ref<FormInstance>()

const typeColumns = [
  { title: '类型编码', dataIndex: 'code', key: 'code', width: 150 },
  { title: '类型名称', dataIndex: 'name', key: 'name', width: 150 },
  { title: '描述', dataIndex: 'description', key: 'description' },
  { title: '状态', dataIndex: 'is_active', key: 'is_active', width: 80 },
  { title: '操作', key: 'action', width: 140 }
]

const itemColumns = [
  { title: '编码', dataIndex: 'code', key: 'code', width: 120 },
  { title: '名称', dataIndex: 'name', key: 'name', width: 150 },
  { title: '排序', dataIndex: 'sort_order', key: 'sort_order', width: 80 },
  { title: '默认', dataIndex: 'is_default', key: 'is_default', width: 80 },
  { title: '状态', dataIndex: 'is_active', key: 'is_active', width: 80 },
  { title: '操作', key: 'action', width: 80 }
]

const typeForm = reactive({
  code: '',
  name: '',
  description: ''
})

const typeRules = {
  code: [{ required: true, message: '请输入类型编码' }],
  name: [{ required: true, message: '请输入类型名称' }]
}

const itemForm = reactive({
  code: '',
  name: '',
  sort_order: 0,
  is_default: false
})

const itemRules = {
  code: [{ required: true, message: '请输入字典项编码' }],
  name: [{ required: true, message: '请输入字典项名称' }]
}

const filteredItems = computed(() => {
  if (!selectedTypeId.value) return dictItems.value
  return dictItems.value.filter(item => item.type_id === selectedTypeId.value)
})

async function fetchDictTypes() {
  typeLoading.value = true
  try {
    const res = await request.get('/dicts/types')
    dictTypes.value = res
  } catch (error) {
    console.error(error)
  } finally {
    typeLoading.value = false
  }
}

async function fetchDictItems() {
  itemLoading.value = true
  try {
    const res = await request.get('/dicts/items')
    dictItems.value = res
  } catch (error) {
    console.error(error)
  } finally {
    itemLoading.value = false
  }
}

// 字典类型操作
function showTypeAddModal() {
  isTypeEdit.value = false
  currentTypeId.value = null
  Object.assign(typeForm, { code: '', name: '', description: '' })
  typeModalVisible.value = true
}

function showTypeEditModal(record: any) {
  isTypeEdit.value = true
  currentTypeId.value = record.id
  Object.assign(typeForm, {
    code: record.code,
    name: record.name,
    description: record.description
  })
  typeModalVisible.value = true
}

async function handleTypeSubmit() {
  try {
    await typeFormRef.value?.validate()
    typeSubmitting.value = true
    
    if (isTypeEdit.value && currentTypeId.value) {
      await request.put(`/dicts/types/${currentTypeId.value}`, typeForm)
      message.success('更新成功')
    } else {
      await request.post('/dicts/types', typeForm)
      message.success('创建成功')
    }
    
    typeModalVisible.value = false
    fetchDictTypes()
  } catch (error) {
    console.error(error)
  } finally {
    typeSubmitting.value = false
  }
}

// 字典项操作
function showItemsModal(record: any) {
  activeTab.value = 'items'
  selectedTypeId.value = record.id
}

function showItemAddModal() {
  isItemEdit.value = false
  currentItemId.value = null
  Object.assign(itemForm, { code: '', name: '', sort_order: 0, is_default: false })
  itemModalVisible.value = true
}

function showItemEditModal(record: any) {
  isItemEdit.value = true
  currentItemId.value = record.id
  selectedTypeId.value = record.type_id
  Object.assign(itemForm, {
    code: record.code,
    name: record.name,
    sort_order: record.sort_order,
    is_default: record.is_default
  })
  itemModalVisible.value = true
}

async function handleItemSubmit() {
  try {
    await itemFormRef.value?.validate()
    itemSubmitting.value = true
    
    const data = {
      ...itemForm,
      type_id: selectedTypeId.value
    }
    
    if (isItemEdit.value && currentItemId.value) {
      await request.put(`/dicts/items/${currentItemId.value}`, data)
      message.success('更新成功')
    } else {
      await request.post('/dicts/items', data)
      message.success('创建成功')
    }
    
    itemModalVisible.value = false
    fetchDictItems()
  } catch (error) {
    console.error(error)
  } finally {
    itemSubmitting.value = false
  }
}

onMounted(() => {
  fetchDictTypes()
  fetchDictItems()
})
</script>

<style scoped>
.page-container { padding: 16px; }
.page-card { background: #fff; border-radius: 8px; padding: 16px; }
.table-actions { margin-bottom: 16px; }
</style>
