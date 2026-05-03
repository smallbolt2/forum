<script setup lang="ts">
import { kungalgameResponseHandler } from '~/utils/responseHandler'

const props = defineProps<{
  reply: TopicReply
}>()

const tempReplyStore = useTempReplyStore()
const { id, role } = usePersistUserStore()

const isCommonUser = role < 2
const isDisabled = computed(() => id !== props.reply.user.id && isCommonUser)

const handleDeleteReply = async () => {
  const res = await useComponentMessageStore().alert(
    isCommonUser
      ? '你这个坏萝莉, 确定删除这个回复吗?'
      : '你好萝莉管理员, 要删除这个回复吗',
    '删除操作不可撤销'
  )
  if (!res) {
    return
  }

  const result = await $fetch(`/api/topic/${props.reply.topicId}/reply`, {
    method: 'DELETE',
    watch: false,
    query: { replyId: props.reply.id },
    ...kungalgameResponseHandler
  })

  if (result) {
    tempReplyStore.setSuccessfulReply({ data: props.reply, type: 'deleted' })
    useMessage('删除回复成功', 'success')
  }
}
</script>

<template>
  <KunButton
    variant="light"
    color="danger"
    size="sm"
    @click="handleDeleteReply"
    class-name="whitespace-nowrap gap-2 justify-start"
    :disabled="isDisabled"
  >
    <KunIcon class-name="text-lg" name="lucide:trash-2" />
    删除回复
  </KunButton>
</template>
