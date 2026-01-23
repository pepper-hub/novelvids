import api from './client'
import type { Novel, NovelDetail, PaginatedResponse } from '@/types'

export async function getNovels(
  page: number = 1,
  pageSize: number = 20
): Promise<PaginatedResponse<Novel>> {
  const response = await api.get('/novels', { params: { page, page_size: pageSize } })
  return response.data
}

export async function getNovel(id: string): Promise<NovelDetail> {
  const response = await api.get(`/novels/${id}`)
  return response.data
}

export async function createNovel(data: {
  title: string
  content: string
  author?: string
}): Promise<Novel> {
  const response = await api.post('/novels', data)
  return response.data
}

export async function updateNovel(
  id: string,
  data: { title?: string; content?: string; author?: string }
): Promise<Novel> {
  const response = await api.put(`/novels/${id}`, data)
  return response.data
}

export async function deleteNovel(id: string): Promise<void> {
  await api.delete(`/novels/${id}`)
}

export async function extractChapters(id: string): Promise<Novel> {
  const response = await api.post(`/novels/${id}/extract-chapters`)
  return response.data
}
