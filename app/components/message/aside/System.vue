<script setup lang="ts">
import type { MessageSystemMessage } from '~~/shared/types/message'

const props = defineProps<{
  message: MessageSystemMessage
}>()

const { language } = storeToRefs(usePersistSettingsStore())

const text = computed(() => {
  const lang = (language.value || 'zh-cn') as keyof typeof props.message.content
  return props.message.content[lang] || props.message.content['zh-cn'] || ''
})
</script>

<template>
  <div
    class="border-default-200 flex flex-col gap-2 rounded-lg border p-3"
    :class="{ 'bg-default-100/60': message.status === 'unread' }"
  >
    <div class="flex items-center justify-between gap-2">
      <KunUser :user="message.admin" size="sm" />
      <span class="text-default-400 text-xs">
        {{ formatTimeDifference(message.created) }}
      </span>
    </div>
    <p class="text-default-600 whitespace-pre-wrap text-sm">{{ text }}</p>
  </div>
</template>
