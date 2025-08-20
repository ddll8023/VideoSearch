<script setup>
import AppHeader from '@/components/system/AppHeader.vue'
</script>

<template>
  <div class="app-layout">
    <AppHeader />

    <!-- 主内容区域 -->
    <main class="app-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-content {
  flex: 1;
  overflow: auto;
  background-color: var(--bg-secondary);
  padding-top: var(--header-height);
  /* 为固定的顶部导航栏预留空间 */
}
</style>
