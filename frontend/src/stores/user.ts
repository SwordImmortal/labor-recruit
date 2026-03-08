import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import router from '@/router'
import { login, getUserInfo } from '@/api/auth'

export interface UserInfo {
  id: number
  username: string
  phone: string
  email?: string
  real_name?: string
  role: string
  is_active: boolean
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const userInfo = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  const isSupervisor = computed(() => userInfo.value?.role === 'supervisor')

  async function loginAction(username: string, password: string) {
    try {
      const res = await login(username, password)
      token.value = res.access_token
      localStorage.setItem('token', res.access_token)
      
      // 获取用户信息
      await fetchUserInfo()
      
      message.success('登录成功')
      router.push('/')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败')
      throw error
    }
  }

  async function fetchUserInfo() {
    try {
      const res = await getUserInfo()
      userInfo.value = res
    } catch (error) {
      console.error('获取用户信息失败', error)
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    isAdmin,
    isSupervisor,
    loginAction,
    fetchUserInfo,
    logout
  }
})
