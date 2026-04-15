<script setup lang="ts">
import { kungalgameResponseHandler } from '~/utils/responseHandler'

const route = useRoute()

const { showKUNGalgameHamburger, messageStatus } = storeToRefs(
  useTempSettingStore()
)
const { id, moemoepoint, isCheckIn } = storeToRefs(usePersistUserStore())
const { showKUNGalgameSidebarCollapsed } = storeToRefs(
  usePersistSettingsStore()
)

const { isSnowing, toggleSnow, startSnow } = useKunSnowEffect()

const router = useRouter()
const canGoBack = ref(false)
// const isShowUpdateAvatarModal = ref(false)

const updateCanGoBack = () => {
  canGoBack.value = window.history.length > 2
}

watch(
  () => route.name,
  () => {
    useTempSettingStore().reset()
  }
)

onMounted(async () => {
  const result = await $fetch('/api/user/status', {
    method: 'GET',
    ...kungalgameResponseHandler
  })
  if (result) {
    isCheckIn.value = result.isCheckIn
    moemoepoint.value = result.moemoepoints
    messageStatus.value = result.hasNewMessage ? 'new' : 'online'
  }

  // if (uid.value && !avatar.value) {
  //   isShowUpdateAvatarModal.value = true
  // }

  updateCanGoBack()

  startSnow()

  router.afterEach(() => {
    updateCanGoBack()
  })
})
</script>

<template>
  <div class="flex items-center gap-1">
    <KunTooltip
      :text="showKUNGalgameSidebarCollapsed ? '展开侧边栏' : '折叠侧边栏'"
      position="bottom"
    >
      <KunButton
        :is-icon-only="true"
        color="default"
        size="xl"
        variant="light"
        class-name="hidden md:flex"
        @click="
          showKUNGalgameSidebarCollapsed = !showKUNGalgameSidebarCollapsed
        "
      >
        <KunIcon
          :name="
            showKUNGalgameSidebarCollapsed
              ? 'lucide:panel-left-open'
              : 'lucide:panel-left-close'
          "
        />
      </KunButton>
    </KunTooltip>

    <KunButton
      :is-icon-only="true"
      color="default"
      size="xl"
      variant="light"
      @click="showKUNGalgameHamburger = true"
      class-name="flex sm:hidden"
    >
      <KunIcon name="lucide:menu" />
    </KunButton>

    <KunTooltip :text="canGoBack ? '返回上一页' : '返回主页'" position="bottom">
      <KunButton
        :is-icon-only="true"
        color="default"
        size="xl"
        variant="light"
        class-name="hidden sm:block mr-6"
        @click="canGoBack ? router.back() : navigateTo('/')"
      >
        <KunIcon :name="canGoBack ? 'lucide:arrow-left' : 'lucide:home'" />
      </KunButton>
    </KunTooltip>

    <KunTopBarSideCollapsed v-if="showKUNGalgameSidebarCollapsed" />

    <KunTooltip
      text="本网站完全开源"
      position="bottom"
      v-if="!id"
    >
      <KunButton
        :is-icon-only="true"
        variant="light"
        color="default"
        size="xl"
        target="_blank"
        :href="kungal.github"
        class-name="text-xl"
      >
        <KunIcon name="ant-design:github-filled" />
        <span class="text-sm sm:text-base">GitHub</span>
      </KunButton>
    </KunTooltip>


    <LazyKunTopBarHamburger />
  </div>
</template>
