import api from './client'
import type { User, TokenResponse } from '@/types'

export async function login(username: string, password: string): Promise<TokenResponse> {
  const response = await api.post('/auth/login', { username, password })
  return response.data
}

export async function register(
  username: string,
  email: string,
  password: string
): Promise<User> {
  const response = await api.post('/auth/register', { username, email, password })
  return response.data
}

export async function refreshToken(refreshToken: string): Promise<TokenResponse> {
  const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
  return response.data
}
