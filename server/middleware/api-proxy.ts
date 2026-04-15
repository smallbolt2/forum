import { getRequestURL, proxyRequest, setResponseHeader } from 'h3'

export default defineEventHandler(async (event) => {
  const url = getRequestURL(event)
  if (!url.pathname.startsWith('/api/')) {
    return
  }

  const config = useRuntimeConfig()
  const upstreamBase = (config.KUN_GALGAME_API || '').toString().replace(/\/+$/, '')
  if (!upstreamBase) {
    return
  }

  const upstreamUrl = `${upstreamBase}${url.pathname.replace(/^\/api/, '')}${url.search}`

  // Make sure downstream sees original host/proto if needed
  setResponseHeader(event, 'x-proxied-by', 'nuxt-nitro')

  return proxyRequest(event, upstreamUrl)
})

