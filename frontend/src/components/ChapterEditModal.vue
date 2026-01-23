<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChapterDetail } from '@/types'

interface Props {
  chapter: ChapterDetail | null
  show: boolean
}

interface Emits {
  (e: 'update:show', value: boolean): void
  (e: 'save', data: { title: string; content: string }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { t } = useI18n()

const title = ref('')
const content = ref('')
const isSaving = ref(false)

watch(() => props.chapter, (newChapter) => {
  if (newChapter) {
    title.value = newChapter.title
    content.value = newChapter.content
  }
}, { immediate: true })

function closeModal(): void {
  emit('update:show', false)
}

async function handleSave(): Promise<void> {
  if (!title.value.trim() || !content.value.trim()) {
    return
  }

  isSaving.value = true
  try {
    emit('save', {
      title: title.value.trim(),
      content: content.value.trim()
    })
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    @click.self="closeModal"
  >
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-hidden flex flex-col">
      <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
          {{ t('chapters.editChapter') }}
        </h2>
        <button
          @click="closeModal"
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ t('chapters.chapterTitle') }}
          </label>
          <input
            v-model="title"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            :placeholder="t('chapters.enterChapterTitle')"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ t('chapters.chapterContent') }}
          </label>
          <textarea
            v-model="content"
            rows="15"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none font-mono text-sm"
            :placeholder="t('chapters.enterChapterContent')"
          ></textarea>
        </div>
      </div>

      <div class="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
        <button
          @click="closeModal"
          class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
        >
          {{ t('common.cancel') }}
        </button>
        <button
          @click="handleSave"
          :disabled="isSaving || !title.trim() || !content.trim()"
          class="btn-primary"
        >
          <span v-if="isSaving" class="flex items-center gap-2">
            <div class="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
            {{ t('common.saving') }}
          </span>
          <span v-else>{{ t('common.save') }}</span>
        </button>
      </div>
    </div>
  </div>
</template>
