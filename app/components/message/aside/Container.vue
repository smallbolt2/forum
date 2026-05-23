<script setup lang="ts">
import { kungalgameResponseHandler } from '~/utils/responseHandler'
import { asideItems } from './asideItemStore'
import type { ChatMessageAsideItem } from '~~/shared/types/chat-message'

const route = useRoute()

const { data: systemItems } = await useFetch<ChatMessageAsideItem[]>(
  '/api/message/nav/system',
  { ...kungalgameResponseHandler }
)

const { data: contactItems } = await useFetch<ChatMessageAsideItem[]>(
  '/api/message/nav/contact',
  { ...kungalgameResponseHandler }
)

watch(
  contactItems,
  (val) => {
    asideItems.value = val ?? []
  },
  { immediate: true }
)

const systemLinks = computed(() => {
  const items = systemItems.value ?? []
  return items.map((item) => ({
    item,
    href: `/message/${item.route}`,
    isActive: route.path === `/message/${item.route}`
  }))
})

const contactLinks = computed(() => {
  const items = contactItems.value ?? []
  return items.map((item) => ({
    item,
    href: `/message/user/${item.route}`,
    isActive: route.path === `/message/user/${item.route}`
  }))
})

const isIndexActive = computed(() => route.path === '/message')
</script>

<template>
  <aside
    class="border-default-200 flex h-full w-72 shrink-0 flex-col border-r md:w-80"
  >
    <header class="border-default-200 border-b p-4">
      <h1 class="text-lg font-semibold">消息</h1>
    </header>

    <div class="scrollbar-hide flex-1 space-y-1 overflow-y-auto p-2">
      <MessageAsideItem
        v-for="{ item, href, isActive } in systemLinks"
        :key="`sys-${item.route}`"
        :item="item"
        :href="href"
        :is-active="isActive"
      />

      <KunDivider v-if="contactLinks.length" class="my-2" />

      <MessageAsideItem
        v-for="{ item, href, isActive } in contactLinks"
        :key="`pm-${item.route}`"
        :item="item"
        :href="href"
        :is-active="isActive"
      />

      <KunNull
        v-if="!systemLinks.length && !contactLinks.length"
        description="暂无会话，通知会显示在「通知」里"
        :is-show-sticker="false"
        class="py-8"
      />
    </div>

    <div class="border-default-200 border-t p-2">
      <KunButton
        variant="light"
        class-name="w-full justify-start"
        href="/message"
        :color="isIndexActive ? 'secondary' : 'default'"
      >
        消息首页
      </KunButton>
    </div>
  </aside>
</template>
