import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { login as apiLogin, register as apiRegister } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  const isAuthenticated = computed(() => !!accessToken.value)

  async function login(username: string, password: string): Promise<void> {
    const response = await apiLogin(username, password)
    accessToken.value = response.access_token
    refreshToken.value = response.refresh_token
    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('refresh_token', response.refresh_token)
  }

  async function register(username: string, email: string, password: string): Promise<void> {
    await apiRegister(username, email, password)
  }

  function logout(): void {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    login,
    register,
    logout,
  }
})
