<script setup lang="ts">
import { kungalgameResponseHandler } from '~/utils/responseHandler'

const props = defineProps<{
  topicId?: number
  replyId?: number
  targetUserId: number
  dislikeCount: number
  isDisliked: boolean
  isLiked: boolean
}>()

const emits = defineEmits<{
  (event: 'updateDislike', payload: { isDisliked: boolean; dislikeCount: number }): void
}>()

const { id } = usePersistUserStore()
const isLiked = ref(props.isLiked)
const isDisliked = ref(props.isDisliked)
const dislikeCount = ref(props.dislikeCount)
const isDislikePending = ref(false)

watch(
  () => props.isLiked,
  (value) => {
    isLiked.value = value
  }
)

watch(
  () => props.isDisliked,
  (value) => {
    isDisliked.value = value
  }
)

watch(
  () => props.dislikeCount,
  (value) => {
    dislikeCount.value = value
  }
)

const toggleDislike = async () => {
  if (isDislikePending.value) {
    return
  }

  isDislikePending.value = true
  const wasDisliked = isDisliked.value
  let res: string | { isDisliked: boolean; dislikeCount: number } = ''

  try {
    if (props.replyId) {
      const result = await $fetch(`/api/topic/${props.topicId}/reply/dislike`, {
        method: 'PUT',
        body: { replyId: props.replyId },
        watch: false,
        ...kungalgameResponseHandler
      })
      res = result ?? ''
    } else if (props.topicId) {
      const result = await $fetch(`/api/topic/${props.topicId}/dislike`, {
        method: 'PUT',
        watch: false,
        body: { topicId: props.topicId },
        ...kungalgameResponseHandler
      })
      res = result ?? ''
    }

    if (res) {
      if (typeof res === 'object' && res !== null && 'isDisliked' in res && 'dislikeCount' in res) {
        isDisliked.value = res.isDisliked
        dislikeCount.value = res.dislikeCount
      } else {
        dislikeCount.value += wasDisliked ? -1 : 1
        isDisliked.value = !wasDisliked
      }

      if (isDisliked.value) {
        isLiked.value = false
      }

      emits('updateDislike', {
        isDisliked: isDisliked.value,
        dislikeCount: dislikeCount.value
      })

      useMessage(wasDisliked ? 10226 : 10225, 'success')
    }
  } finally {
    isDislikePending.value = false
  }
}

const handleClickDislikeThrottled = throttle(toggleDislike, 1007, () =>
  useMessage(10227, 'warn')
)

const handleClickDislike = () => {
  if (!id) {
    useMessage(10228, 'warn', 5000)
    return
  }
  if (id === props.targetUserId) {
    useMessage(10229, 'warn')
    return
  }
  if (isLiked.value) {
    useMessage('您已点赞，无法点踩', 'warn')
    return
  }
  handleClickDislikeThrottled()
}
</script>

<template>
  <KunTooltip text="点踩">
    <KunButton
      :is-icon-only="true"
      :variant="isDisliked ? 'flat' : 'light'"
      :color="isDisliked ? 'secondary' : 'default'"
      :size="dislikeCount ? 'md' : 'lg'"
      class-name="gap-1"
      :disabled="isLiked"
      @click="handleClickDislike"
    >
      <KunIcon class="icon" name="lucide:thumbs-down" />
      <span v-if="dislikeCount">{{ dislikeCount }}</span>
    </KunButton>
  </KunTooltip>
</template>
