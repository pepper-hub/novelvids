<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useInfiniteScroll } from '@vueuse/core'
import { VueDraggable } from 'vue-draggable-plus'
import { useNovelStore, useChapterStore, useToastStore } from '@/stores'
import { getStatusColor } from '@/utils/status'
import ChapterEditModal from '@/components/ChapterEditModal.vue'
import type { ChapterDetail } from '@/types'

const { t } = useI18n()
const route = useRoute()
const novelStore = useNovelStore()
const chapterStore = useChapterStore()
const toastStore = useToastStore()

const scrollContainer = ref<HTMLElement | null>(null)

useInfiniteScroll(
  scrollContainer,
  async () => {
    if (novelStore.currentNovel && !chapterStore.isLoading && chapterStore.hasMore) {
      await chapterStore.loadMore(novelStore.currentNovel.id)
    }
  },
  { distance: 10 }
)

const isProcessing = ref(false)
const showEditModal = ref(false)
const editingChapter = ref<ChapterDetail | null>(null)
const isReordering = ref(false)

onMounted(() => {
  const id = route.params.id as string
  novelStore.fetchNovel(id)
  chapterStore.fetchChapters(id)
})

async function handleProcessNovel(): Promise<void> {
  if (!novelStore.currentNovel) return

  isProcessing.value = true

  try {
    await novelStore.processNovel(novelStore.currentNovel.id)
    toastStore.success(t('generate.processNovelSuccess'))
    await novelStore.fetchNovel(novelStore.currentNovel.id)
    await chapterStore.fetchChapters(novelStore.currentNovel.id)
  } catch (err) {
    const message = err instanceof Error ? err.message : t('generate.generationFailed')
    toastStore.error(message)
  } finally {
    isProcessing.value = false
  }
}

async function handleEditChapter(chapterId: string): Promise<void> {
  await chapterStore.fetchChapter(chapterId)
  editingChapter.value = chapterStore.currentChapter
  showEditModal.value = true
}

async function handleSaveChapter(data: { title: string; content: string }): Promise<void> {
  if (!editingChapter.value) return

  try {
    await chapterStore.editChapter(editingChapter.value.id, data)
    showEditModal.value = false
    editingChapter.value = null
    toastStore.success(t('common.saved', '保存成功'))
  } catch (err) {
    const message = err instanceof Error ? err.message : t('common.saveFailed')
    toastStore.error(message)
  }
}

async function onReorder() {
  isReordering.value = true
  try {
    const updates = chapterStore.chapters.map((chapter, index) => {
      // With infinite scroll, the list contains all loaded chapters in order.
      // So the new number is simply index + 1
      const newNumber = index + 1
      return { id: chapter.id, number: newNumber }
    })
    
    // Check if any numbers actually changed to avoid unnecessary API calls
    const hasChanges = updates.some(() => true)

    if (hasChanges) {
       await chapterStore.reorderChapters(updates)
       // toastStore.success(t('common.reorderSuccess', '排序已更新')) // Optional: might be too noisy
    }
  } catch (error) {
    console.error('Failed to reorder chapters:', error)
    toastStore.error(t('common.reorderFailed', '排序更新失败'))
    
    // Refresh chapters to revert state on error
    if (novelStore.currentNovel) {
      await chapterStore.fetchChapters(novelStore.currentNovel.id, chapterStore.currentPage)
    }
  } finally {
    isReordering.value = false
  }
}

</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <div v-if="novelStore.isLoading" class="text-center py-12">
      <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
      <p class="text-gray-500 mt-4">{{ t('common.loading') }}</p>
    </div>

    <template v-else-if="novelStore.currentNovel">
      <div class="flex items-center justify-between">
        <div>
          <router-link to="/novels" class="text-primary-500 hover:text-primary-600 text-sm mb-2 inline-block">
            &larr; {{ t('common.backToNovels') }}
          </router-link>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ novelStore.currentNovel.title }}</h1>
          <p v-if="novelStore.currentNovel.author" class="text-gray-500 dark:text-gray-400 mt-1">
            {{ t('common.byAuthor', { author: novelStore.currentNovel.author }) }}
          </p>
        </div>
        <button
          @click="handleProcessNovel"
          :disabled="isProcessing || novelStore.currentNovel.status === 'running' || (novelStore.currentNovel.totalChapters ?? novelStore.currentNovel.total_chapters) > 0"
          class="btn-primary"
        >
          <span v-if="isProcessing" class="flex items-center gap-2">
            <div class="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
            {{ t('generate.processingNovel') }}
          </span>
          <span v-else>{{ t('common.processNovel') }}</span>
        </button>
      </div>

      <div class="grid lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <div class="card p-6">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('common.contentPreview') }}</h2>
            <div class="prose dark:prose-invert max-h-96 overflow-y-auto">
              <p class="whitespace-pre-wrap text-gray-600 dark:text-gray-300">
                {{ novelStore.currentNovel.content.substring(0, 2000) }}...
              </p>
            </div>
          </div>

          <div class="card p-6">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('chapters.title') }}</h2>
            
            <div v-if="(novelStore.currentNovel.totalChapters ?? novelStore.currentNovel.total_chapters) === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
              <p>{{ t('common.noChaptersExtracted') }}</p>
            </div>
            
            <div v-else-if="chapterStore.isLoading" class="text-center py-8">
              <div class="animate-spin w-6 h-6 border-3 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
              <p class="text-gray-500 dark:text-gray-400 mt-3 text-sm">{{ t('common.loading') }}</p>
            </div>
            
            <div v-else class="space-y-3 max-h-[600px] overflow-y-auto" ref="scrollContainer">
              <VueDraggable 
                v-model="chapterStore.chapters" 
                @end="onReorder"
                :animation="150"
                ghost-class="opacity-50"
                class="space-y-3"
              >
                <div 
                  v-for="chapter in chapterStore.chapters" 
                  :key="chapter.id"
                  class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition group cursor-move"
                >
                  <div class="flex items-center justify-between">
                    <div class="flex-1">
                      <div class="flex items-center gap-2">
                        <span class="text-sm font-medium text-gray-500 dark:text-gray-400">
                          {{ t('chapters.chapter', { number: chapter.number }) }}
                        </span>
                        <h3 class="text-base font-medium text-gray-900 dark:text-white">
                          {{ chapter.title }}
                        </h3>
                      </div>
                      <div class="flex items-center gap-4 mt-2 text-xs text-gray-500 dark:text-gray-400">
                        <span :class="['px-2 py-1 rounded-full capitalize', getStatusColor(chapter.status)]">
                          {{ t('novels.novelStatus.' + chapter.status) }}
                        </span>
                        <span>{{ chapter.sceneCount }} {{ t('novels.scenes', '场景') }}</span>
                      </div>
                    </div>
                    <button
                      @click="handleEditChapter(chapter.id)"
                      class="opacity-0 group-hover:opacity-100 transition px-3 py-1.5 text-sm text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg"
                    >
                      {{ t('common.edit') }}
                    </button>
                  </div>
                </div>
              </VueDraggable>
              
              <!-- Loading More Indicator -->
              <div v-if="chapterStore.isLoading && chapterStore.currentPage > 1" class="text-center py-4">
                <div class="animate-spin w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
                <p class="text-xs text-gray-500 mt-2">{{ t('common.loadingMore', '加载更多...') }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="card p-6">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('novels.status') }}</h2>
            <div class="space-y-4">
              <div class="flex justify-between">
                <span class="text-gray-500 dark:text-gray-400">{{ t('novels.status') }}</span>
                <span :class="['px-2 py-1 text-xs font-medium rounded-full capitalize', getStatusColor(novelStore.currentNovel.status)]">
                  {{ t('novels.novelStatus.' + novelStore.currentNovel.status) }}
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500 dark:text-gray-400">{{ t('novels.totalChapters') }}</span>
                <span class="font-medium text-gray-900 dark:text-white">{{ novelStore.currentNovel.totalChapters ?? novelStore.currentNovel.total_chapters }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500 dark:text-gray-400">{{ t('novels.processedChapters') }}</span>
                <span class="font-medium text-gray-900 dark:text-white">{{ novelStore.currentNovel.processedChapters ?? novelStore.currentNovel.processed_chapters }}</span>
              </div>
            </div>
          </div>

          <div class="card p-6">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('novels.characters') }}</h2>
            <div class="text-center py-4 text-gray-500 dark:text-gray-400">
              <p class="text-sm">{{ t('common.noCharactersExtracted') }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="text-center py-12">
      <p class="text-gray-500 dark:text-gray-400">{{ t('common.novelNotFound') }}</p>
    </div>

    <ChapterEditModal
      v-model:show="showEditModal"
      :chapter="editingChapter"
      @save="handleSaveChapter"
    />
  </div>
</template>
