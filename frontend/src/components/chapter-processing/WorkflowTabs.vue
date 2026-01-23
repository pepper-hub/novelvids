<script setup lang="ts">
/**
 * 处理工作流标签页
 * 支持：角色提取 -> 分镜处理 -> 视频生成
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { WorkflowStep } from '@/types'

interface Props {
  currentStep: WorkflowStep
  completedSteps: WorkflowStep[]
}

interface Emits {
  (e: 'change', step: WorkflowStep): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { t } = useI18n()

const tabs = computed(() => [
  { key: 'extraction' as WorkflowStep, label: t('chapterProcessing.workflow.extraction'), icon: 'users' },
  { key: 'storyboard' as WorkflowStep, label: t('chapterProcessing.workflow.storyboard'), icon: 'film' },
  { key: 'generation' as WorkflowStep, label: t('chapterProcessing.workflow.generation'), icon: 'play' },
])

function isCompleted(step: WorkflowStep): boolean {
  return props.completedSteps.includes(step)
}

function isActive(step: WorkflowStep): boolean {
  return props.currentStep === step
}

function canAccess(step: WorkflowStep): boolean {
  const stepIndex = tabs.value.findIndex((item) => item.key === step)
  if (stepIndex === 0) return true
  // 需要前一步完成才能访问
  const prevStep = tabs.value[stepIndex - 1]?.key
  return prevStep ? props.completedSteps.includes(prevStep) : false
}

function handleClick(step: WorkflowStep): void {
  if (canAccess(step)) {
    emit('change', step)
  }
}
</script>

<template>
  <div class="border-b border-gray-200 dark:border-gray-700">
    <nav class="flex gap-1 px-1" :aria-label="t('chapterProcessing.workflow.title')">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="handleClick(tab.key)"
        :disabled="!canAccess(tab.key)"
        :class="[
          'relative flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors duration-200',
          'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2',
          isActive(tab.key)
            ? 'text-primary-600 dark:text-primary-400'
            : canAccess(tab.key)
              ? 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 cursor-pointer'
              : 'text-gray-400 dark:text-gray-600 cursor-not-allowed',
        ]"
      >
        <!-- 图标 -->
        <svg
          v-if="tab.icon === 'users'"
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
          />
        </svg>
        <svg
          v-else-if="tab.icon === 'film'"
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"
          />
        </svg>
        <svg
          v-else-if="tab.icon === 'play'"
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
          />
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>

        <span>{{ tab.label }}</span>

        <!-- 完成标记 -->
        <svg
          v-if="isCompleted(tab.key)"
          class="w-4 h-4 text-green-500"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
            clip-rule="evenodd"
          />
        </svg>

        <!-- 活动指示器 -->
        <span
          v-if="isActive(tab.key)"
          class="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500 rounded-full"
        />
      </button>
    </nav>
  </div>
</template>
