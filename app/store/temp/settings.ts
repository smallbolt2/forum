import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { TempSettingStore } from '~/store/types/settings'

export const useTempSettingStore = defineStore(
  'tempSetting',
  () => {
    const showKUNGalgameHamburger =
      ref<TempSettingStore['showKUNGalgameHamburger']>(false)
    const showKUNGalgamePanel =
      ref<TempSettingStore['showKUNGalgamePanel']>(false)
    const showKUNGalgameUserPanel =
      ref<TempSettingStore['showKUNGalgameUserPanel']>(false)
    const showKUNGalgameMessageBox =
      ref<TempSettingStore['showKUNGalgameMessageBox']>(false)
    const messageStatus = ref<TempSettingStore['messageStatus']>('offline')

    const reset = () => {
      showKUNGalgameHamburger.value = false
      showKUNGalgamePanel.value = false
      showKUNGalgameUserPanel.value = false
      showKUNGalgameMessageBox.value = false
    }

    return {
      showKUNGalgameHamburger,
      showKUNGalgamePanel,
      showKUNGalgameUserPanel,
      showKUNGalgameMessageBox,
      messageStatus,
      reset
    }
  },
  {
    persist: false
  }
)
