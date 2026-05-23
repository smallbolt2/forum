<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const { messageStatus } = storeToRefs(useTempSettingStore())

useHead({ title: `消息 - ${kungal.titleShort}` })

onMounted(() => (messageStatus.value = 'online'))
</script>

<template>
  <KunCard
    :is-hoverable="false"
    :is-transparent="false"
    content-class="flex-row h-[calc(100dvh-120px)]"
  >
    <MessageAsideContainer />
    <div class="min-w-0 flex-1 overflow-hidden">
      <NuxtPage />
    </div>
  </KunCard>
</template>
