from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "app" / "components" / "message"

SYSTEM = """<script setup lang="ts">
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
  <motion.div
    class="border-default-200 flex flex-col gap-2 rounded-lg border p-3"
    :class="{ 'bg-default-100/60': message.status === 'unread' }"
  >
    <motion.div class="flex items-center justify-between gap-2">
      <KunUser :user="message.admin" size="sm" />
      <span class="text-default-400 text-xs">
        {{ formatTimeDifference(message.created) }}
      </span>
    </motion.div>
    <p class="text-default-600 whitespace-pre-wrap text-sm">{{ text }}</p>
  </motion.div>
</template>
"""

PM_HEADER = """<script setup lang="ts">
import { kungalgameResponseHandler } from '~/utils/responseHandler'

const props = defineProps<{
  id: number
}>()

const { data: user } = await useFetch<{ name: string; avatar: string }>(
  `/api/user/${props.id}`,
  {
    method: 'GET',
    query: { userId: props.id },
    ...kungalgameResponseHandler
  }
)
</script>

<template>
  <header class="border-default-200 flex items-center gap-3 border-b pb-3">
    <KunAvatar
      :user="{
        id: props.id,
        name: user?.name || '',
        avatar: user?.avatar || ''
      }"
      size="md"
    />
    <div>
      <p class="font-medium">{{ user?.name || '加载中...' }}</p>
      <p class="text-default-500 text-xs">私信</p>
    </motion.div>
  </header>
</template>
"""

PM_ITEM = """<script setup lang="ts">
import type { ChatMessage } from '~~/shared/types/chat-message'

defineProps<{
  message: ChatMessage
  isSent: boolean
}>()
</script>

<template>
  <motion.div class="flex" :class="isSent ? 'justify-end' : 'justify-start'">
    <motion.div
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
    </motion.div>
  </motion.div>
</template>
"""

PM_CONTAINER = """<script setup lang="ts">
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
  <motion.div class="flex h-[calc(100%-3rem)] flex-col gap-3">
    <motion.div
      v-if="isShowLoader"
      class="flex justify-center"
    >
      <KunButton variant="light" size="sm" @click="handleLoadHistoryMessages">
        加载更多
      </KunButton>
    </motion.div>

    <motion.div
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
    </motion.div>

    <motion.div class="flex items-end gap-2 border-t pt-3">
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
    </motion.div>
  </motion.div>
</template>
"""

NOTICE = """<template>
  <motion.div class="text-default-600 flex h-full flex-col gap-3 p-4 text-sm">
    <p class="text-lg font-semibold">提示</p>
    <p>本消息系统尚在开发中，但是功能应该足够用。</p>
    <p>
      如果您有任何问题，请查看这个话题：
      <KunLink to="/topic/1" color="primary">[公告] 有关论坛消息系统的说明</KunLink>
    </p>
    <p>
      本论坛依旧是完全开源的，如果您觉得不错，可以给我们的 GitHub 项目点一个 star：
      <KunLink
        href="https://github.com/KUN1007/kun-galgame-nuxt4"
        target="_blank"
        color="primary"
      >
        kun-galgame-nuxt4
      </KunLink>
    </p>
  </motion.div>
</template>
"""

ASIDE_NOTICE = """<script setup lang="ts">
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
  <motion.div
    class="border-default-200 hover:bg-default-50 flex flex-col gap-2 rounded-lg border p-3 transition-colors"
    :class="{ 'bg-default-100/60': message.status === 'unread' }"
  >
    <motion.div class="flex items-start justify-between gap-2">
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
    </motion.div>
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
  </motion.div>
</template>
"""


def fix_divs(text: str) -> str:
  return text.replace("<motion.div", "<div").replace("</motion.div>", "</div>")


files = {
  ROOT / "aside" / "System.vue": fix_divs(SYSTEM),
  ROOT / "pm" / "Header.vue": fix_divs(PM_HEADER),
  ROOT / "pm" / "Item.vue": fix_divs(PM_ITEM),
  ROOT / "pm" / "Container.vue": fix_divs(PM_CONTAINER),
  ROOT / "Notice.vue": fix_divs(NOTICE),
  ROOT / "aside" / "Notice.vue": fix_divs(ASIDE_NOTICE),
}

for path, content in files.items():
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(content, encoding="utf-8", newline="\n")
  print("wrote", path)
