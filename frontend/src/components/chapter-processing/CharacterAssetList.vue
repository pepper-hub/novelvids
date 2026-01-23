<script setup lang="ts">
/**
 * 角色资产列表
 * 展示所有已提取的角色资产
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { CharacterAsset } from '@/types'
import CharacterAssetCard from './CharacterAssetCard.vue'

interface Props {
  assets: CharacterAsset[]
  isLoading?: boolean
}

interface Emits {
  (e: 'edit', asset: CharacterAsset): void
  (e: 'view-prompt', asset: CharacterAsset): void
  (e: 'refresh'): void
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
})
const emit = defineEmits<Emits>()
const { t } = useI18n()

const sortedAssets = computed(() => {
  return [...props.assets].sort((a, b) => {
    // 人物优先于物品
    if (a.characterType !== b.characterType) {
      return a.characterType === 'Person' ? -1 : 1
    }
    // 按最后更新章节降序
    return b.lastUpdatedChapter - a.lastUpdatedChapter
  })
})

const personCount = computed(() =>
  props.assets.filter((a) => a.characterType === 'Person').length
)

const objectCount = computed(() =>
  props.assets.filter((a) => a.characterType === 'Object').length
)
</script>

<template>
  <div class="space-y-6">
    <!-- 标题和统计 -->
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
          {{ t('chapterProcessing.assets.title') }}
        </h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {{ t('chapterProcessing.assets.summary', { total: assets.length, persons: personCount, objects: objectCount }) }}
        </p>
      </div>
      <button
        @click="emit('refresh')"
        :disabled="isLoading"
        class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        :title="t('chapterProcessing.assets.refresh')"
      >
        <svg
          class="w-5 h-5"
          :class="{ 'animate-spin': isLoading }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading && assets.length === 0" class="space-y-4">
      <div
        v-for="i in 3"
        :key="i"
        class="h-24 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse"
      />
    </div>

    <!-- 空状态 -->
    <div
      v-else-if="assets.length === 0"
      class="text-center py-12 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
    >
      <svg
        class="w-12 h-12 mx-auto text-gray-400 dark:text-gray-600"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.5"
          d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
        />
      </svg>
      <h4 class="mt-4 text-base font-medium text-gray-900 dark:text-white">
        {{ t('chapterProcessing.assets.noAssets') }}
      </h4>
      <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
        {{ t('chapterProcessing.assets.noAssetsHint') }}
      </p>
    </div>

    <!-- 资产网格 -->
    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <CharacterAssetCard
        v-for="asset in sortedAssets"
        :key="asset.canonicalName"
        :asset="asset"
        @edit="emit('edit', $event)"
        @view-prompt="emit('view-prompt', $event)"
      />
    </div>
  </div>
</template>
