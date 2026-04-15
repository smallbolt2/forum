<script setup lang="ts">
definePageMeta({
  middleware: ['auth', 'prevent']
})

useKunSeoMeta({ title: '发布 Game' })
</script>

<template>
  <EditGalgame />
</template>
