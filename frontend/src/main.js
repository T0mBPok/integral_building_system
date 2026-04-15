import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// глобальные стили
import './assets/styles/main.css'
import './assets/styles/dashboard.css'

const app = createApp(App)

app.use(router)

app.mount('#app')
