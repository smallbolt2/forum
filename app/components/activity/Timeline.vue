<script setup lang="ts">
import { KUN_ACTIVITY_TYPE_TYPE } from '~/constants/activity'
import { kungalgameResponseHandler } from '~/utils/responseHandler'

const pageData = reactive({
  page: 1,
  limit: 50
})

const unwrapTimeline = (payload: unknown): { items: ActivityItem[]; totalCount: number } => {
  const empty = { items: [] as ActivityItem[], totalCount: 0 }
  if (!payload || typeof payload !== 'object') {
    return empty
  }
  const raw =
    'data' in payload
      ? (payload as { data: { items?: ActivityItem[]; totalCount?: number } }).data
      : (payload as { items?: ActivityItem[]; totalCount?: number })
  return {
    items: raw?.items ?? [],
    totalCount: raw?.totalCount ?? 0
  }
}

const { data: timelineRaw, status } = await useFetch('/api/activity/timeline', {
  method: 'GET',
  query: pageData,
  ...kungalgameResponseHandler
})

const data = computed(() => unwrapTimeline(timelineRaw.value))
</script>

<template>
  <KunCard
    :is-transparent="false"
    v-if="data.items.length || status !== 'pending'"
    content-class="space-y-3"
    :is-hoverable="false"
  >
    <KunHeader
      name="动态时间线"
      description="动态时间线, 展示全站 话题, 回复, Game 与社区的最新 Game 资源, Game 动态, Game 讨论, Game 评论等"
    />

    <KunLoading v-if="status === 'pending'" />

    <p v-else-if="!data.items.length" class="text-default-500 text-sm">
      暂无动态，发布话题或回复后将显示在这里
    </p>

    <div v-else class="relative space-y-6">
      <div
        class="from-primary to-secondary absolute top-6 bottom-0 left-4 w-0.5 bg-gradient-to-b opacity-20"
      />

      <div
        v-for="(activity, index) in data.items"
        :key="activity.uniqueId || index"
        class="flex items-center gap-3"
      >
        <KunAvatar v-if="activity.actor" :user="activity.actor" />

        <div class="flex flex-col space-y-2">
          <KunLink
            underline="none"
            color="default"
            :to="activity.link"
            class-name="hover:text-primary block space-x-3 break-all transition-colors"
          >
            <KunContentText
              class-name="whitespace-normal!"
              :content="activity.content"
            />
            <KunBadge color="primary" size="xs">
              {{ KUN_ACTIVITY_TYPE_TYPE[activity.type] }}
            </KunBadge>
          </KunLink>

          <div class="flex items-center space-x-2">
            <span class="text-default-500 text-sm">
              {{
                activity.actor
                  ? `${activity.actor.name} 发布于 ${formatTimeDifference(activity.timestamp)}`
                  : formatTimeDifference(activity.timestamp)
              }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <KunPagination
      v-model:current-page="pageData.page"
      :total-page="Math.ceil(data.totalCount / pageData.limit)"
      :is-loading="status === 'pending'"
    />
  </KunCard>
</template>
