import { render } from 'vue'
import MessageContainer from '~/components/kun/alert/MessageContainer.vue'
import { infoMessages } from '~/error/kunMessage'

export type KunMessageType = 'warn' | 'success' | 'error' | 'info'
export type KunMessagePosition =
  | 'top-center'
  | 'top-left'
  | 'top-right'
  | 'bottom-center'
  | 'bottom-left'
  | 'bottom-right'

export interface KunMessageOptions {
  id: string
  message: string
  type: KunMessageType
  duration: number
  richText: boolean
  position: KunMessagePosition
  count: number
}

const messages: Ref<KunMessageOptions[]> = ref([])
let seed = 0
let containerRef: HTMLElement | null = null

export const useMessageState = () => ({
  messages: computed(() => messages.value),
  removeMessage: (id: string) => {
    messages.value = messages.value.filter((msg) => msg.id !== id)
  }
})

const initializeContainer = () => {
  if (containerRef) return

  containerRef = document.createElement('div')
  containerRef.id = 'kun-message-container-root'
  document.body.appendChild(containerRef)

  const vNode = h(MessageContainer)
  render(vNode, containerRef)
}

export const useMessage = (
  messageData: number | string,
  type: KunMessageType,
  duration = 3000,
  richText = false,
  position = 'top-center' as KunMessagePosition
) => {
  initializeContainer()

  const resolvedMessage =
    typeof messageData === 'string'
      ? messageData
      : (infoMessages[messageData] ?? '')

  const existingMessage = messages.value.find(
    (m) =>
      m.message === resolvedMessage &&
      m.position === position &&
      m.type === type
  )

  if (existingMessage) {
    existingMessage.count++
    existingMessage.duration = duration
  } else {
    seed++
    const id = `message_${seed}`

    const newMessage: KunMessageOptions = {
      id,
      message: resolvedMessage,
      type,
      duration,
      richText,
      position,
      count: 1
    }

    if (position.startsWith('top')) {
      messages.value.push(newMessage)
    } else {
      messages.value.unshift(newMessage)
    }
  }
}
