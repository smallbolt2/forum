<script setup lang="ts">
defineProps<{
  user: SearchResultUser
}>()
</script>

<template>
  <KunCard :is-pressable="true" :href="`/user/${user.id}/info`">
    <div class="flex items-center">
      <KunAvatar :disable-floating="true" :user="user" />
      <span class="ml-2">{{ user.name }}</span>
    </div>

    <pre v-if="user.bio" class="mt-2 text-sm break-all whitespace-pre-wrap">
      {{ user.bio }}
    </pre>

    <div class="mt-2 flex items-center justify-end text-sm">
      <span class="text-default-700">
        {{ formatDate(user.created, { isShowYear: true }) }}
      </span>
    </div>
  </KunCard>
</template>
