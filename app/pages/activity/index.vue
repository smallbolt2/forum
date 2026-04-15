<script setup lang="ts">
const description = `动态时间线, 展示全站 话题, 回复, Game 与社区的最新 Game 资源, Game 动态, Game 讨论, Game 评论等`

useKunSeoMeta({
  title: '动态时间线',
  description
})
</script>

<template>
  <ActivityTimeline />
</template>
