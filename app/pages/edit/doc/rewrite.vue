<script setup lang="ts">
import { kungalgameResponseHandler } from '~/utils/responseHandler'

definePageMeta({
  middleware: 'auth'
})

const route = useRoute()
const slug = computed(() => (route.query.slug as string) || '')

if (!slug.value) {
  await navigateTo('/doc')
}

const { data: article } = await useFetch<DocArticleDetail>(
  `/api/doc/article/${slug.value}`,
  {
    method: 'GET',
    ...kungalgameResponseHandler
  }
)

useKunSeoMeta({ title: '重新编辑文档' })
</script>

<template>
  <div>
    <EditDocLayout v-if="article" mode="rewrite" :initial-article="article" />
    <KunNull v-else description="未找到对应的文档" />
  </div>
</template>
