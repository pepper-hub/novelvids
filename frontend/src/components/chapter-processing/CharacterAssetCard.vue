<script setup lang="ts">
/**
 * 角色资产卡片
 * 展示单个角色的固有属性、别名和视觉状态
 */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { CharacterAsset } from '@/types'

interface Props {
  asset: CharacterAsset
}

interface Emits {
  (e: 'edit', asset: CharacterAsset): void
  (e: 'view-prompt', asset: CharacterAsset): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { t } = useI18n()

const isExpanded = ref(false)

const latestState = computed(() => {
  const states = props.asset.visualStates
  return states.length > 0 ? states[states.length - 1] : null
})

const aliasText = computed(() => {
  const aliases = props.asset.aliases.filter((a) => a !== props.asset.canonicalName)
  return aliases.length > 0 ? aliases.join('、') : t('chapterProcessing.assets.noAliases')
})

function toggleExpand(): void {
  isExpanded.value = !isExpanded.value
}
</script>

<template>
  <div
    class="group bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden transition-shadow duration-200 hover:shadow-md cursor-pointer"
    @click="toggleExpand"
  >
    <!-- 卡片头部 -->
    <div class="p-4">
      <div class="flex items-start justify-between">
        <div class="flex items-center gap-3">
          <!-- 角色头像占位 -->
          <div
            class="w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold"
            :class="[
              asset.characterType === 'Person'
                ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
                : 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400',
            ]"
          >
            {{ asset.canonicalName.charAt(0) }}
          </div>
          <div>
            <h4 class="font-semibold text-gray-900 dark:text-white">
              {{ asset.canonicalName }}
            </h4>
                <p class="text-xs text-gray-500 dark:text-gray-400">
                  {{ asset.characterType === 'Person' ? t('chapterProcessing.assets.person') : t('chapterProcessing.assets.object') }}
                  · {{ t('chapterProcessing.assets.updatedAtChapter', { chapter: asset.lastUpdatedChapter }) }}
                </p>
          </div>
        </div>

        <!-- 展开指示器 -->
        <svg
          class="w-5 h-5 text-gray-400 transition-transform duration-200"
          :class="{ 'rotate-180': isExpanded }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </div>

      <!-- 别名标签 -->
      <div v-if="asset.aliases.length > 1" class="mt-3 flex flex-wrap gap-1">
        <span
          v-for="alias in asset.aliases.slice(0, 3)"
          :key="alias"
          class="px-2 py-0.5 text-xs rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
        >
          {{ alias }}
        </span>
        <span
          v-if="asset.aliases.length > 3"
          class="px-2 py-0.5 text-xs rounded-full bg-gray-100 dark:bg-gray-700 text-gray-500"
        >
          +{{ asset.aliases.length - 3 }}
        </span>
      </div>
    </div>

    <!-- 展开内容 -->
    <div
      v-show="isExpanded"
      class="border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50"
    >
      <!-- 固有属性 -->
      <div class="p-4 space-y-3">
        <div>
          <label class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
            {{ t('chapterProcessing.assets.baseTraits') }}
          </label>
          <p
            class="mt-1 text-sm text-gray-700 dark:text-gray-300 font-mono bg-white dark:bg-gray-900 p-2 rounded border border-gray-200 dark:border-gray-700"
          >
            {{ asset.baseTraits || t('chapterProcessing.assets.noDescription') }}
          </p>
        </div>

        <!-- 最新视觉状态 -->
        <div v-if="latestState">
          <label class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
            {{ t('chapterProcessing.assets.latestState', { chapter: latestState.chapterNumber }) }}
          </label>
          <p
            class="mt-1 text-sm text-gray-700 dark:text-gray-300 font-mono bg-white dark:bg-gray-900 p-2 rounded border border-gray-200 dark:border-gray-700"
          >
            {{ latestState.currentState }}
          </p>
        </div>

        <!-- 所有别名 -->
        <div v-if="asset.aliases.length > 0">
          <label class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
            {{ t('chapterProcessing.assets.allAliases') }}
          </label>
          <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
            {{ aliasText }}
          </p>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="px-4 pb-4 flex gap-2">
        <button
          @click.stop="emit('edit', asset)"
          class="flex-1 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
        >
          {{ t('chapterProcessing.assets.edit') }}
        </button>
        <button
          @click.stop="emit('view-prompt', asset)"
          class="flex-1 px-3 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors"
        >
          {{ t('chapterProcessing.assets.viewPrompt') }}
        </button>
      </div>
    </div>
  </div>
</template>
