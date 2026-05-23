<script setup lang="ts">
import type { ChatMessageAsideItem } from '~~/shared/types/chat-message'

const props = defineProps<{
  item: ChatMessageAsideItem
  href: string
  isActive?: boolean
}>()
</script>

<template>
  <KunLink
    :to="href"
    underline="none"
    color="default"
    :class-name="
      cn(
        'hover:bg-default-100 flex items-center gap-3 rounded-lg p-3 transition-colors',
        isActive && 'bg-default-100'
      )
    "
  >
    <KunAvatar
      :user="{ id: 0, name: item.title, avatar: item.avatar }"
      size="md"
    />
    <div class="min-w-0 flex-1">
      <div class="flex items-center justify-between gap-2">
        <span class="truncate font-medium">{{ item.title }}</span>
        <span
          v-if="item.unreadCount"
          class="bg-secondary-500 shrink-0 rounded-full px-2 py-0.5 text-xs text-white"
        >
          {{ item.unreadCount }}
        </span>
      </div>
      <p class="text-default-500 truncate text-xs">
        {{ item.content || '暂无消息' }}
      </p>
      <p
        v-if="item.lastMessageTime"
        class="text-default-400 mt-1 text-xs"
      >
        {{ formatTimeDifference(item.lastMessageTime) }}
      </p>
    </div>
  </KunLink>
</template>
