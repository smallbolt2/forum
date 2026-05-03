<script setup lang="ts">
import { kungalgameResponseHandler } from '~/utils/responseHandler'

useKunDisableSeo('数据总览')

const days = ref(30)
const dayOptions = [7, 30, 90, 180, 365]

const { data: summaryData, status: summaryStatus } = await useFetch(
  '/api/admin/overview/all',
  {
    method: 'GET',
    ...kungalgameResponseHandler
  }
)

const { data: statsData, status: statsStatus } = await useFetch<AdminOverStats[]>(
  '/api/admin/overview/stats',
  {
    method: 'GET',
    query: computed(() => ({ days: days.value })),
    ...kungalgameResponseHandler
  }
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
          v-for="item in summaryData || []"
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
      <AdminOverviewChart class="mt-6" :data="statsData || []" />
    </KunCard>
  </div>
</template>
