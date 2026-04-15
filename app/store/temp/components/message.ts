import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { MessageStore } from '~/store/types/components/message'

export const useComponentMessageStore = defineStore(
  'tempComponentMessage',
  () => {
    const showAlert = ref<MessageStore['showAlert']>(false)
    const alertTitle = ref<MessageStore['alertTitle']>('')
    const alertMsg = ref<MessageStore['alertMsg']>('')
    const isShowCancel = ref<MessageStore['isShowCancel']>(false)
    const isShowCapture = ref<MessageStore['isShowCapture']>(false)
    const isCaptureSuccessful = ref<MessageStore['isCaptureSuccessful']>(false)
    const codeSalt = ref<MessageStore['codeSalt']>('')

    const handleCloseHandler = ref<() => void>(() => {})
    const handleConfirmHandler = ref<() => void>(() => {})

    const alert = (
      title?: string,
      message?: string,
      showCancel?: boolean
    ): Promise<boolean> => {
      return new Promise<boolean>((resolve) => {
        showAlert.value = true
        alertTitle.value = title
        alertMsg.value = message
        isShowCancel.value = showCancel

        handleCloseHandler.value = () => resolve(false)
        handleConfirmHandler.value = () => resolve(true)
      })
    }

    const handleClose = () => {
      handleCloseHandler.value()
    }

    const handleConfirm = () => {
      handleConfirmHandler.value()
    }

    return {
      showAlert,
      alertTitle,
      alertMsg,
      isShowCancel,
      isShowCapture,
      isCaptureSuccessful,
      codeSalt,
      alert,
      handleClose,
      handleConfirm
    }
  },
  {
    persist: false
  }
)
