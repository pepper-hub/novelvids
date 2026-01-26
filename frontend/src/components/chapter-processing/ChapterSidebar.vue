<script setup lang="ts">
/**
 * 章节侧边栏
 * 显示章节列表，支持状态筛选、选择和无限滚动加载
 */
import { computed, ref, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Chapter, ChapterWorkflowStatus } from '@/types'
import { getChapters } from '@/api/chapters'

interface Props {
  novelId: string
  selectedChapterId: string | null
}

interface Emits {
  (e: 'select', chapter: Chapter): void
  (e: 'chapters-loaded', chapters: Chapter[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { t } = useI18n()

// 分页状态
const chapters = ref<Chapter[]>([])
const currentPage = ref(1)
const totalChapters = ref(0)
const totalPages = ref(0)
const pageSize = 20
const loading = ref(false)
const loadingMore = ref(false)
const hasMore = computed(() => currentPage.value < totalPages.value)

// 筛选状态
type FilterType = 'all' | 'pending' | 'completed'
const filter = ref<FilterType>('all')

// 滚动容器引用
const scrollContainer = ref<HTMLElement | null>(null)

// 根据筛选条件过滤章节（客户端筛选当前已加载的数据）
const filteredChapters = computed(() => {
  if (filter.value === 'all') return chapters.value
  if (filter.value === 'pending') {
    return chapters.value.filter((c) => c.workflowStatus === 'pending')
  }
  return chapters.value.filter((c) => c.workflowStatus === 'completed')
})

// 加载章节
async function loadChapters(page: number = 1, append: boolean = false): Promise<void> {
  if (append) {
    loadingMore.value = true
  } else {
    loading.value = true
  }

  try {
    const response = await getChapters(props.novelId, page, pageSize)
    if (append) {
      chapters.value = [...chapters.value, ...response.items]
    } else {
      chapters.value = response.items
    }
    totalChapters.value = response.total
    totalPages.value = response.totalPages
    currentPage.value = page

    // 通知父组件章节已加载
    emit('chapters-loaded', chapters.value)
  } catch (err) {
    console.error('Failed to load chapters:', err)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

// 加载更多
async function loadMore(): Promise<void> {
  if (loadingMore.value || !hasMore.value) return
  await loadChapters(currentPage.value + 1, true)
}

// 刷新章节列表（重新从第一页加载）
async function refresh(): Promise<void> {
  currentPage.value = 1
  await loadChapters(1, false)
}

// 处理滚动事件
function handleScroll(event: Event): void {
  const target = event.target as HTMLElement
  const scrollBottom = target.scrollHeight - target.scrollTop - target.clientHeight

  // 距离底部 100px 时触发加载更多
  if (scrollBottom < 100 && hasMore.value && !loadingMore.value) {
    loadMore()
  }
}

function getStatusIcon(status: ChapterWorkflowStatus): string {
  switch (status) {
    case 'completed':
      return '✅'
    case 'generating':
      return '🎬'
    case 'storyboard_ready':
      return '📋'
    case 'characters_extracted':
      return '👤'
    default:
      return '○'
  }
}

function getStatusClass(status: ChapterWorkflowStatus): string {
  switch (status) {
    case 'completed':
      return 'text-green-600 dark:text-green-400'
    case 'generating':
      return 'text-purple-600 dark:text-purple-400'
    case 'storyboard_ready':
      return 'text-blue-600 dark:text-blue-400'
    case 'characters_extracted':
      return 'text-amber-600 dark:text-amber-400'
    default:
      return 'text-gray-400 dark:text-gray-500'
  }
}

function handleSelect(chapter: Chapter): void {
  emit('select', chapter)
}

// 更新章节（供父组件调用）
function updateChapter(updatedChapter: Chapter): void {
  const index = chapters.value.findIndex((c) => c.id === updatedChapter.id)
  if (index !== -1) {
    chapters.value[index] = updatedChapter
  }
}

// 监听 novelId 变化，重新加载
watch(
  () => props.novelId,
  () => {
    chapters.value = []
    currentPage.value = 1
    loadChapters(1)
  }
)

// 初始加载
onMounted(() => {
  loadChapters(1)
})

// 暴露方法供父组件调用
defineExpose({
  refresh,
  updateChapter,
})
</script>

<template>
  <div class="flex flex-col h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
    <!-- 标题 -->
    <div class="p-4 border-b border-gray-200 dark:border-gray-700">
      <h3 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        {{ t('chapterProcessing.sidebar.title') }}
      </h3>
      <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
        {{ t('chapterProcessing.sidebar.total', { count: totalChapters }) }}
      </p>
    </div>

    <!-- 筛选按钮 -->
    <div class="p-2 border-b border-gray-200 dark:border-gray-700">
      <div class="flex gap-1">
        <button
          v-for="f in ['all', 'pending', 'completed'] as FilterType[]"
          :key="f"
          @click="filter = f"
          class="flex-1 px-2 py-1 text-xs font-medium rounded transition-colors"
          :class="filter === f
            ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'"
        >
          {{ t(`chapterProcessing.sidebar.filter.${f}`) }}
        </button>
      </div>
    </div>

    <!-- 章节列表 -->
    <div
      ref="scrollContainer"
      class="flex-1 overflow-y-auto"
      @scroll="handleScroll"
    >
      <!-- 初始加载状态 -->
      <div v-if="loading && chapters.length === 0" class="flex items-center justify-center py-8">
        <svg class="w-6 h-6 animate-spin text-primary-500" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      </div>

      <!-- 空状态 -->
      <div v-else-if="filteredChapters.length === 0" class="text-center py-8 px-4">
        <p class="text-sm text-gray-500 dark:text-gray-400">
          {{ t('chapterProcessing.sidebar.empty') }}
        </p>
      </div>

      <!-- 章节项 -->
      <template v-else>
        <div class="divide-y divide-gray-100 dark:divide-gray-700">
          <button
            v-for="chapter in filteredChapters"
            :key="chapter.id"
            @click="handleSelect(chapter)"
            class="w-full px-4 py-3 text-left transition-colors hover:bg-gray-50 dark:hover:bg-gray-700/50"
            :class="selectedChapterId === chapter.id
              ? 'bg-primary-50 dark:bg-primary-900/20 border-l-2 border-primary-500'
              : ''"
          >
            <div class="flex items-center gap-3">
              <span :class="getStatusClass(chapter.workflowStatus)" class="text-lg">
                {{ getStatusIcon(chapter.workflowStatus) }}
              </span>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="text-xs font-medium text-gray-500 dark:text-gray-400">
                    {{ t('chapterProcessing.sidebar.chapterNumber', { number: chapter.number }) }}
                  </span>
                </div>
                <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {{ chapter.title }}
                </p>
              </div>
              <svg
                v-if="selectedChapterId === chapter.id"
                class="w-4 h-4 text-primary-500 flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </div>
          </button>
        </div>

        <!-- 加载更多指示器 -->
        <div v-if="loadingMore" class="flex items-center justify-center py-4">
          <svg class="w-5 h-5 animate-spin text-primary-500" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        </div>

        <!-- 没有更多数据 -->
        <div v-else-if="!hasMore && chapters.length > 0" class="text-center py-3 text-xs text-gray-400 dark:text-gray-500">
          {{ t('chapterProcessing.sidebar.noMore') }}
        </div>
      </template>
    </div>

    <!-- 状态图例 -->
    <div class="p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
      <div class="grid grid-cols-2 gap-1 text-xs">
        <div class="flex items-center gap-1.5 text-gray-500 dark:text-gray-400">
          <span>○</span>
          <span>{{ t('chapterProcessing.sidebar.status.pending') }}</span>
        </div>
        <div class="flex items-center gap-1.5 text-amber-600 dark:text-amber-400">
          <span>👤</span>
          <span>{{ t('chapterProcessing.sidebar.status.charactersExtracted') }}</span>
        </div>
        <div class="flex items-center gap-1.5 text-blue-600 dark:text-blue-400">
          <span>📋</span>
          <span>{{ t('chapterProcessing.sidebar.status.storyboardReady') }}</span>
        </div>
        <div class="flex items-center gap-1.5 text-green-600 dark:text-green-400">
          <span>✅</span>
          <span>{{ t('chapterProcessing.sidebar.status.completed') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
