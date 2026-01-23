/**
 * 章节处理 Store
 * 管理角色提取、资产管理等状态
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  CharacterAsset,
  CharacterPrompts,
  ChapterExtractionResult,
  ProcessingProgress,
  WorkflowStep,
  WorkflowState,
} from '@/types'
import {
  processChapter,
  processChaptersBatch,
  processChaptersBatchAsync,
  getCharacterAssets,
  getCharacterPrompts,
} from '@/api'

export const useChapterProcessingStore = defineStore('chapterProcessing', () => {
  // ==================== 状态 ====================

  // 角色资产
  const assets = ref<CharacterAsset[]>([])
  const prompts = ref<CharacterPrompts | null>(null)

  // 提取结果历史
  const extractionResults = ref<ChapterExtractionResult[]>([])

  // 处理进度
  const progress = ref<ProcessingProgress>({
    status: 'idle',
    currentChapter: 0,
    totalChapters: 0,
    message: '',
  })

  // 工作流状态
  const workflow = ref<WorkflowState>({
    currentStep: 'extraction',
    completedSteps: [],
    canProceed: false,
  })

  // 加载状态
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // ==================== 计算属性 ====================

  const isProcessing = computed(() => progress.value.status === 'processing')

  const progressPercent = computed(() => {
    if (progress.value.totalChapters === 0) return 0
    return Math.round(
      (progress.value.currentChapter / progress.value.totalChapters) * 100
    )
  })

  const hasAssets = computed(() => assets.value.length > 0)

  const characterCount = computed(() => assets.value.length)

  const aliasCount = computed(() =>
    assets.value.reduce((sum, a) => sum + a.aliases.length, 0)
  )

  // ==================== 操作 ====================

  /**
   * 处理单个章节
   */
  async function processSingleChapter(chapterId: string): Promise<ChapterExtractionResult> {
    isLoading.value = true
    error.value = null
    progress.value.status = 'processing'
    progress.value.message = '正在提取角色信息...'

    try {
      const result = await processChapter(chapterId)
      extractionResults.value.push(result)
      progress.value.status = 'completed'
      progress.value.message = '提取完成'

      // 标记提取步骤完成
      if (!workflow.value.completedSteps.includes('extraction')) {
        workflow.value.completedSteps.push('extraction')
      }
      workflow.value.canProceed = true

      return result
    } catch (err) {
      progress.value.status = 'failed'
      progress.value.message = err instanceof Error ? err.message : '处理失败'
      error.value = progress.value.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 批量处理章节
   */
  async function processChapters(
    novelId: string,
    startChapter: number = 1,
    endChapter?: number
  ): Promise<ChapterExtractionResult[]> {
    isLoading.value = true
    error.value = null
    progress.value = {
      status: 'processing',
      currentChapter: startChapter,
      totalChapters: endChapter ?? startChapter,
      message: '正在批量处理章节...',
    }

    try {
      const results = await processChaptersBatch(novelId, startChapter, endChapter)
      extractionResults.value = results
      progress.value.status = 'completed'
      progress.value.currentChapter = results.length
      progress.value.message = `已处理 ${results.length} 个章节`

      // 标记提取步骤完成
      if (!workflow.value.completedSteps.includes('extraction')) {
        workflow.value.completedSteps.push('extraction')
      }
      workflow.value.canProceed = true

      return results
    } catch (err) {
      progress.value.status = 'failed'
      progress.value.message = err instanceof Error ? err.message : '处理失败'
      error.value = progress.value.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 异步批量处理章节
   */
  async function processChaptersAsync(
    novelId: string,
    startChapter: number = 1,
    endChapter?: number
  ): Promise<void> {
    isLoading.value = true
    error.value = null
    progress.value = {
      status: 'processing',
      currentChapter: 0,
      totalChapters: endChapter ?? 0,
      message: '任务已提交，正在后台处理...',
    }

    try {
      await processChaptersBatchAsync(novelId, startChapter, endChapter)
    } catch (err) {
      progress.value.status = 'failed'
      progress.value.message = err instanceof Error ? err.message : '提交失败'
      error.value = progress.value.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 加载角色资产
   */
  async function loadAssets(novelId: string): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      assets.value = await getCharacterAssets(novelId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 加载角色 prompts
   */
  async function loadPrompts(novelId: string, chapterNumber?: number): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      prompts.value = await getCharacterPrompts(novelId, chapterNumber)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 设置工作流步骤
   */
  function setWorkflowStep(step: WorkflowStep): void {
    workflow.value.currentStep = step
  }

  /**
   * 重置状态
   */
  function reset(): void {
    assets.value = []
    prompts.value = null
    extractionResults.value = []
    progress.value = {
      status: 'idle',
      currentChapter: 0,
      totalChapters: 0,
      message: '',
    }
    workflow.value = {
      currentStep: 'extraction',
      completedSteps: [],
      canProceed: false,
    }
    error.value = null
  }

  return {
    // 状态
    assets,
    prompts,
    extractionResults,
    progress,
    workflow,
    isLoading,
    error,

    // 计算属性
    isProcessing,
    progressPercent,
    hasAssets,
    characterCount,
    aliasCount,

    // 操作
    processSingleChapter,
    processChapters,
    processChaptersAsync,
    loadAssets,
    loadPrompts,
    setWorkflowStep,
    reset,
  }
})
