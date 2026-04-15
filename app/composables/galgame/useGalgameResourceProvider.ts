import { GALGAME_RESOURCE_PROVIDER_MAP } from '~/constants/galgameResource'

export const useGalgameResourceProvider = () => {
  const providerName = ref('')

  const fetchTitle = async (domain: string) => {
    try {
      const html = await $fetch<string>(`https://www.${domain}`, {
        timeout: 5000,
        headers: {
          'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
      })

      const match = html.match(/<title>(.*?)<\/title>/i)

      if (match && match[1]) {
        const index = match[1].indexOf(' ')
        const result = index === -1 ? match[1] : match[1].substring(0, index)
        return { title: result.trim() }
      }
      return { title: null }
    } catch (_err) {
      return { title: null }
    }
  }

  const findKnownProvider = (domain: string): string | null => {
    if (GALGAME_RESOURCE_PROVIDER_MAP[domain]) {
      return GALGAME_RESOURCE_PROVIDER_MAP[domain]
    }
    if (domain.includes('lanzou')) {
      return GALGAME_RESOURCE_PROVIDER_MAP.lanzou!
    }
    return null
  }

  const resolveProviderName = async (domain: string) => {
    const known = findKnownProvider(domain)

    if (known) {
      providerName.value = known
      return known
    }

    providerName.value = '正在获取资源提供方信息...'

    try {
      const result = await fetchTitle(domain)
      providerName.value = result.title || domain
      return providerName.value
    } catch (err) {
      providerName.value = domain
      return domain
    }
  }

  return {
    providerName,
    resolveProviderName
  }
}
