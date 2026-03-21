// 菜单权限配置
// key: 角色名, value: 该角色可访问的菜单 name 列表
export const menuPermission: Record<string, string[]> = {
  admin: [
    'dashboard',
    'leads',
    'candidates',
    'talents',
    'customers',
    'projects',
    'onboardings',
    'channels',
    'users',
    'dicts'
  ],
  supervisor: [
    'dashboard',
    'leads',
    'candidates',
    'talents',
    'customers',
    'projects',
    'onboardings'
  ],
  recruiter: [
    'dashboard',
    'leads',
    'candidates',
    'talents'
  ]
}

// 角色名称映射
export const roleMap: Record<string, string> = {
  admin: '管理员',
  supervisor: '招聘主管',
  recruiter: '招聘专员'
}
