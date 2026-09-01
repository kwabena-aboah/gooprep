import axios from 'axios'

const API_BASE = (
  import.meta.env.VITE_API_URL || 'http://localhost:8000'
).replace(/\/$/, '')

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

/*
|--------------------------------------------------------------------------
| Request interceptor
|--------------------------------------------------------------------------
*/

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')

    if (token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(error)
)

/*
|--------------------------------------------------------------------------
| Token refresh
|--------------------------------------------------------------------------
*/

let refreshing = false
let queue = []

const flushQueue = (error, token = null) => {
  queue.forEach((promise) => {
    if (error) {
      promise.reject(error)
    } else {
      promise.resolve(token)
    }
  })

  queue = []
}

/*
|--------------------------------------------------------------------------
| Response interceptor
|--------------------------------------------------------------------------
*/

api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const originalRequest = error.config

    /*
     * Only refresh the token for 401 errors.
     *
     * A 400 error from /scheduling/lessons/ is NOT a
     * token-refresh problem.
     */
    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/token/') &&
      !originalRequest.url?.includes('/auth/token/refresh/')
    ) {
      /*
       * Another request is already refreshing the token.
       * Put this request into the queue.
       */
      if (refreshing) {
        return new Promise((resolve, reject) => {
          queue.push({
            resolve,
            reject,
          })
        }).then((newToken) => {
          originalRequest.headers =
            originalRequest.headers || {}

          originalRequest.headers.Authorization =
            `Bearer ${newToken}`

          return api(originalRequest)
        })
      }

      originalRequest._retry = true
      refreshing = true

      const refreshToken =
        localStorage.getItem('refresh_token')

      if (!refreshToken) {
        refreshing = false

        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('gp_user')

        return Promise.reject(error)
      }

      try {
        const response = await axios.post(
          `${API_BASE}/api/auth/token/refresh/`,
          {
            refresh: refreshToken,
          },
          {
            headers: {
              'Content-Type': 'application/json',
            },
            withCredentials: true,
          }
        )

        const newAccessToken =
          response.data.access

        localStorage.setItem(
          'access_token',
          newAccessToken
        )

        flushQueue(null, newAccessToken)

        originalRequest.headers =
          originalRequest.headers || {}

        originalRequest.headers.Authorization =
          `Bearer ${newAccessToken}`

        return api(originalRequest)

      } catch (refreshError) {
        flushQueue(refreshError)

        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('gp_user')

        return Promise.reject(refreshError)

      } finally {
        refreshing = false
      }
    }

    return Promise.reject(error)
  }
)

/*
|--------------------------------------------------------------------------
| API helpers
|--------------------------------------------------------------------------
*/

export const apiGet = (
  url,
  params = {}
) => {
  return api.get(url, { params })
}

export const apiDownload = (
  url,
  params = {}
) => {
  return api.get(url, {
    params,
    responseType: 'blob',
  })
}

export const apiPost = async (url, data = {}) => {
  try {
    return await api.post(url, data)
  } catch (error) {
    console.error('API POST ERROR')
    console.error('URL:', url)
    console.error('Status:', error.response?.status)
    console.error('Response:', error.response?.data)
    console.error('Request data:', data)

    throw error
  }
}

export const apiPatch = (
  url,
  data = {}
) => {
  return api.patch(url, data)
}

export const apiPut = (
  url,
  data = {}
) => {
  return api.put(url, data)
}

export const apiDelete = (
  url
) => {
  return api.delete(url)
}

export const apiUpload = (
  url,
  form,
  method = 'patch'
) => {
  return api.request({
    method,
    url,
    data: form,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

/*
|--------------------------------------------------------------------------
| WebSocket
|--------------------------------------------------------------------------
*/

export function createWS(path) {
  const configuredWsUrl = import.meta.env.VITE_WS_URL
  const apiUrl = import.meta.env.VITE_API_URL
  const derivedWsUrl = apiUrl
    ? apiUrl.replace(/^http/, 'ws')
    : ''
  const base = configuredWsUrl || derivedWsUrl || 'ws://localhost:8000'

  const token =
    localStorage.getItem('access_token')

  return new WebSocket(
    `${base}/ws/${path}${
      token
        ? `?token=${encodeURIComponent(token)}`
        : ''
    }`
  )
}

export default api