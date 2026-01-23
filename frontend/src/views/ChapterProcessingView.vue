<script setup lang="ts">
/**
 * 章节处理视图
 * 独立页面，处理角色提取、分镜等工作流
 */
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useNovelStore, useChapterStore, useChapterProcessingStore, useToastStore } from '@/stores'
import {
  WorkflowTabs,
  ExtractionPanel,
  CharacterAssetList,
  PromptViewModal,
} from '@/components/chapter-processing'
import type { CharacterAsset, WorkflowStep } from '@/types'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const novelStore = useNovelStore()
const chapterStore = useChapterStore()
const processingStore = useChapterProcessingStore()
const toastStore = useToastStore()

const novelId = computed(() => route.params.id as string)

// Prompt 模态框状态
const showPromptModal = ref(false)
const selectedAsset = ref<CharacterAsset | null>(null)

onMounted(async () => {
  // 加载小说和章节信息
  await novelStore.fetchNovel(novelId.value)
  await chapterStore.fetchChapters(novelId.value)

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

// 处理工作流步骤切换
function handleStepChange(step: WorkflowStep): void {
  processingStore.setWorkflowStep(step)
}

// 处理角色提取
async function handleProcess(options: { startChapter: number; endChapter?: number }): Promise<void> {
  try {
    await processingStore.processChapters(
      novelId.value,
      options.startChapter,
      options.endChapter ?? chapterStore.totalChapters
    )
    // 重新加载资产
    await processingStore.loadAssets(novelId.value)
    toastStore.success(t('chapterProcessing.extraction.extractionComplete'))
  } catch (err) {
    const message = err instanceof Error ? err.message : t('chapterProcessing.extraction.extractionFailed')
    toastStore.error(message)
  }
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
  // TODO: 打开编辑模态框
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
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- 顶部导航 -->
    <header class="sticky top-0 z-40 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center gap-4">
            <button
              @click="goBack"
              class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
            </button>
            <div v-if="novelStore.currentNovel">
              <h1 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ novelStore.currentNovel.title }}
              </h1>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                {{ t('chapterProcessing.title') }} · {{ t('chapterProcessing.chaptersCount', { count: chapterStore.totalChapters }) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div v-if="novelStore.isLoading" class="flex items-center justify-center py-20">
        <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>

      <template v-else-if="novelStore.currentNovel">
        <!-- 工作流标签页 -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm mb-6">
          <WorkflowTabs
            :current-step="processingStore.workflow.currentStep"
            :completed-steps="processingStore.workflow.completedSteps"
            @change="handleStepChange"
          />
        </div>

        <!-- 步骤内容 -->
        <div class="grid lg:grid-cols-5 gap-6">
          <!-- 左侧：主要操作区 -->
          <div class="lg:col-span-3">
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
              <!-- 角色提取 -->
              <ExtractionPanel
                v-if="processingStore.workflow.currentStep === 'extraction'"
                :progress="processingStore.progress"
                :results="processingStore.extractionResults"
                :total-chapters="chapterStore.totalChapters"
                @process="handleProcess"
              />

              <!-- 分镜处理（占位） -->
              <div
                v-else-if="processingStore.workflow.currentStep === 'storyboard'"
                class="text-center py-12"
              >
                <svg
                  class="w-16 h-16 mx-auto text-gray-400 dark:text-gray-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="1.5"
                    d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"
                  />
                </svg>
                <h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-white">
                  {{ t('chapterProcessing.workflow.storyboard') }}
                </h3>
                <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  {{ t('chapterProcessing.workflow.comingSoon') }}
                </p>
              </div>

              <!-- 视频生成（占位） -->
              <div
                v-else-if="processingStore.workflow.currentStep === 'generation'"
                class="text-center py-12"
              >
                <svg
                  class="w-16 h-16 mx-auto text-gray-400 dark:text-gray-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="1.5"
                    d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="1.5"
                    d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-white">
                  {{ t('chapterProcessing.workflow.generation') }}
                </h3>
                <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  {{ t('chapterProcessing.workflow.comingSoon') }}
                </p>
              </div>
            </div>
          </div>

          <!-- 右侧：角色资产库 -->
          <div class="lg:col-span-2">
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
              <CharacterAssetList
                :assets="processingStore.assets"
                :is-loading="processingStore.isLoading"
                @refresh="handleRefreshAssets"
                @edit="handleEditAsset"
                @view-prompt="handleViewPrompt"
              />
            </div>
          </div>
        </div>
      </template>

      <div v-else class="text-center py-20">
        <p class="text-gray-500 dark:text-gray-400">{{ t('chapterProcessing.novelNotFound') }}</p>
      </div>
    </main>

    <!-- Prompt 查看模态框 -->
    <PromptViewModal
      v-model:show="showPromptModal"
      :asset="selectedAsset"
      @copy="handleCopyPrompt"
    />
  </div>
</template>
