<script setup lang="ts">
import { kungalgameResponseHandler } from '~/utils/responseHandler'

const props = defineProps<{
  topicId: number
}>()

const { id, role } = usePersistUserStore()
const topicUserId = inject<number>('topicUserId')

const isDisabled = role < 2 && topicUserId !== id

const handleUpdateTopicHideStatus = async () => {
  const res = await useComponentMessageStore().alert(
    '八嘎杂鱼笨蛋萝莉, 你要隐藏该话题吗, 隐藏后此话题任何人都不可见, 您可以在您的主页重新启用被隐藏的话题'
  )
  if (!res) {
    return
  }

  const result = await $fetch(`/api/topic/${props.topicId}/hide`, {
    method: 'PUT',
    watch: false,
    body: { topicId: props.topicId },
    ...kungalgameResponseHandler
  })

  if (result) {
    useMessage('隐藏话题成功', 'success')
  }
}

const handleDeleteTopicPermanently = async () => {
  const res = await useComponentMessageStore().alert(
    '确定要彻底删除该话题吗？此操作不可恢复，将删除该话题及其所有回复和评论。'
  )
  if (!res) {
    return
  }

  const result = await $fetch(`/api/topic/${props.topicId}`, {
    method: 'DELETE',
    watch: false,
    query: { topicId: props.topicId },
    ...kungalgameResponseHandler
  })

  if (result) {
    useMessage('彻底删除话题成功', 'success')
    await navigateTo('/topic')
  }
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <KunButton
      variant="light"
      color="danger"
      size="sm"
      :disabled="isDisabled"
      @click="handleUpdateTopicHideStatus"
      class-name="whitespace-nowrap gap-2 justify-start"
    >
      <KunIcon class-name="text-lg" name="lucide:ban" />
      隐藏该话题
    </KunButton>

    <KunButton
      variant="light"
      color="danger"
      size="sm"
      :disabled="isDisabled"
      @click="handleDeleteTopicPermanently"
      class-name="whitespace-nowrap gap-2 justify-start"
    >
      <KunIcon class-name="text-lg" name="lucide:trash-2" />
      彻底删除话题
    </KunButton>
  </div>
</template>
