import request from './request'

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface UserInfo {
  id: number
  username: string
  phone: string
  email?: string
  real_name?: string
  role: string
  is_active: boolean
}

// 登录
export function login(username: string, password: string): Promise<LoginResponse> {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)
  return request.post('/auth/login', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 获取当前用户信息
export function getUserInfo(): Promise<UserInfo> {
  return request.get('/auth/me')
}

// 注册
export function register(data: {
  username: string
  password: string
  phone: string
  email?: string
  real_name?: string
  role?: string
}): Promise<UserInfo> {
  return request.post('/auth/register', data)
}
