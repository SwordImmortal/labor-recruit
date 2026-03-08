import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '工作台', icon: 'HomeOutlined' }
      },
      {
        path: 'candidates',
        name: 'Candidates',
        component: () => import('@/views/candidates/Index.vue'),
        meta: { title: '候选人管理', icon: 'UserOutlined' }
      },
      {
        path: 'candidates/:id',
        name: 'CandidateDetail',
        component: () => import('@/views/candidates/Detail.vue'),
        meta: { title: '候选人详情', hidden: true }
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/views/projects/Index.vue'),
        meta: { title: '项目管理', icon: 'ProjectOutlined' }
      },
      {
        path: 'onboardings',
        name: 'Onboardings',
        component: () => import('@/views/onboardings/Index.vue'),
        meta: { title: '入职管理', icon: 'SolutionOutlined' }
      },
      {
        path: 'channels',
        name: 'Channels',
        component: () => import('@/views/channels/Index.vue'),
        meta: { title: '渠道管理', icon: 'ApiOutlined' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/users/Index.vue'),
        meta: { title: '用户管理', icon: 'TeamOutlined' }
      },
      {
        path: 'dicts',
        name: 'Dicts',
        component: () => import('@/views/dicts/Index.vue'),
        meta: { title: '字典管理', icon: 'BookOutlined' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth !== false && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
