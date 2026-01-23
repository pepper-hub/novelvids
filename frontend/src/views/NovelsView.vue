<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useNovelStore } from '@/stores'
import { getStatusColor } from '@/utils/status'

const { t } = useI18n()
const novelStore = useNovelStore()

const showCreateModal = ref(false)
const newNovel = ref({
  title: '',
  content: '',
  author: '',
})

// upload file modal and helpers
const showUploadModal = ref(false)
const filePreview = ref('')
const fileName = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

function handleFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  const f = target.files && target.files[0]
  if (!f) return
  fileName.value = f.name
  const reader = new FileReader()
  reader.onload = () => {
    filePreview.value = String(reader.result || '')
    showUploadModal.value = true
  }
  reader.readAsText(f)
  // reset input so same file can be picked again
  target.value = ''
}

function confirmInsert() {
  newNovel.value.content = filePreview.value
  showUploadModal.value = false
}

function cancelUpload() {
  filePreview.value = ''
  fileName.value = ''
  showUploadModal.value = false
}

function openFilePicker() {
  const el = fileInput.value
  if (el && typeof (el as any).click === 'function') {
    ;(el as any).click()
  } else {
    // element not ready yet
    // eslint-disable-next-line no-console
    console.warn('file input not ready')
  }
}

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
          <span>{{ novel.totalChapters ?? novel.total_chapters }} {{ t('novels.chapters') }}</span>
          <span>{{ novel.processedChapters ?? novel.processed_chapters }} {{ t('novels.processedChapters') }}</span>
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
            <div class="flex items-end gap-3">
              <textarea
                v-model="newNovel.content"
                class="input min-h-[200px] flex-1"
                :placeholder="t('novels.content')"
                required
              ></textarea>
              <div class="flex flex-col gap-2">
                <input ref="fileInput" type="file" accept=".txt" class="hidden" @change="handleFileChange" />
                <button type="button" @click="openFilePicker" class="btn-secondary">{{ t('novels.uploadTxt') || '上传 TXT' }}</button>
              </div>
            </div>
          </div>
          <div class="flex gap-3 justify-end">
            <button type="button" @click="showCreateModal = false" class="btn-secondary">{{ t('common.cancel') }}</button>
            <button type="submit" class="btn-primary">{{ t('common.create') }}</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Upload preview/confirm modal -->
    <div v-if="showUploadModal" class="fixed inset-0 z-60 flex items-center justify-center bg-black/60 fixed-modal">
      <div class="card w-full max-w-2xl mx-4 p-6">
        <h3 class="text-lg font-semibold mb-2">{{ fileName }}</h3>
        <div class="max-h-64 overflow-auto bg-gray-50 p-3 rounded mb-4 whitespace-pre-wrap">{{ filePreview }}</div>
        <div class="flex justify-end gap-3">
          <button type="button" @click="cancelUpload" class="btn-secondary">{{ t('common.cancel') }}</button>
          <button type="button" @click="confirmInsert" class="btn-primary">{{ t('novels.insertIntoContent') || '插入到内容' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
/* Override spacing so modals fully cover (remove top margin between visible siblings) */
.space-y-6 > :not([hidden]) ~ :not([hidden]) {
  margin-top: 0 !important;
}

/* Ensure upload modal sits above create modal and covers fully */
.fixed-modal {
  z-index: 9999;
}
</style>
