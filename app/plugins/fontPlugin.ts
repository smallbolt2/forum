
export default defineNuxtPlugin((nuxtApp) => {
  // 确保 pinia 已经注册
  const pinia = usePinia()
  const store = usePersistSettingsStore(pinia)
  if (import.meta.client) {
    document.documentElement.style.setProperty(
      '--font-family',
      store.showKUNGalgameFontStyle
    )
  }
})