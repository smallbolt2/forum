import Cookies from 'js-cookie'
import type { FetchResponse } from 'ofetch'

interface KunErrorData {
  data?: {
    code: number
    message: string
  }
  stack: string[]
  statusCode: number
  statusMessage: string
}

/** Nitro H3 嵌套 data；Flask 统一 error() 为顶层 code + message */
function extractBusinessCodeMessage(body: unknown): {
  code: number
  message: string
} | null {
  if (!body || typeof body !== 'object') {
    return null
  }
  const b = body as Record<string, unknown>
  if (typeof b.code === 'number' && typeof b.message === 'string') {
    return { code: b.code, message: b.message }
  }
  const inner = b.data
  if (
    inner &&
    typeof inner === 'object' &&
    typeof (inner as { code?: unknown }).code === 'number' &&
    typeof (inner as { message?: unknown }).message === 'string'
  ) {
    return {
      code: (inner as { code: number }).code,
      message: (inner as { message: string }).message
    }
  }
  return null
}

interface ResponseMap {
  blob: Blob
  text: string
  arrayBuffer: ArrayBuffer
  stream: ReadableStream<Uint8Array>
}
type ResponseType = keyof ResponseMap | 'json'

type KunOnResponseContext<
  R extends ResponseType,
  JsonType = unknown
> = R extends keyof ResponseMap ? ResponseMap[R] : JsonType

export const onResponse = async <R extends ResponseType>(
  context: KunOnResponseContext<R>
) => {
  const { response } = context as { response: FetchResponse<ResponseType> }
  const raw = response?._data
  const parsed = extractBusinessCodeMessage(raw)

  if (!raw) {
    useMessage('网络请求失败，请稍后重试', 'error')
    return
  }
  if (!parsed) {
    return
  }

  const { code, message } = parsed

  if (code === 205) {
    const navigateCookie = Cookies.get('kungalgame-is-navigate-to-login')
    const userStore = usePersistUserStore()

    if (!navigateCookie && userStore.id) {
      userStore.resetUser()

      useMessage(message || '登录已失效，请重新登录', 'error', 7777)

      Cookies.set('kungalgame-is-navigate-to-login', 'navigated', {
        expires: 1 / 1440
      })

      await navigateTo('/login')
      return
    }
  }

  if (code === 233) {
    useMessage(message, 'error')
  }
}

export const onResponseError = async <R extends ResponseType>(
  context: KunOnResponseContext<R>
) => {
  // ofetch 在非 2xx 时会触发 onResponseError，这里复用同一套错误解析逻辑
  await onResponse(context)
}

export const kungalgameResponseHandler = { onResponse, onResponseError }
