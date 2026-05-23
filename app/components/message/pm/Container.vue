<script setup lang="ts">
import { kungalgameResponseHandler } from '~/utils/responseHandler'
import type { ChatMessage } from '~~/shared/types/chat-message'

const props = defineProps<{
  userId: number
}>()

const historyContainer = ref<HTMLElement | null>(null)
const messageInput = ref('')
const messages = ref<ChatMessage[]>([])
const isLoadHistoryMessageComplete = ref(false)
const isSending = ref(false)
const currentUserId = usePersistUserStore().id

const isShowLoader = computed(() => {
  if (isLoadHistoryMessageComplete.value) return false
  if (messages.value.length < 30) return false
  return true
})

const pageData = reactive({ page: 1, limit: 30 })

const scrollToBottom = () => {
  historyContainer.value?.scrollTo({
    top: historyContainer.value.scrollHeight,
    behavior: 'smooth'
  })
}

const getMessageHistory = async () => {
  const histories = await $fetch<ChatMessage[]>('/api/message/chat/history', {
    method: 'GET',
    query: {
      receiverUid: props.userId,
      page: pageData.page,
      limit: pageData.limit
    },
    ...kungalgameResponseHandler
  })
  return Array.isArray(histories) ? histories : []
}

const sendMessage = async () => {
  if (!messageInput.value.trim()) {
    useMessage(10401, 'warn')
    return
  }
  if (messageInput.value.length > 1007) {
    useMessage(10402, 'warn')
    return
  }

  isSending.value = true
  try {
    const result = await $fetch('/api/message/chat/send', {
      method: 'POST',
      body: { receiverUid: props.userId, content: messageInput.value },
      ...kungalgameResponseHandler
    })
    if (result) {
      messageInput.value = ''
      pageData.page = 1
      messages.value = await getMessageHistory()
      await nextTick()
      scrollToBottom()
    }
  } finally {
    isSending.value = false
  }
}

const handleLoadHistoryMessages = async () => {
  if (!historyContainer.value) return
  const previousScrollHeight = historyContainer.value.scrollHeight
  const previousScrollTop = historyContainer.value.scrollTop
  pageData.page += 1
  const histories = await getMessageHistory()
  if (histories.length > 0) {
    messages.value.unshift(...histories)
    await nextTick()
    if (historyContainer.value) {
      const newScrollHeight = historyContainer.value.scrollHeight
      historyContainer.value.scrollTop =
        previousScrollTop + (newScrollHeight - previousScrollHeight)
    }
  } else {
    isLoadHistoryMessageComplete.value = true
  }
}

const onKeydown = async (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    await sendMessage()
  }
}

onMounted(async () => {
  messages.value = await getMessageHistory()
  window.addEventListener('keydown', onKeydown)
  await nextTick()
  scrollToBottom()
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <div class="flex h-[calc(100%-3rem)] flex-col gap-3">
    <div
      v-if="isShowLoader"
      class="flex justify-center"
    >
      <KunButton variant="light" size="sm" @click="handleLoadHistoryMessages">
        加载更多
      </KunButton>
    </div>

    <div
      ref="historyContainer"
      class="scrollbar-hide flex flex-1 flex-col gap-3 overflow-y-auto pr-2"
    >
      <MessagePmItem
        v-for="message in messages"
        :key="message.id"
        :message="message"
        :is-sent="message.sender.id === currentUserId"
      />
      <KunNull
        v-if="!messages.length"
        description="暂无消息，发送一条消息开始聊天吧"
        :is-show-sticker="false"
      />
    </div>

    <div class="flex items-end gap-2 border-t pt-3">
      <KunTextarea
        v-model="messageInput"
        placeholder="输入消息，Enter 发送"
        class="flex-1"
        :rows="2"
      />
      <KunButton
        color="primary"
        :is-loading="isSending"
        @click="sendMessage"
      >
        发送
      </KunButton>
    </div>
  </div>
</template>
