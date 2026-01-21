<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useNovelStore } from '@/stores'

const { t } = useI18n()
const route = useRoute()
const novelStore = useNovelStore()

onMounted(() => {
  const id = route.params.id as string
  novelStore.fetchNovel(id)
})
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
        <button class="btn-primary">{{ t('common.processNovel') }}</button>
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
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('novels.chapters') }}</h2>
            <div class="text-center py-8 text-gray-500 dark:text-gray-400">
              <p>{{ t('common.noChaptersExtracted') }}</p>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="card p-6">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('novels.status') }}</h2>
            <div class="space-y-4">
              <div class="flex justify-between">
                <span class="text-gray-500 dark:text-gray-400">{{ t('novels.status') }}</span>
                <span class="font-medium text-gray-900 dark:text-white capitalize">{{ novelStore.currentNovel.status }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500 dark:text-gray-400">{{ t('novels.totalChapters') }}</span>
                <span class="font-medium text-gray-900 dark:text-white">{{ novelStore.currentNovel.totalChapters }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500 dark:text-gray-400">{{ t('novels.processedChapters') }}</span>
                <span class="font-medium text-gray-900 dark:text-white">{{ novelStore.currentNovel.processedChapters }}</span>
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
  </div>
</template>
