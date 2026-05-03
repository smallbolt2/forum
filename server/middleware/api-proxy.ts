import { getRequestURL, proxyRequest, setResponseHeader } from 'h3'

export default defineEventHandler(async (event) => {
  const url = getRequestURL(event)
  if (!url.pathname.startsWith('/api/')) {
    return
  }

  // @nuxt/icon 在 Nitro 上注册为 /api/_nuxt_icon/*，勿转发到 Flask，否则会 404。
  if (url.pathname.startsWith('/api/_nuxt_icon')) {
    return
  }

  const config = useRuntimeConfig()
  const upstreamBase = (config.KUN_GALGAME_API || '').toString().replace(/\/+$/, '')
  if (!upstreamBase) {
    return
  }

  // Flask 等后端挂在 /api/*；上游地址常见两种写法：
  // - http://127.0.0.1:5000        → 应转发完整路径 /api/user/login
  // - http://127.0.0.1:5000/api    → 路径里不要再多一层 /api
  const pathWithQuery = `${url.pathname}${url.search}`
  const upstreamUrl =
    upstreamBase.endsWith('/api') && pathWithQuery.startsWith('/api/')
      ? `${upstreamBase}${pathWithQuery.slice(4)}`
      : `${upstreamBase}${pathWithQuery}`

  // Make sure downstream sees original host/proto if needed
  setResponseHeader(event, 'x-proxied-by', 'nuxt-nitro')

  return proxyRequest(event, upstreamUrl)
})

