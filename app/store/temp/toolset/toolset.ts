import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ToolsetStoreTemp } from '~/store/types/toolset/toolset'

export const useTempToolsetStore = defineStore(
  'tempToolset',
  () => {
    const page = ref<ToolsetStoreTemp['page']>(1)
    const limit = ref<ToolsetStoreTemp['limit']>(24)
    const type = ref<ToolsetStoreTemp['type']>('all')
    const language = ref<ToolsetStoreTemp['language']>('all')
    const platform = ref<ToolsetStoreTemp['platform']>('all')
    const version = ref<ToolsetStoreTemp['version']>('all')
    const sortField = ref<ToolsetStoreTemp['sortField']>('resource_update_time')
    const sortOrder = ref<ToolsetStoreTemp['sortOrder']>('desc')

    return {
      page,
      limit,
      type,
      language,
      platform,
      version,
      sortField,
      sortOrder
    }
  },
  {
    persist: false
  }
)
