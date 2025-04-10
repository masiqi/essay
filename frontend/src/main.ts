import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // 引入路由
import vuetify from './plugins/vuetify' // 引入 Vuetify 插件
// import { loadFonts } from './plugins/webfontloader' // 暂时注释掉，因为文件不存在

import './style.css' // 确保 Tailwind CSS 样式在最后引入

// loadFonts() // 暂时注释掉

createApp(App)
  .use(router) // 使用路由
  .use(vuetify) // 使用 Vuetify
  .mount('#app')
