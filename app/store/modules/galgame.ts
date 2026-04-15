import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ProviderKey } from '~/constants/galgameResource'
import type { GalgameAdvancedFilterPersist } from '~/store/types/galgame/advancedFilter'

export const usePersistKUNGalgameAdvancedFilterStore = defineStore(
  'KUNGalgameAdvancedFilter',
  () => {
    const includeProviders = ref<
      GalgameAdvancedFilterPersist['includeProviders']
    >([])
    const excludeOnlyProviders = ref<
      GalgameAdvancedFilterPersist['excludeOnlyProviders']
    >([])

    const setIncludeProviders = (providers: ProviderKey[]) => {
      includeProviders.value = Array.from(new Set(providers))
    }

    const setExcludeOnlyProviders = (providers: ProviderKey[]) => {
      excludeOnlyProviders.value = Array.from(new Set(providers))
    }

    const toggleIncludeProvider = (provider: ProviderKey) => {
      const idx = includeProviders.value.indexOf(provider)
      if (idx === -1) includeProviders.value.push(provider)
      else includeProviders.value.splice(idx, 1)
    }

    const toggleExcludeOnlyProvider = (provider: ProviderKey) => {
      const idx = excludeOnlyProviders.value.indexOf(provider)
      if (idx === -1) excludeOnlyProviders.value.push(provider)
      else excludeOnlyProviders.value.splice(idx, 1)
    }

    return {
      includeProviders,
      excludeOnlyProviders,
      setIncludeProviders,
      setExcludeOnlyProviders,
      toggleIncludeProvider,
      toggleExcludeOnlyProvider
    }
  },
  {
    persist: true
  }
)
