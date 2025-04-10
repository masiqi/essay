// Styles
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

// Composables
import { createVuetify } from 'vuetify'
import type { ThemeDefinition } from 'vuetify'

const lightTheme: ThemeDefinition = {
  dark: false,
  colors: {
    background: '#F5F5F5',
    surface: '#FFFFFF',
    primary: '#1976D2',
    secondary: '#4CAF50',
    accent: '#FF9800',
    error: '#B00020',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FF9800',
    'on-background': '#212121',
    'on-surface': '#212121',
    'on-primary': '#FFFFFF',
    'on-secondary': '#FFFFFF',
    'on-accent': '#FFFFFF',
  }
}

export default createVuetify({
  theme: {
    defaultTheme: 'lightTheme',
    themes: {
      lightTheme,
    }
  },
  icons: {
    defaultSet: 'mdi',
  },
})
