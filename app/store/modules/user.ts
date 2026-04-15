import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserStore } from '../types/user'

export const usePersistUserStore = defineStore(
  'KUNGalgameUser',
  () => {
    const id = ref<UserStore['id']>(0)
    const name = ref<UserStore['name']>('')
    const avatar = ref<UserStore['avatar']>('')
    const avatarMin = ref<UserStore['avatarMin']>('')
    const moemoepoint = ref<UserStore['moemoepoint']>(0)
    const role = ref<UserStore['role']>(0)
    const isCheckIn = ref<UserStore['isCheckIn']>(false)
    const dailyToolsetUploadCount = ref<UserStore['dailyToolsetUploadCount']>(0)

    const setUserInfo = (user: UserStore) => {
      id.value = user.id
      name.value = user.name
      avatar.value = user.avatar
      avatarMin.value = user.avatar.replace(/\.webp$/, '-100.webp')
      moemoepoint.value = user.moemoepoint
      role.value = user.role
      isCheckIn.value = user.isCheckIn
      dailyToolsetUploadCount.value = user.dailyToolsetUploadCount
    }

    const resetUser = () => {
      id.value = 0
      name.value = ''
      avatar.value = ''
      avatarMin.value = ''
      moemoepoint.value = 0
      role.value = 0
      isCheckIn.value = false
      dailyToolsetUploadCount.value = 0
    }

    return {
      id,
      name,
      avatar,
      avatarMin,
      moemoepoint,
      role,
      isCheckIn,
      dailyToolsetUploadCount,
      setUserInfo,
      resetUser
    }
  },
  {
    persist: true
  }
)
