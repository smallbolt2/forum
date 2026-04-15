import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'
import { createEmptyLocaleMap, resetReactiveState } from '~/store/index'
import type { GalgameStorePersist } from '~/store/types/edit/galgame'

export const usePersistEditGalgameStore = defineStore(
  'KUNGalgameEditGalgame',
  () => {
    const vndbId = ref<GalgameStorePersist['vndbId']>('')
    const name = reactive<GalgameStorePersist['name']>({
      'en-us': '',
      'ja-jp': '',
      'zh-cn': '',
      'zh-tw': ''
    })
    const introduction = reactive<GalgameStorePersist['introduction']>({
      'en-us': '',
      'ja-jp': '',
      'zh-cn': '',
      'zh-tw': ''
    })
    const contentLimit = ref<GalgameStorePersist['contentLimit']>('sfw')
    const aliases = ref<GalgameStorePersist['aliases']>([])

    const resetEditGalgameStore = () => {
      vndbId.value = ''
      resetReactiveState(name, createEmptyLocaleMap())
      resetReactiveState(introduction, createEmptyLocaleMap())
      contentLimit.value = 'sfw'
      aliases.value = []
    }

    return {
      vndbId,
      name,
      introduction,
      contentLimit,
      aliases,

      resetEditGalgameStore
    }
  },
  {
    persist: {
      storage: piniaPluginPersistedstate.localStorage()
    }
  }
)
