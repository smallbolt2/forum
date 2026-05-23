<script setup lang="ts">
import { kungalgameResponseHandler } from '~/utils/responseHandler'

useKunDisableSeo('数据总览')

const days = ref(30)
const dayOptions = [7, 30, 90, 180, 365]

/** Flask 统一响应为 { code, message, data }；Nitro 直连时为数组 */
const unwrapApiData = <T>(payload: unknown): T => {
  if (payload && typeof payload === 'object' && 'data' in payload) {
    return (payload as { data: T }).data
  }
  return payload as T
}

const { data: summaryRaw, status: summaryStatus } = await useFetch(
  '/api/admin/overview/all',
  {
    method: 'GET',
    ...kungalgameResponseHandler
  }
)

const { data: statsRaw, status: statsStatus } = await useFetch(
  '/api/admin/overview/stats',
  {
    method: 'GET',
    query: computed(() => ({ days: days.value })),
    ...kungalgameResponseHandler
  }
)

const summaryData = computed(() =>
  unwrapApiData<
    { name: string; label: string; color: string; count: number }[]
  >(summaryRaw.value) ?? []
)

const statsData = computed(() =>
  unwrapApiData<AdminOverStats[]>(statsRaw.value) ?? []
)
</script>

<template>
  <div class="w-full space-y-3">
    <KunCard
      :is-hoverable="false"
      :is-pressable="false"
      :is-transparent="false"
      class-name="w-full"
    >
      <KunHeader
        name="数据总览"
        description="查看网站核心数据总量及近一段时间的变化趋势"
      />

      <div class="mt-4 flex flex-wrap items-center gap-2">
        <span class="text-default-600 text-sm">统计范围</span>
        <KunButton
          v-for="day in dayOptions"
          :key="day"
          size="sm"
          :variant="days === day ? 'flat' : 'light'"
          @click="days = day"
        >
          {{ day }} 天
        </KunButton>
      </div>

      <KunLoading
        v-if="summaryStatus === 'pending' || statsStatus === 'pending'"
        class-name="mt-6"
      />

      <div
        v-else
        class="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
      >
        <KunCard
          v-for="item in summaryData"
          :key="item.name"
          :is-hoverable="false"
          :is-pressable="false"
          :is-transparent="true"
        >
          <div class="space-y-1">
            <p class="text-default-600 text-sm">{{ item.label }}</p>
            <p class="text-2xl font-bold" :style="{ color: item.color }">
              {{ item.count }}
            </p>
          </div>
        </KunCard>
      </div>
    </KunCard>

    <KunCard
      :is-hoverable="false"
      :is-pressable="false"
      :is-transparent="false"
      class-name="w-full"
    >
      <KunHeader
        name="趋势统计"
        :description="`最近 ${days} 天各类数据变化趋势`"
      />
      <AdminOverviewChart class="mt-6" :data="statsData" />
    </KunCard>
  </div>
</template>
