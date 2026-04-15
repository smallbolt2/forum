import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { EditStoreTemp } from '~/store/types/edit/topic'

export const useTempEditStore = defineStore(
  'tempEdit',
  () => {
    const id = ref<EditStoreTemp['id']>(0)
    const title = ref<EditStoreTemp['title']>('')
    const content = ref<EditStoreTemp['content']>('')
    const tags = ref<EditStoreTemp['tags']>([])
    const category = ref<EditStoreTemp['category']>('')
    const section = ref<EditStoreTemp['section']>([])
    const isNSFW = ref<EditStoreTemp['isNSFW']>(false)
    const isTopicRewriting = ref<EditStoreTemp['isTopicRewriting']>(false)

    const resetRewriteTopicData = () => {
      id.value = 0
      title.value = ''
      content.value = ''
      tags.value = []
      category.value = ''
      section.value = []
      isNSFW.value = false
      isTopicRewriting.value = false
    }

    return {
      id,
      title,
      content,
      tags,
      category,
      section,
      isNSFW,
      isTopicRewriting,
      resetRewriteTopicData
    }
  },
  {
    persist: false
  }
)
