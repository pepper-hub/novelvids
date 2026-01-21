<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores'

const { t } = useI18n()

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')

async function handleSubmit(): Promise<void> {
  if (!username.value || !password.value) {
    error.value = t('auth.fillAllFields')
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    await authStore.login(username.value, password.value)
    router.push('/dashboard')
  } catch (err) {
    error.value = t('auth.invalidCredentials')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center px-6">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <router-link to="/" class="inline-flex items-center gap-3 mb-6">
          <div class="w-12 h-12 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center">
            <span class="text-white font-bold text-lg">NV</span>
          </div>
          <span class="text-3xl font-bold text-white">NovelVids</span>
        </router-link>
        <h1 class="text-2xl font-semibold text-white">{{ t('auth.welcomeBack') }}</h1>
        <p class="text-gray-400 mt-2">{{ t('auth.welcomeMessage') }}</p>
      </div>

      <div class="card p-8 bg-gray-800/50 border-gray-700">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div v-if="error" class="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
            <p class="text-red-400 text-sm">{{ error }}</p>
          </div>

          <div>
            <label class="label text-gray-300">{{ t('auth.usernameOrEmail') }}</label>
            <input
              v-model="username"
              type="text"
              class="input bg-gray-700 border-gray-600 text-white"
              :placeholder="t('auth.enterUsername')"
            />
          </div>

          <div>
            <label class="label text-gray-300">{{ t('auth.password') }}</label>
            <input
              v-model="password"
              type="password"
              class="input bg-gray-700 border-gray-600 text-white"
              :placeholder="t('auth.enterPassword')"
            />
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="w-full btn-primary py-3"
          >
            <span v-if="isLoading">{{ t('auth.signingIn') }}</span>
            <span v-else>{{ t('auth.signIn') }}</span>
          </button>
        </form>

        <p class="mt-6 text-center text-gray-400">
          {{ t('auth.noAccount') }}
          <router-link to="/register" class="text-primary-400 hover:text-primary-300">
            {{ t('auth.signUp') }}
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>
