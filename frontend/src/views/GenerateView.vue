<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const prompt = ref('')
const negativePrompt = ref('')
const width = ref(1024)
const height = ref(576)
const isGenerating = ref(false)
const generatedImage = ref<string | null>(null)

async function handleGenerate(): Promise<void> {
  if (!prompt.value) return

  isGenerating.value = true
  generatedImage.value = null

  try {
    const response = await fetch('/api/v1/generate/image', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: JSON.stringify({
        prompt: prompt.value,
        negative_prompt: negativePrompt.value,
        width: width.value,
        height: height.value,
      }),
    })

    if (response.ok) {
      const data = await response.json()
      generatedImage.value = data.image_url
    }
  } finally {
    isGenerating.value = false
  }
}
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ t('generate.title') }}</h1>
      <p class="text-gray-500 dark:text-gray-400 mt-1">{{ t('generate.options') }}</p>
    </div>

    <div class="grid lg:grid-cols-2 gap-6">
      <div class="card p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('generate.imageSettings') }}</h2>
        <form @submit.prevent="handleGenerate" class="space-y-4">
          <div>
            <label class="label">{{ t('generate.prompt') }}</label>
            <textarea
              v-model="prompt"
              class="input min-h-[100px]"
              :placeholder="t('generate.promptPlaceholder')"
              required
            ></textarea>
          </div>

          <div>
            <label class="label">{{ t('generate.negativePrompt') }} ({{ t('common.optional') }})</label>
            <textarea
              v-model="negativePrompt"
              class="input min-h-[60px]"
              :placeholder="t('generate.negativePromptPlaceholder')"
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label">{{ t('generate.resolution') }}</label>
              <input v-model.number="width" type="number" class="input" min="256" max="2048" step="64" />
            </div>
            <div>
              <label class="label">{{ t('generate.resolution') }}</label>
              <input v-model.number="height" type="number" class="input" min="256" max="2048" step="64" />
            </div>
          </div>

          <button
            type="submit"
            :disabled="isGenerating || !prompt"
            class="w-full btn-primary py-3"
          >
            <span v-if="isGenerating" class="flex items-center justify-center gap-2">
              <div class="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
              {{ t('generate.generationInProgress') }}
            </span>
            <span v-else>{{ t('generate.startGeneration') }}</span>
          </button>
        </form>
      </div>

      <div class="card p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('common.view') }}</h2>
        <div
          v-if="generatedImage"
          class="aspect-video bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden"
        >
          <img :src="generatedImage" :alt="t('generate.generatedImage')" class="w-full h-full object-contain" />
        </div>
        <div
          v-else
          class="aspect-video bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center"
        >
          <div class="text-center text-gray-400">
            <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p>{{ t('common.noData') }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
