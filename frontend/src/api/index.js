import axios from 'axios'
var api = axios.create({ baseURL: '/api' })
var token = localStorage.getItem('token') || null
var refreshToken = localStorage.getItem('refreshToken') || null

export function setTokens(t, rt) {
  token = t; refreshToken = rt
  localStorage.setItem('token', t); localStorage.setItem('refreshToken', rt)
  api.defaults.headers.common['Authorization'] = 'Bearer ' + t
}
export function clearTokens() {
  token = null; refreshToken = null
  localStorage.removeItem('token'); localStorage.removeItem('refreshToken')
  delete api.defaults.headers.common['Authorization']
}
export function getToken() { return token }
if (token) api.defaults.headers.common['Authorization'] = 'Bearer ' + token

api.interceptors.response.use(function(r) { return r }, async function(err) {
  if (err.response && err.response.status === 401 && refreshToken) {
    try {
      var resp = await axios.post('/api/auth/refresh', { refresh_token: refreshToken })
      setTokens(resp.data.token, resp.data.refresh_token)
      err.config.headers['Authorization'] = 'Bearer ' + resp.data.token
      return api(err.config)
    } catch(e) { clearTokens(); window.location.hash = '#/login' }
  }
  return Promise.reject(err)
})

export var authApi = {
  register: function(d) { return api.post('/auth/register', d) },
  login: function(d) { return api.post('/auth/login', d) },
  refresh: function(d) { return api.post('/auth/refresh', d) }
}
export var userApi = { me: function() { return api.get('/users/me') }, get: function(id) { return api.get('/users/' + id) } }
export var kycApi = {
  status: function() { return api.get('/kyc/status') },
  submit: function(d) { return api.post('/kyc/submit', d) },
  verify: function() { return api.post('/kyc/verify') }
}
export var inventoryApi = {
  list: function(params) { return api.get('/inventory', { params: params }) },
  create: function(d) { return api.post('/inventory', d) },
  remove: function(id) { return api.delete('/inventory/' + id) }
}
export var listingApi = {
  list: function(params) { return api.get('/listings', { params: params }) },
  my: function() { return api.get('/listings/my') },
  create: function(d) { return api.post('/listings', d) },
  close: function(id) { return api.patch('/listings/' + id + '/close') }
}
export var offerApi = {
  list: function() { return api.get('/offers') },
  create: function(d) { return api.post('/offers', d) },
  accept: function(id) { return api.post('/offers/' + id + '/accept') },
  reject: function(id) { return api.post('/offers/' + id + '/reject') },
  confirm: function(id) { return api.post('/offers/' + id + '/confirm') }
}
export var tradeApi = {
  list: function() { return api.get('/trades') },
  get: function(id) { return api.get('/trades/' + id) }
}
export var notifApi = {
  list: function(params) { return api.get('/notifications', { params: params }) },
  markRead: function(id) { return api.patch('/notifications/' + id + '/read') },
  markAllRead: function() { return api.post('/notifications/read-all') }
}
export var steamApi = {
  link: function(d) { return api.post('/steam/link', d) },
  accounts: function() { return api.get('/steam/accounts') }
}
export default api