import api from './client'
import type { Chapter, ChapterDetail, PaginatedResponse } from '@/types'

export async function getChapters(
  novelId: string,
  page: number = 1,
  pageSize: number = 20
): Promise<PaginatedResponse<Chapter>> {
  const response = await api.get('/chapters', {
    params: { novel_id: novelId, page, page_size: pageSize }
  })
  return response.data
}

export async function getChapter(id: string): Promise<ChapterDetail> {
  const response = await api.get(`/chapters/${id}`)
  return response.data
}

export async function updateChapter(
  id: string,
  data: { title?: string; content?: string }
): Promise<Chapter> {
  const response = await api.put(`/chapters/${id}`, data)
  return response.data
}

export async function deleteChapter(id: string): Promise<void> {
  await api.delete(`/chapters/${id}`)
}
