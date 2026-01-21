<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex flex-col">
    <header class="container mx-auto px-6 py-6">
      <nav class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center">
            <span class="text-white font-bold">NV</span>
          </div>
          <span class="text-2xl font-bold text-white">{{ t('home.title') }}</span>
        </div>
        <div class="flex items-center gap-4">
          <router-link to="/login" class="px-4 py-2 text-gray-300 hover:text-white transition-colors">
            {{ t('home.login') }}
          </router-link>
          <router-link to="/register" class="btn-primary">
            {{ t('home.getStartedButton') }}
          </router-link>
        </div>
      </nav>
    </header>

    <main class="flex-1 container mx-auto px-6 py-20">
      <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
          {{ t('home.turnNovelsInto') }}
          <span class="bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">
            {{ t('home.stunningVideos') }}
          </span>
        </h1>
        <p class="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
          {{ t('home.platformDescription') }}
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <router-link to="/register" class="btn-primary text-lg px-8 py-3">
            {{ t('home.getStartedButton') }}
          </router-link>
          <button class="btn-secondary text-lg px-8 py-3">
            {{ t('home.watchDemo') }}
          </button>
        </div>
      </div>

      <div class="mt-32 grid md:grid-cols-3 gap-8">
        <div class="card p-8 bg-gray-800/50 border-gray-700">
          <div class="w-12 h-12 bg-primary-500/20 rounded-lg flex items-center justify-center mb-4">
            <svg class="w-6 h-6 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-white mb-2">{{ t('home.featureCards.characterExtraction.title') }}</h3>
          <p class="text-gray-400">
            {{ t('home.featureCards.characterExtraction.description') }}
          </p>
        </div>

        <div class="card p-8 bg-gray-800/50 border-gray-700">
          <div class="w-12 h-12 bg-accent-500/20 rounded-lg flex items-center justify-center mb-4">
            <svg class="w-6 h-6 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-white mb-2">{{ t('home.featureCards.sceneGeneration.title') }}</h3>
          <p class="text-gray-400">
            {{ t('home.featureCards.sceneGeneration.description') }}
          </p>
        </div>

        <div class="card p-8 bg-gray-800/50 border-gray-700">
          <div class="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mb-4">
            <svg class="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-white mb-2">{{ t('home.featureCards.voiceSynthesis.title') }}</h3>
          <p class="text-gray-400">
            {{ t('home.featureCards.voiceSynthesis.description') }}
          </p>
        </div>
      </div>
    </main>

    <footer class="container mx-auto px-6 py-8 border-t border-gray-800">
      <p class="text-center text-gray-500">
        {{ t('home.footer.copyright') }}
      </p>
    </footer>
  </div>
</template>
