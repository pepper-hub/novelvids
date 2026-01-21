<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useNovelStore } from '@/stores'

const { t } = useI18n()

const novelStore = useNovelStore()

const showCreateModal = ref(false)
const newNovel = ref({
  title: '',
  content: '',
  author: '',
})

onMounted(() => {
  novelStore.fetchNovels()
})

async function handleCreate(): Promise<void> {
  if (!newNovel.value.title || !newNovel.value.content) return

  await novelStore.addNovel({
    title: newNovel.value.title,
    content: newNovel.value.content,
    author: newNovel.value.author || undefined,
  })

  showCreateModal.value = false
  newNovel.value = { title: '', content: '', author: '' }
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    queued: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    running: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
    completed: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    failed: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    cancelled: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400',
  }
  return colors[status] || colors.pending
}
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ t('novels.title') }}</h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1">{{ t('novels.myNovels') }}</p>
      </div>
      <button @click="showCreateModal = true" class="btn-primary">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        {{ t('novels.uploadNovel') }}
      </button>
    </div>

    <div v-if="novelStore.isLoading" class="text-center py-12">
      <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
      <p class="text-gray-500 mt-4">{{ t('common.loading') }}</p>
    </div>

    <div v-else-if="novelStore.novels.length === 0" class="card p-12 text-center">
      <svg class="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">{{ t('novels.noNovels') }}</h3>
      <p class="text-gray-500 dark:text-gray-400 mb-4">{{ t('novels.uploadFirst') }}</p>
      <button @click="showCreateModal = true" class="btn-primary">{{ t('novels.uploadNovel') }}</button>
    </div>

    <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      <router-link
        v-for="novel in novelStore.novels"
        :key="novel.id"
        :to="`/novels/${novel.id}`"
        class="card p-6 hover:shadow-lg transition-shadow"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="w-12 h-12 bg-gradient-to-br from-primary-400 to-accent-400 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <span :class="['px-2 py-1 text-xs font-medium rounded-full', getStatusColor(novel.status)]">
            {{ t(`novels.novelStatus.${novel.status}`) }}
          </span>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">{{ novel.title }}</h3>
        <p v-if="novel.author" class="text-sm text-gray-500 dark:text-gray-400 mb-4">{{ t('common.byAuthor', { author: novel.author }) }}</p>
        <div class="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
          <span>{{ novel.totalChapters }} {{ t('novels.chapters') }}</span>
          <span>{{ novel.processedChapters }} {{ t('novels.processedChapters') }}</span>
        </div>
      </router-link>
    </div>

    <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="card w-full max-w-lg mx-4 p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">{{ t('novels.uploadNovel') }}</h2>
        <form @submit.prevent="handleCreate" class="space-y-4">
          <div>
            <label class="label">{{ t('novels.novelTitle') }}</label>
            <input v-model="newNovel.title" type="text" class="input" :placeholder="t('novels.novelTitle')" required />
          </div>
          <div>
            <label class="label">{{ t('novels.author') }} ({{ t('common.optional') }})</label>
            <input v-model="newNovel.author" type="text" class="input" :placeholder="t('novels.author')" />
          </div>
          <div>
            <label class="label">{{ t('novels.content') }}</label>
            <textarea
              v-model="newNovel.content"
              class="input min-h-[200px]"
              :placeholder="t('novels.content')"
              required
            ></textarea>
          </div>
          <div class="flex gap-3 justify-end">
            <button type="button" @click="showCreateModal = false" class="btn-secondary">{{ t('common.cancel') }}</button>
            <button type="submit" class="btn-primary">{{ t('common.create') }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
