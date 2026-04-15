import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'
import type { ReplyStorePersist } from '~/store/types/topic/reply'

export const usePersistKUNGalgameReplyStore = defineStore(
  'KUNGalgameTopicReply',
  () => {
    const mode = ref<ReplyStorePersist['mode']>('preview')
    const replyDraft = reactive<ReplyStorePersist['replyDraft']>({
      targets: [],
      mainContent: ''
    })

    const addTarget = (target: {
      targetReplyId: number
      targetFloor: number
      targetUserName: string
    }) => {
      if (
        replyDraft.targets.some((t) => t.targetReplyId === target.targetReplyId)
      ) {
        return
      }
      if (replyDraft.targets.length >= 10) {
        useMessage('???????? 10 ???', 'warn')
        return
      }

      replyDraft.targets.push({
        ...target,
        content: ''
      })
    }

    const removeTarget = (targetReplyId: number) => {
      replyDraft.targets = replyDraft.targets.filter(
        (t) => t.targetReplyId !== targetReplyId
      )
    }

    const resetReplyDraft = () => {
      replyDraft.targets = []
      replyDraft.mainContent = ''
    }

    const resetReplyContent = () => {
      replyDraft.targets.forEach((t) => (t.content = ''))
      replyDraft.mainContent = ''
    }

    return {
      mode,
      replyDraft,
      addTarget,
      removeTarget,
      resetReplyDraft,
      resetReplyContent
    }
  },
  {
    persist: true
  }
)
