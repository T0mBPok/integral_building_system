import axios from 'axios'

const apiHost = window.location.hostname || 'localhost'

const api = axios.create({
  baseURL: `http://${apiHost}:9000`,
  withCredentials: true             
})

export default api
