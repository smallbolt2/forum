<script setup lang="ts">
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
    </div>
  </header>
</template>
