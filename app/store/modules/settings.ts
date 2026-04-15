import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  ENABLE_KUN_VISUAL_NOVEL_FORUM_WINTER_THEME,
  KUN_VISUAL_NOVEL_FORUM_WINTER_THEME_BACKGROUND
} from '~/config/theme'
import type { KUNGalgameSettingsStore } from '../types/settings'

const SETTINGS_CUSTOM_BACKGROUND_IMAGE_NAME: string = 'kun-galgame-custom-bg'
const SETTINGS_PUBLISH_Banner_IMAGE_NAME: string = 'kun-galgame-publish-banner'
const SETTINGS_DEFAULT_FONT_FAMILY: string = 'system-ui'

export const usePersistSettingsStore = defineStore(
  'KUNGalgameSettings',
  () => {
    const showKUNGalgamePageTransparency =
      ref<KUNGalgameSettingsStore['showKUNGalgamePageTransparency']>(50)
    const showKUNGalgameFontStyle = ref<
      KUNGalgameSettingsStore['showKUNGalgameFontStyle']
    >(SETTINGS_DEFAULT_FONT_FAMILY)
    const showKUNGalgameContentLimit =
      ref<KUNGalgameSettingsStore['showKUNGalgameContentLimit']>('sfw')
    const showKUNGalgameBackground =
      ref<KUNGalgameSettingsStore['showKUNGalgameBackground']>(0)
    const showKUNGalgameBackgroundBlur =
      ref<KUNGalgameSettingsStore['showKUNGalgameBackgroundBlur']>(0)
    const showKUNGalgameBackgroundBrightness =
      ref<KUNGalgameSettingsStore['showKUNGalgameBackgroundBrightness']>(100)
    const showKUNGalgameBackLoli =
      ref<KUNGalgameSettingsStore['showKUNGalgameBackLoli']>(false)
    const showKUNGalgameSidebarCollapsed =
      ref<KUNGalgameSettingsStore['showKUNGalgameSidebarCollapsed']>(false)

    const toggleKUNGalgameSidebarCollapsed = () => {
      showKUNGalgameSidebarCollapsed.value =
        !showKUNGalgameSidebarCollapsed.value
    }

    const setKUNGalgameFontStyle = (font: string) => {
      showKUNGalgameFontStyle.value = font
      document.documentElement.style.setProperty('--font-family', font)
    }

    const setKUNGalgameTransparency = (trans: number) => {
      showKUNGalgamePageTransparency.value = trans
      document.documentElement.style.setProperty(
        '--kun-global-opacity',
        `${trans / 100}`
      )
    }

    const setKUNGalgameBackgroundBlur = (blur: number) => {
      showKUNGalgameBackgroundBlur.value = blur
      document.documentElement.style.setProperty(
        '--kun-background-blur',
        `${blur}px`
      )
    }

    const setKUNGalgameBackgroundBrightness = (brightness: number) => {
      showKUNGalgameBackgroundBrightness.value = brightness
      document.documentElement.style.setProperty(
        '--kun-background-brightness',
        `${brightness}%`
      )
    }

    const setSystemBackground = async (index: number) => {
      showKUNGalgameBackground.value = index
      await deleteImage(SETTINGS_CUSTOM_BACKGROUND_IMAGE_NAME)
    }

    const setCustomBackground = async (file: File) => {
      await saveImage(file, SETTINGS_CUSTOM_BACKGROUND_IMAGE_NAME)
      showKUNGalgameBackground.value = -1
    }

    const getCurrentBackground = async () => {
      const backgroundImageBlobData = await getImage(
        SETTINGS_CUSTOM_BACKGROUND_IMAGE_NAME
      )
      if (showKUNGalgameBackground.value === 0) {
        return ENABLE_KUN_VISUAL_NOVEL_FORUM_WINTER_THEME
          ? KUN_VISUAL_NOVEL_FORUM_WINTER_THEME_BACKGROUND
          : ''
      }

      if (showKUNGalgameBackground.value === -1 && backgroundImageBlobData) {
        return URL.createObjectURL(backgroundImageBlobData)
      }

      return `/bg/bg${showKUNGalgameBackground.value}.webp`
    }

    const setKUNGalgameSettingsRecover = async () => {
      kungalgameStoreReset()
      await deleteImage(SETTINGS_CUSTOM_BACKGROUND_IMAGE_NAME)
      await deleteImage(SETTINGS_PUBLISH_Banner_IMAGE_NAME)
    }

    return {
      showKUNGalgamePageTransparency,
      showKUNGalgameFontStyle,
      showKUNGalgameContentLimit,
      showKUNGalgameBackground,
      showKUNGalgameBackgroundBlur,
      showKUNGalgameBackgroundBrightness,
      showKUNGalgameBackLoli,
      showKUNGalgameSidebarCollapsed,
      toggleKUNGalgameSidebarCollapsed,
      setKUNGalgameFontStyle,
      setKUNGalgameTransparency,
      setKUNGalgameBackgroundBlur,
      setKUNGalgameBackgroundBrightness,
      setSystemBackground,
      setCustomBackground,
      getCurrentBackground,
      setKUNGalgameSettingsRecover
    }
  },
  {
    persist: true
  }
)
