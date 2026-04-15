import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  ReplyStoreTemp,
  SuccessfulReplyEvent
} from '~/store/types/topic/reply'

export const useTempReplyStore = defineStore(
  'tempTopicReply',
  () => {
    const isEdit = ref<ReplyStoreTemp['isEdit']>(false)
    const isScrollToTop = ref<ReplyStoreTemp['isScrollToTop']>(false)
    const scrollToReplyId = ref<ReplyStoreTemp['scrollToReplyId']>(-1)
    const isReplyRewriting = ref<ReplyStoreTemp['isReplyRewriting']>(false)
    const replyRewrite = ref<ReplyStoreTemp['replyRewrite']>(null)
    const lastSuccessfulReply = ref<ReplyStoreTemp['lastSuccessfulReply']>(null)

    const setRewriteData = (reply: TopicReply) => {
      isReplyRewriting.value = true
      replyRewrite.value = {
        id: reply.id,
        mainContent: reply.contentMarkdown,
        targets: reply.targets.map((t) => ({
          targetReplyId: t.id,
          targetFloor: t.floor,
          targetUserName: t.user.name,
          content: t.replyContentMarkdown
        }))
      }
    }

    const resetRewriteReplyData = () => {
      replyRewrite.value = null
      isReplyRewriting.value = false
    }

    const setSuccessfulReply = (event: SuccessfulReplyEvent) => {
      lastSuccessfulReply.value = event
    }

    const clearSuccessfulReply = () => {
      lastSuccessfulReply.value = null
    }

    return {
      isEdit,
      isScrollToTop,
      scrollToReplyId,
      isReplyRewriting,
      replyRewrite,
      lastSuccessfulReply,
      setRewriteData,
      resetRewriteReplyData,
      setSuccessfulReply,
      clearSuccessfulReply
    }
  },
  {
    persist: false
  }
)
