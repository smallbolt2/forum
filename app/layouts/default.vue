<script setup lang="ts">
import KunLayoutSidebar from '~/components/kun/layout/Sidebar.vue'
import KunTopBar from '~/components/kun/top-bar/TopBar.vue'
import {
  ENABLE_KUN_VISUAL_NOVEL_FORUM_WINTER_THEME,
  KUN_VISUAL_NOVEL_FORUM_WINTER_THEME_BACKGROUND
} from '~/config/theme'

const { showKUNGalgameBackground, showKUNGalgameBackLoli } = storeToRefs(
  usePersistSettingsStore()
)

const imageURL = ref(
  ENABLE_KUN_VISUAL_NOVEL_FORUM_WINTER_THEME
    ? KUN_VISUAL_NOVEL_FORUM_WINTER_THEME_BACKGROUND
    : ''
)

onMounted(async () => {
  imageURL.value = await usePersistSettingsStore().getCurrentBackground()
})

watch(
  () => showKUNGalgameBackground.value,
  async () => {
    imageURL.value = await usePersistSettingsStore().getCurrentBackground()
  }
)

const { showKUNGalgameSidebarCollapsed } = storeToRefs(
  usePersistSettingsStore()
)
</script>

<template>
  <div class="contents">
    <div class="bg-background fixed top-0 left-0 h-full w-full">
      <div
        class="fixed size-full bg-cover bg-fixed bg-center bg-no-repeat opacity-30 brightness-[var(--kun-background-brightness)]"
        :style="{ backgroundImage: `url(${imageURL})` }"
      />
    </div>

    <div class="hidden md:block">
      <KunLayoutSidebar />
    </div>

    <KunTopBar />

    <div class="bg-primary-50 flex min-h-dvh min-h-screen justify-center">
      <div
        :class="
          cn(
            // 原 max-w-7xl(1280px) 偏窄；与顶栏共用宽幅，大屏更接近鲲式三栏比例
            'z-10 w-full max-w-[min(100%,100rem)] min-w-0 transition-all duration-300 md:mr-3',
            showKUNGalgameSidebarCollapsed
              ? 'kun-main-ms-collapsed'
              : 'kun-main-ms-expanded'
          )
        "
      >
        <div class="h-full px-1 pt-19 pb-3 md:px-0">
          <NuxtPage />
        </div>

        <KunImage
          v-if="showKUNGalgameBackLoli"
          class="pointer-events-none fixed right-px bottom-px z-0 min-w-60 opacity-17! select-none"
          :src="
            ENABLE_KUN_VISUAL_NOVEL_FORUM_WINTER_THEME
              ? '/winter/sd.webp'
              : '/image/kohaku.webp'
          "
          loading="lazy"
          alt="kohaku"
        />
      </div>
    </div>
  </div>
</template>
