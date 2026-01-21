<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ t('settings.title') }}</h1>
      <p class="text-gray-500 dark:text-gray-400 mt-1">{{ t('settings.general') }}</p>
    </div>

    <div class="grid lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <div class="card p-6">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('settings.account') }}</h2>
          <form class="space-y-4">
            <div>
              <label class="label">{{ t('auth.username') }}</label>
              <input type="text" class="input" :placeholder="t('auth.username')" />
            </div>
            <div>
              <label class="label">{{ t('auth.email') }}</label>
              <input type="email" class="input" :placeholder="t('auth.email')" />
            </div>
            <button type="submit" class="btn-primary">{{ t('settings.saveChanges') }}</button>
          </form>
        </div>

        <div class="card p-6">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('settings.comfyuiConfig') }}</h2>
          <form class="space-y-4">
            <div>
              <label class="label">{{ t('settings.apiUrl') }}</label>
              <input type="text" class="input" placeholder="http://localhost:8188" />
            </div>
            <div>
              <label class="label">{{ t('settings.apiKey') }} ({{ t('common.optional') }})</label>
              <input type="password" class="input" :placeholder="t('settings.apiKey')" />
            </div>
            <button type="submit" class="btn-primary">{{ t('settings.saveConfiguration') }}</button>
          </form>
        </div>
      </div>

      <div class="space-y-6">
        <div class="card p-6">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('settings.billing') }}</h2>
          <div class="space-y-4">
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('dashboard.stats.accountBalance') }}</p>
              <p class="text-3xl font-bold text-gray-900 dark:text-white">$0.00</p>
            </div>
            <button class="w-full btn-accent">{{ t('common.upload') }}</button>
          </div>
        </div>

        <div class="card p-6">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ t('settings.dangerZone') }}</h2>
          <button class="w-full btn bg-red-600 text-white hover:bg-red-700 focus:ring-red-500">
            {{ t('settings.deleteAccount') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
