<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'

const authStore = useAuthStore()
const router = useRouter()

const sidebarOpen = ref(true)
const isAuthenticated = computed(() => authStore.isAuthenticated)

function toggleSidebar(): void {
  sidebarOpen.value = !sidebarOpen.value
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <template v-if="isAuthenticated">
      <AppSidebar :open="sidebarOpen" />
      <div
        :class="[
          'transition-all duration-300',
          sidebarOpen ? 'ml-64' : 'ml-16',
        ]"
      >
        <AppHeader @toggle-sidebar="toggleSidebar" />
        <main class="p-6">
          <slot />
        </main>
      </div>
    </template>
    <template v-else>
      <slot />
    </template>
  </div>
</template>
