<script setup lang="ts">
import type { ChatMessage } from '~~/shared/types/chat-message'

defineProps<{
  message: ChatMessage
  isSent: boolean
}>()
</script>

<template>
  <div class="flex" :class="isSent ? 'justify-end' : 'justify-start'">
    <div
      class="max-w-[75%] rounded-2xl px-3 py-2 text-sm"
      :class="
        isSent
          ? 'bg-primary text-primary-foreground'
          : 'bg-default-100 text-foreground'
      "
    >
      <p class="whitespace-pre-wrap break-words">{{ message.content }}</p>
      <p class="mt-1 text-right text-xs opacity-70">
        {{ formatDate(message.created, { isPrecise: true }) }}
      </p>
    </div>
  </div>
</template>
