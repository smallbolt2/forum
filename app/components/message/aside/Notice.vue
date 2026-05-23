<script setup lang="ts">
import { getMessageI18n } from '../utils/getMessageI18n'
import { kungalgameResponseHandler } from '~/utils/responseHandler'
import type { Message } from '~~/shared/types/message'

const props = defineProps<{
  message: Message
  refresh: () => void
}>()

const handleDeleteMessage = async (messageId: number) => {
  const res = await useComponentMessageStore().alert(
    '您确定要删除这条消息吗？此操作不可撤销。'
  )
  if (!res) return

  const result = await $fetch(`/api/message/${messageId}`, {
    method: 'DELETE',
    query: { messageId },
    ...kungalgameResponseHandler
  })

  if (result) {
    props.refresh()
    useMessage(10106, 'success')
  }
}
</script>

<template>
  <div
    class="border-default-200 hover:bg-default-50 flex flex-col gap-2 rounded-lg border p-3 transition-colors"
    :class="{ 'bg-default-100/60': message.status === 'unread' }"
  >
    <div class="flex items-start justify-between gap-2">
      <KunLink :to="message.link" underline="none" color="default" class-name="min-w-0 flex-1">
        <KunUser :user="message.sender" :description="getMessageI18n(message)" size="sm" />
      </KunLink>
      <KunButton
        :is-icon-only="true"
        variant="light"
        color="danger"
        size="sm"
        @click="handleDeleteMessage(message.id)"
      >
        <KunIcon name="lucide:trash-2" />
      </KunButton>
    </div>
    <KunLink
      :to="message.link"
      underline="none"
      color="default"
      class-name="text-default-600 line-clamp-3 text-sm"
    >
      {{ markdownToText(message.content) }}
    </KunLink>
    <span class="text-default-400 text-xs">
      {{ formatDate(message.created, { isShowYear: true, isPrecise: true }) }}
    </span>
  </div>
</template>
