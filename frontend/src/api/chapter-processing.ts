/**
 * 章节处理 API 客户端
 */
import api from './client'
import type {
  CharacterAsset,
  CharacterPrompts,
  ChapterExtractionResult,
  ProcessChapterRequest,
  ProcessChaptersBatchRequest,
} from '@/types'

/**
 * 处理单个章节，提取角色信息
 */
export async function processChapter(
  chapterId: string
): Promise<ChapterExtractionResult> {
  const request: ProcessChapterRequest = { chapter_id: chapterId }
  const response = await api.post('/chapter-processing/process', request)
  return transformExtractionResult(response.data)
}

/**
 * 批量处理章节（同步）
 */
export async function processChaptersBatch(
  novelId: string,
  startChapter: number = 1,
  endChapter?: number
): Promise<ChapterExtractionResult[]> {
  const request: ProcessChaptersBatchRequest = {
    novel_id: novelId,
    start_chapter: startChapter,
    end_chapter: endChapter ?? null,
  }
  const response = await api.post('/chapter-processing/process-batch', request)
  return response.data.map(transformExtractionResult)
}

/**
 * 异步批量处理章节
 */
export async function processChaptersBatchAsync(
  novelId: string,
  startChapter: number = 1,
  endChapter?: number
): Promise<{ message: string; novelId: string }> {
  const request: ProcessChaptersBatchRequest = {
    novel_id: novelId,
    start_chapter: startChapter,
    end_chapter: endChapter ?? null,
  }
  const response = await api.post('/chapter-processing/process-batch-async', request)
  return {
    message: response.data.message,
    novelId: response.data.novel_id,
  }
}

/**
 * 获取角色的图像生成 prompts
 */
export async function getCharacterPrompts(
  novelId: string,
  chapterNumber?: number
): Promise<CharacterPrompts> {
  const params = chapterNumber ? { chapter_number: chapterNumber } : {}
  const response = await api.get(`/chapter-processing/prompts/${novelId}`, { params })
  return {
    novelId: response.data.novel_id,
    chapterNumber: response.data.chapter_number,
    prompts: response.data.prompts,
  }
}

/**
 * 获取小说的所有角色资产
 */
export async function getCharacterAssets(novelId: string): Promise<CharacterAsset[]> {
  const response = await api.get(`/chapter-processing/assets/${novelId}`)
  return response.data.map(transformCharacterAsset)
}

// ==================== 数据转换函数 ====================

function transformExtractionResult(data: any): ChapterExtractionResult {
  return {
    chapterNumber: data.chapter_number,
    entities: data.entities.map((e: any) => ({
      name: e.name,
      entityType: e.entity_type,
      visualDesc: e.visual_desc,
      actionContext: e.action_context,
    })),
    aliasRelations: data.alias_relations.map((r: any) => ({
      alias: r.alias,
      canonicalName: r.canonical_name,
      reason: r.reason,
      chapterDiscovered: r.chapter_discovered,
    })),
    characterPrompts: data.character_prompts,
  }
}

function transformCharacterAsset(data: any): CharacterAsset {
  return {
    canonicalName: data.canonical_name,
    characterType: data.character_type,
    baseTraits: data.base_traits,
    aliases: data.aliases,
    visualStates: data.visual_states.map((s: any) => ({
      chapterNumber: s.chapter_number,
      aliasUsed: s.alias_used,
      currentState: s.current_state,
    })),
    lastUpdatedChapter: data.last_updated_chapter,
  }
}
