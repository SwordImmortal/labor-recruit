<template>
  <div class="dashboard">
    <h2 class="page-title">工作台</h2>
    
    <!-- 快捷统计 -->
    <a-row :gutter="[16, 16]">
      <a-col :xs="12" :sm="6">
        <a-card>
          <a-statistic title="今日线索" :value="stats.todayLeads" />
        </a-card>
      </a-col>
      <a-col :xs="12" :sm="6">
        <a-card>
          <a-statistic title="待跟进" :value="stats.pendingFollow" />
        </a-card>
      </a-col>
      <a-col :xs="12" :sm="6">
        <a-card>
          <a-statistic title="本月入职" :value="stats.monthOnboard" />
        </a-card>
      </a-col>
      <a-col :xs="12" :sm="6">
        <a-card>
          <a-statistic title="在职人数" :value="stats.currentOnline" />
        </a-card>
      </a-col>
    </a-row>

    <!-- 快捷操作 -->
    <a-card title="快捷操作" style="margin-top: 16px">
      <a-space wrap>
        <a-button type="primary" @click="$router.push('/candidates')">
          新增候选人
        </a-button>
        <a-button @click="$router.push('/onboardings')">
          入职登记
        </a-button>
        <a-button @click="$router.push('/projects')">
          查看项目
        </a-button>
      </a-space>
    </a-card>

    <!-- 最近候选人 -->
    <a-card title="最近候选人" style="margin-top: 16px">
      <a-empty description="暂无数据" />
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const stats = reactive({
  todayLeads: 0,
  pendingFollow: 0,
  monthOnboard: 0,
  currentOnline: 0
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
