<template>
  <a-layout class="layout">
    <!-- 移动端侧边栏折叠 -->
    <a-drawer
      v-model:open="collapsed"
      placement="left"
      :closable="false"
      width="200"
      class="mobile-drawer"
    >
      <div class="logo">招聘系统</div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        mode="inline"
        :items="menuItems"
        @click="handleMenuClick"
      />
    </a-drawer>

    <!-- PC端侧边栏 -->
    <a-layout-sider
      v-model:collapsed="siderCollapsed"
      :trigger="null"
      collapsible
      breakpoint="lg"
      @collapse="onCollapse"
      class="sider"
    >
      <div class="logo">{{ siderCollapsed ? '招聘' : '招聘系统' }}</div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        mode="inline"
        :items="menuItems"
        @click="handleMenuClick"
      />
    </a-layout-sider>

    <a-layout>
      <a-layout-header class="header">
        <div class="header-left">
          <MenuFoldOutlined
            v-if="!siderCollapsed"
            class="trigger"
            @click="siderCollapsed = true"
          />
          <MenuUnfoldOutlined
            v-else
            class="trigger"
            @click="siderCollapsed = false"
          />
          <span class="page-breadcrumb">{{ currentTitle }}</span>
        </div>
        <div class="header-right">
          <a-dropdown>
            <a-space class="user-info">
              <a-avatar>{{ userStore.userInfo?.real_name?.[0] || userStore.userInfo?.username?.[0] }}</a-avatar>
              <span class="user-name">{{ userStore.userInfo?.real_name || userStore.userInfo?.username }}</span>
            </a-space>
            <template #overlay>
              <a-menu>
                <a-menu-item @click="userStore.logout">
                  <LogoutOutlined /> 退出登录
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>
      
      <a-layout-content class="content">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  LogoutOutlined,
  HomeOutlined,
  UserOutlined,
  ProjectOutlined,
  SolutionOutlined,
  ApiOutlined,
  TeamOutlined,
  BookOutlined
} from '@ant-design/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const collapsed = ref(false)
const siderCollapsed = ref(false)
const selectedKeys = ref<string[]>([route.path])

// 获取当前路由信息
const currentTitle = computed(() => {
  return route.meta?.title || '工作台'
})

// 菜单项
const menuItems = computed(() => {
  const items = [
    { key: '/dashboard', icon: () => h(HomeOutlined), label: '工作台' },
    { key: '/candidates', icon: () => h(UserOutlined), label: '候选人管理' },
    { key: '/projects', icon: () => h(ProjectOutlined), label: '项目管理' },
    { key: '/onboardings', icon: () => h(SolutionOutlined), label: '入职管理' },
    { key: '/channels', icon: () => h(ApiOutlined), label: '渠道管理' },
  ]
  
  // 管理员/主管可见
  if (userStore.isAdmin || userStore.isSupervisor) {
    items.push({ key: '/users', icon: () => h(TeamOutlined), label: '用户管理' })
  }
  
  // 管理员可见
  if (userStore.isAdmin) {
    items.push({ key: '/dicts', icon: () => h(BookOutlined), label: '字典管理' })
  }
  
  return items
})

function handleMenuClick({ key }: { key: string }) {
  router.push(key)
  collapsed.value = false
}

function onCollapse(collapsed: boolean) {
  siderCollapsed.value = collapsed
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
}

.sider {
  background: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
}

.logo {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
  color: #1890ff;
  border-bottom: 1px solid #f0f0f0;
}

.header {
  background: #fff;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.trigger {
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s;
}

.trigger:hover {
  color: #1890ff;
}

.page-breadcrumb {
  font-size: 16px;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  cursor: pointer;
}

.user-name {
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.content {
  margin: 16px;
  background: #f5f5f5;
  border-radius: 8px;
  overflow: auto;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .sider {
    display: none;
  }
  
  .user-name {
    display: none;
  }
  
  .content {
    margin: 12px;
  }
}
</style>
