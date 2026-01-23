<script setup lang="ts">
/**
 * Prompt 查看模态框
 * 显示角色的完整图像生成 prompt
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { CharacterAsset } from '@/types'

interface Props {
  show: boolean
  asset: CharacterAsset | null
  prompt?: string
}

interface Emits {
  (e: 'update:show', value: boolean): void
  (e: 'copy', prompt: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { t } = useI18n()

const isVisible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value),
})

const generatedPrompt = computed(() => {
  if (!props.asset) return ''
  if (props.prompt) return props.prompt

  // 生成默认 prompt
  const parts: string[] = []
  if (props.asset.baseTraits) {
    parts.push(`(Base: ${props.asset.baseTraits})`)
  } else {
    parts.push('(Base: Unknown Appearance)')
  }

  const latestState = props.asset.visualStates[props.asset.visualStates.length - 1]
  if (latestState?.currentState) {
    parts.push(latestState.currentState)
  }

  return parts.join(', ')
})

function handleCopy(): void {
  if (generatedPrompt.value) {
    navigator.clipboard.writeText(generatedPrompt.value)
    emit('copy', generatedPrompt.value)
  }
}

function close(): void {
  isVisible.value = false
}
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isVisible"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <!-- 背景遮罩 -->
        <div
          class="absolute inset-0 bg-black/50 backdrop-blur-sm"
          @click="close"
        />

        <!-- 模态框内容 -->
        <Transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div
            v-if="isVisible && asset"
            class="relative w-full max-w-lg bg-white dark:bg-gray-800 rounded-xl shadow-2xl"
          >
            <!-- 头部 -->
            <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <div class="flex items-center gap-3">
                <div
                  class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400"
                >
                  {{ asset.canonicalName.charAt(0) }}
                </div>
                <div>
                  <h3 class="font-semibold text-gray-900 dark:text-white">
                    {{ asset.canonicalName }}
                  </h3>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    {{ t('chapterProcessing.prompts.title') }}
                  </p>
                </div>
              </div>
              <button
                @click="close"
                class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            <!-- 内容 -->
            <div class="p-4 space-y-4">
              <!-- Prompt 显示 -->
              <div>
                <label class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                  {{ t('chapterProcessing.prompts.fullPrompt') }}
                </label>
                <div
                  class="mt-2 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 font-mono text-sm text-gray-700 dark:text-gray-300 max-h-48 overflow-y-auto"
                >
                  {{ generatedPrompt }}
                </div>
              </div>

              <!-- 视觉状态历史 -->
              <div v-if="asset.visualStates.length > 0">
                <label class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                  {{ t('chapterProcessing.prompts.stateHistory', { count: asset.visualStates.length }) }}
                </label>
                <div class="mt-2 space-y-2 max-h-32 overflow-y-auto">
                  <div
                    v-for="state in asset.visualStates"
                    :key="state.chapterNumber"
                    class="p-2 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-700"
                  >
                    <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
                      <span>{{ t('chapterProcessing.prompts.chapterNumber', { chapter: state.chapterNumber }) }}</span>
                      <span>{{ t('chapterProcessing.prompts.aliasUsed', { alias: state.aliasUsed }) }}</span>
                    </div>
                    <p class="text-xs text-gray-600 dark:text-gray-400 font-mono truncate">
                      {{ state.currentState }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 底部操作 -->
            <div class="flex gap-3 p-4 border-t border-gray-200 dark:border-gray-700">
              <button
                @click="close"
                class="flex-1 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
              >
                {{ t('chapterProcessing.prompts.close') }}
              </button>
              <button
                @click="handleCopy"
                class="flex-1 px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                  />
                </svg>
                {{ t('chapterProcessing.prompts.copyPrompt') }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>
