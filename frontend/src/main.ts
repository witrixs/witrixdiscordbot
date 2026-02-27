import { createApp } from 'vue'
import { initTheme } from './composables/useTheme'
import './style.css'
import App from './App.vue'
import router from './router'

initTheme()
createApp(App).use(router).mount('#app')
