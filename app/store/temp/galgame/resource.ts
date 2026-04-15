import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { GalgameResourceStoreTemp } from '~/store/types/galgame/resource'

export const useTempGalgameResourceStore = defineStore(
  'tempGalgameResource',
  () => {
    const initResource: GalgameResourceStoreTemp = {
      type: 'game',
      link: [],
      language: 'zh-cn',
      platform: 'windows',
      size: '',
      code: '',
      password: '',
      note: ''
    }
    const resource = ref<GalgameResourceStoreTemp>(initResource)
    const isShowPublish = ref(false)
    const rewriteResourceId = ref(0)
    const commentToUid = ref(0)

    const resetGalgameResource = () => {
      resource.value = initResource
      isShowPublish.value = false
      rewriteResourceId.value = 0
      commentToUid.value = 0
    }

    return {
      resource,
      isShowPublish,
      rewriteResourceId,
      commentToUid,
      resetGalgameResource
    }
  },
  { persist: false }
)
