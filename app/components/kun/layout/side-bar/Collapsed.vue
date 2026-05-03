<script setup lang="ts">
import type { KunLayoutCollapsedItem } from '~/constants/layout'

const route = useRoute()

/** 与 KunTopBarSideCollapsed 入口一致，纵向排布适配窄侧栏 */
const items: KunLayoutCollapsedItem[] = [
  {
    name: 'create',
    icon: 'lucide:pencil',
    label: '发布主题',
    router: '/edit/topic'
  },
  {
    name: 'timeline',
    icon: 'lucide:activity',
    label: '动态时间线',
    router: '/activity'
  }
]
</script>

<template>
  <nav class="flex w-full flex-col items-center gap-2 px-1 py-2">
    <KunTooltip
      v-for="item in items"
      :key="item.name"
      :text="item.label"
      position="right"
    >
      <KunButton
        is-icon-only
        variant="light"
        size="lg"
        :href="item.router"
        :aria-label="item.label"
        color="default"
        :class="
          cn(
            'flex h-11 w-11 items-center justify-center',
            route.fullPath === item.router
              ? 'bg-accent text-primary'
              : 'text-foreground'
          )
        "
      >
        <KunIcon :name="item.icon" class="text-xl" />
      </KunButton>
    </KunTooltip>
  </nav>
</template>
