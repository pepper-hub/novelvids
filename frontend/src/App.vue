<script setup lang="ts">
import AppLayout from './components/layout/AppLayout.vue'
import ToastContainer from './components/common/ToastContainer.vue'
</script>

<template>
  <AppLayout>
    <router-view />
  </AppLayout>
  <ToastContainer />
</template>
