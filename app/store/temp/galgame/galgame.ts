import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { GalgameStoreTemp } from '~/store/types/galgame/galgame'

// for cross page state not lost
export const useTempGalgameStore = defineStore(
  'tempGalgame',
  () => {
    const page = ref<GalgameStoreTemp['page']>(1)
    const limit = ref<GalgameStoreTemp['limit']>(24)
    const type = ref<GalgameStoreTemp['type']>('all')
    const language = ref<GalgameStoreTemp['language']>('all')
    const platform = ref<GalgameStoreTemp['platform']>('all')
    const sortField = ref<GalgameStoreTemp['sortField']>('time')
    const sortOrder = ref<GalgameStoreTemp['sortOrder']>('desc')

    return {
      page,
      limit,
      type,
      language,
      platform,
      sortField,
      sortOrder
    }
  },
  {
    persist: false
  }
)
