<script setup lang="ts">
import { kungalgameResponseHandler } from '~/utils/responseHandler'

const props = defineProps<{
  comment: TopicComment
}>()

const emits = defineEmits<{
  removeComment: [commentId: number]
}>()

const { id, role } = usePersistUserStore()

const isCommonUser = role < 2
const isAdmin = role > 1
const canDelete = computed(() => id === props.comment.user.id || isAdmin)

const handleDeleteComment = async () => {
  const res = await useComponentMessageStore().alert(
    isCommonUser
      ? '你这个坏萝莉, 确定删除这个评论吗?'
      : '你好萝莉管理员, 要删除这个评论吗',
    '删除操作不可撤销'
  )
  if (!res) {
    return
  }

  const result = await $fetch(`/api/topic/${props.comment.topicId}/comment`, {
    method: 'DELETE',
    watch: false,
    query: { commentId: props.comment.id },
    ...kungalgameResponseHandler
  })

  if (result) {
    emits('removeComment', props.comment.id)
    useMessage('删除评论成功', 'success')
  }
}
</script>

<template>
  <KunButton
    v-if="canDelete"
    :is-icon-only="true"
    variant="light"
    color="danger"
    @click="handleDeleteComment"
  >
    <KunIcon name="lucide:trash-2" />
  </KunButton>
</template>
