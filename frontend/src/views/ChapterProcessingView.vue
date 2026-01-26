<script setup lang="ts">
/**
 * 章节处理视图
 * 左右分栏布局：左侧章节列表（分页加载），右侧步骤面板，底部角色资产库
 */
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useNovelStore, useChapterProcessingStore, useToastStore } from '@/stores'
import {
  ChapterSidebar,
  ChapterStepPanel,
  CharacterAssetList,
  PromptViewModal,
} from '@/components/chapter-processing'
import type { CharacterAsset, Chapter } from '@/types'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const novelStore = useNovelStore()
const processingStore = useChapterProcessingStore()
const toastStore = useToastStore()

const novelId = computed(() => route.params.id as string)

// 章节侧边栏组件引用
const chapterSidebarRef = ref<InstanceType<typeof ChapterSidebar> | null>(null)

// 选中的章节
const selectedChapter = ref<Chapter | null>(null)

// Prompt 模态框状态
const showPromptModal = ref(false)
const selectedAsset = ref<CharacterAsset | null>(null)

onMounted(async () => {
  // 加载小说信息
  await novelStore.fetchNovel(novelId.value)

  // 检查工作流状态 - 如果不能提取角色，返回小说详情页
  if (novelStore.currentNovel && !novelStore.currentNovel.canExtractCharacters) {
    toastStore.warning(t('novels.workflowHints.needChapters'))
    router.push(`/novels/${novelId.value}`)
    return
  }

  // 加载已有的角色资产
  try {
    await processingStore.loadAssets(novelId.value)
  } catch {
    // 首次可能没有资产，忽略错误
  }
})

// 选择章节
function handleSelectChapter(chapter: Chapter): void {
  selectedChapter.value = chapter
}

// 章节加载完成回调
function handleChaptersLoaded(chapters: Chapter[]): void {
  // 如果有选中的章节，更新其状态
  if (selectedChapter.value) {
    const updated = chapters.find((c) => c.id === selectedChapter.value?.id)
    if (updated) {
      selectedChapter.value = updated
    }
  }
}

// 提取角色
async function handleExtractCharacters(chapterId: string): Promise<void> {
  try {
    await processingStore.processSingleChapter(chapterId)
    // 刷新章节列表以更新状态
    await chapterSidebarRef.value?.refresh()
    // 重新加载资产
    await processingStore.loadAssets(novelId.value)
    toastStore.success(t('chapterProcessing.extraction.extractionComplete'))
  } catch (err) {
    const message = err instanceof Error ? err.message : t('chapterProcessing.extraction.extractionFailed')
    toastStore.error(message)
  }
}

// 创建分镜（占位）
async function handleCreateStoryboard(_chapterId: string): Promise<void> {
  toastStore.info(t('chapterProcessing.workflow.comingSoon'))
}

// 生成视频（占位）
async function handleGenerateVideo(_chapterId: string): Promise<void> {
  toastStore.info(t('chapterProcessing.workflow.comingSoon'))
}

// 刷新资产
async function handleRefreshAssets(): Promise<void> {
  try {
    await processingStore.loadAssets(novelId.value)
  } catch (err) {
    const message = err instanceof Error ? err.message : t('chapterProcessing.assets.loadFailed')
    toastStore.error(message)
  }
}

// 查看 Prompt
function handleViewPrompt(asset: CharacterAsset): void {
  selectedAsset.value = asset
  showPromptModal.value = true
}

// 编辑角色
function handleEditAsset(asset: CharacterAsset): void {
  toastStore.info(t('chapterProcessing.assets.editingInProgress', { name: asset.canonicalName }))
}

// 复制 Prompt
function handleCopyPrompt(_prompt: string): void {
  toastStore.success(t('chapterProcessing.prompts.copied'))
}

// 返回小说详情
function goBack(): void {
  router.push(`/novels/${novelId.value}`)
}
</script>

<template>
  <div class="h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
    <!-- 顶部导航 -->
    <header class="flex-shrink-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div class="px-4 sm:px-6">
        <div class="flex items-center justify-between h-14">
          <div class="flex items-center gap-4">
            <button
              @click="goBack"
              class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <div v-if="novelStore.currentNovel">
              <h1 class="text-base font-semibold text-gray-900 dark:text-white">
                {{ novelStore.currentNovel.title }}
              </h1>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                {{ t('chapterProcessing.title') }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <div v-if="novelStore.isLoading" class="flex-1 flex items-center justify-center">
      <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full" />
    </div>

    <template v-else-if="novelStore.currentNovel">
      <div class="flex-1 flex overflow-hidden">
        <!-- 左侧：章节列表 (25%) -->
        <div class="w-1/4 min-w-[280px] max-w-[360px] flex-shrink-0">
          <ChapterSidebar
            ref="chapterSidebarRef"
            :novel-id="novelId"
            :selected-chapter-id="selectedChapter?.id ?? null"
            @select="handleSelectChapter"
            @chapters-loaded="handleChaptersLoaded"
          />
        </div>

        <!-- 右侧：步骤面板 (75%) -->
        <div class="flex-1 bg-white dark:bg-gray-800 overflow-hidden">
          <ChapterStepPanel
            :chapter="selectedChapter"
            :is-processing="processingStore.isProcessing"
            :processing-message="processingStore.progress.message"
            @extract-characters="handleExtractCharacters"
            @create-storyboard="handleCreateStoryboard"
            @generate-video="handleGenerateVideo"
          />
        </div>
      </div>

      <!-- 底部：角色资产库 -->
      <div class="flex-shrink-0 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div class="p-4 max-h-64 overflow-y-auto">
          <CharacterAssetList
            :assets="processingStore.assets"
            :is-loading="processingStore.isLoading"
            :compact="true"
            @refresh="handleRefreshAssets"
            @edit="handleEditAsset"
            @view-prompt="handleViewPrompt"
          />
        </div>
      </div>
    </template>

    <div v-else class="flex-1 flex items-center justify-center">
      <p class="text-gray-500 dark:text-gray-400">{{ t('chapterProcessing.novelNotFound') }}</p>
    </div>

    <!-- Prompt 查看模态框 -->
    <PromptViewModal
      v-model:show="showPromptModal"
      :asset="selectedAsset"
      @copy="handleCopyPrompt"
    />
  </div>
</template>
