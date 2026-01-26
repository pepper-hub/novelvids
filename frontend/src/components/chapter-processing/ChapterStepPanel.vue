<script setup lang="ts">
/**
 * 章节步骤面板
 * 显示选中章节的工作流步骤，支持逐步处理
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Chapter, ChapterWorkflowStatus } from '@/types'

interface Props {
  chapter: Chapter | null
  isProcessing?: boolean
  processingMessage?: string
}

interface Emits {
  (e: 'extract-characters', chapterId: string): void
  (e: 'create-storyboard', chapterId: string): void
  (e: 'generate-video', chapterId: string): void
}

const props = withDefaults(defineProps<Props>(), {
  isProcessing: false,
  processingMessage: '',
})
const emit = defineEmits<Emits>()
const { t } = useI18n()

interface Step {
  id: number
  key: string
  status: 'completed' | 'current' | 'pending' | 'disabled'
  canAction: boolean
}

const steps = computed<Step[]>(() => {
  if (!props.chapter) return []

  const status = props.chapter.workflowStatus
  const statusOrder: ChapterWorkflowStatus[] = [
    'pending',
    'characters_extracted',
    'storyboard_ready',
    'generating',
    'completed',
  ]
  const currentIndex = statusOrder.indexOf(status)

  return [
    {
      id: 1,
      key: 'extractCharacters',
      status: getStepStatus(0, currentIndex, status),
      canAction: status === 'pending',
    },
    {
      id: 2,
      key: 'createStoryboard',
      status: getStepStatus(1, currentIndex, status),
      canAction: status === 'characters_extracted',
    },
    {
      id: 3,
      key: 'generateVideo',
      status: getStepStatus(2, currentIndex, status),
      canAction: status === 'storyboard_ready',
    },
  ]
})

function getStepStatus(
  stepIndex: number,
  currentIndex: number,
  workflowStatus: ChapterWorkflowStatus
): Step['status'] {
  // 完成态：workflow 状态已过这个步骤
  if (stepIndex < currentIndex) return 'completed'
  // 当前步骤
  if (stepIndex === currentIndex) {
    if (workflowStatus === 'completed') return 'completed'
    if (workflowStatus === 'generating' && stepIndex === 2) return 'current'
    return 'current'
  }
  // 未来步骤
  return 'pending'
}

function handleAction(step: Step): void {
  if (!props.chapter || !step.canAction || props.isProcessing) return

  switch (step.key) {
    case 'extractCharacters':
      emit('extract-characters', props.chapter.id)
      break
    case 'createStoryboard':
      emit('create-storyboard', props.chapter.id)
      break
    case 'generateVideo':
      emit('generate-video', props.chapter.id)
      break
  }
}
</script>

<template>
  <div class="h-full flex flex-col">
    <!-- 空状态：未选择章节 -->
    <div
      v-if="!chapter"
      class="flex-1 flex items-center justify-center"
    >
      <div class="text-center">
        <svg
          class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-white">
          {{ t('chapterProcessing.stepPanel.noSelection') }}
        </h3>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
          {{ t('chapterProcessing.stepPanel.selectHint') }}
        </p>
      </div>
    </div>

    <!-- 已选择章节：显示步骤 -->
    <template v-else>
      <!-- 章节标题 -->
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <span>{{ t('chapterProcessing.stepPanel.chapterNumber', { number: chapter.number }) }}</span>
        </div>
        <h2 class="mt-1 text-xl font-semibold text-gray-900 dark:text-white">
          {{ chapter.title }}
        </h2>
      </div>

      <!-- 步骤列表 -->
      <div class="flex-1 p-6 space-y-4 overflow-y-auto">
        <div
          v-for="(step, index) in steps"
          :key="step.id"
          class="relative"
        >
          <!-- 连接线 -->
          <div
            v-if="index < steps.length - 1"
            class="absolute left-5 top-12 w-0.5 h-8"
            :class="step.status === 'completed' ? 'bg-green-500' : 'bg-gray-200 dark:bg-gray-700'"
          />

          <!-- 步骤卡片 -->
          <div
            class="relative p-4 rounded-lg border transition-all"
            :class="{
              'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800': step.status === 'completed',
              'bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-700 ring-2 ring-primary-500/20': step.status === 'current',
              'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700': step.status === 'pending',
            }"
          >
            <div class="flex items-start gap-4">
              <!-- 步骤图标 -->
              <div
                class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center"
                :class="{
                  'bg-green-500 text-white': step.status === 'completed',
                  'bg-primary-500 text-white': step.status === 'current',
                  'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400': step.status === 'pending',
                }"
              >
                <svg v-if="step.status === 'completed'" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span v-else class="text-sm font-semibold">{{ step.id }}</span>
              </div>

              <!-- 步骤内容 -->
              <div class="flex-1 min-w-0">
                <h4 class="text-base font-medium text-gray-900 dark:text-white">
                  {{ t(`chapterProcessing.stepPanel.steps.${step.key}.title`) }}
                </h4>
                <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  {{ t(`chapterProcessing.stepPanel.steps.${step.key}.description`) }}
                </p>

                <!-- 操作按钮 -->
                <div v-if="step.canAction" class="mt-3">
                  <button
                    @click="handleAction(step)"
                    :disabled="isProcessing"
                    class="btn-primary text-sm flex items-center gap-2"
                  >
                    <svg
                      v-if="isProcessing"
                      class="w-4 h-4 animate-spin"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    {{ t(`chapterProcessing.stepPanel.steps.${step.key}.action`) }}
                  </button>
                </div>

                <!-- 处理中消息 -->
                <div v-if="isProcessing && step.status === 'current'" class="mt-3">
                  <p class="text-sm text-primary-600 dark:text-primary-400 flex items-center gap-2">
                    <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    {{ processingMessage || t('chapterProcessing.stepPanel.processing') }}
                  </p>
                </div>

                <!-- 完成状态 -->
                <div v-if="step.status === 'completed'" class="mt-2">
                  <span class="text-sm text-green-600 dark:text-green-400 flex items-center gap-1">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                    {{ t('chapterProcessing.stepPanel.completed') }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
