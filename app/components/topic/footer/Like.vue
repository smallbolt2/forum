<script setup lang="ts">
import { kungalgameResponseHandler } from '~/utils/responseHandler'

const props = defineProps<{
  topicId?: number
  replyId?: number
  targetUserId: number
  likeCount: number
  isLiked: boolean
  isDisliked: boolean
}>()

const emits = defineEmits<{
  (event: 'updateLike', payload: { isLiked: boolean; likeCount: number }): void
}>()

const { id } = usePersistUserStore()
const isLiked = ref(props.isLiked)
const isDisliked = ref(props.isDisliked)
const likeCount = ref(props.likeCount)
const isLikePending = ref(false)

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
  () => props.likeCount,
  (value) => {
    likeCount.value = value
  }
)

const toggleLike = async () => {
  if (isLikePending.value) {
    return
  }

  isLikePending.value = true
  const wasLiked = isLiked.value
  let res: string | { isLiked: boolean; likeCount: number } = ''

  try {
    if (props.replyId) {
      const result = await $fetch(`/api/topic/${props.topicId}/reply/like`, {
        method: 'PUT',
        body: { replyId: props.replyId },
        watch: false,
        ...kungalgameResponseHandler
      })
      res = result ?? ''
    } else if (props.topicId) {
      const result = await $fetch(`/api/topic/${props.topicId}/like`, {
        method: 'PUT',
        watch: false,
        body: { topicId: props.topicId },
        ...kungalgameResponseHandler
      })
      res = result ?? ''
    }

    if (res) {
      if (typeof res === 'object' && res !== null && 'isLiked' in res && 'likeCount' in res) {
        isLiked.value = res.isLiked
        likeCount.value = res.likeCount
      } else {
        isLiked.value = !wasLiked
        likeCount.value = Math.max(0, likeCount.value + (wasLiked ? -1 : 1))
      }

      if (isLiked.value) {
        isDisliked.value = false
      }

      emits('updateLike', {
        isLiked: isLiked.value,
        likeCount: likeCount.value
      })

      useMessage(wasLiked ? 10234 : 10233, 'success')
    }
  } finally {
    isLikePending.value = false
  }
}

const handleClickLike = () => {
  if (!id) {
    useMessage(10235, 'warn', 5000)
    return
  }
  if (id === props.targetUserId) {
    useMessage(10236, 'warn')
    return
  }
  if (isDisliked.value) {
    useMessage('您已点踩，无法点赞', 'warn')
    return
  }
  toggleLike()
}
</script>

<template>
  <KunTooltip text="点赞">
    <KunButton
      :is-icon-only="true"
      :variant="isLiked ? 'flat' : 'light'"
      :color="isLiked ? 'secondary' : 'default'"
      :size="likeCount ? 'md' : 'lg'"
      class-name="gap-1"
      :loading="isLikePending"
      :disabled="isLikePending || isDisliked"
      @click="handleClickLike"
    >
      <KunIcon name="lucide:thumbs-up" />
      <span v-if="likeCount">{{ likeCount }}</span>
    </KunButton>
  </KunTooltip>
</template>
