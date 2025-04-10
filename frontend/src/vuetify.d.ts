// Vuetify 类型声明
declare module 'vuetify' {
  import { VuetifyOptions } from 'vuetify'
  export function createVuetify(options?: VuetifyOptions): any
  export interface ThemeDefinition {
    dark?: boolean
    colors?: Record<string, string>
    variables?: Record<string, string>
  }
  export function useDisplay(): {
    mobile: boolean
    mobileBreakpoint: number
    platform: {
      android: boolean
      ios: boolean
      cordova: boolean
      electron: boolean
      chrome: boolean
      edge: boolean
      firefox: boolean
      opera: boolean
      safari: boolean
      win: boolean
      mac: boolean
      linux: boolean
      touch: boolean
    }
    thresholds: {
      xs: number
      sm: number
      md: number
      lg: number
      xl: number
    }
    width: number
    height: number
    name: string
    xs: boolean
    sm: boolean
    md: boolean
    lg: boolean
    xl: boolean
    xsOnly: boolean
    smOnly: boolean
    smAndDown: boolean
    smAndUp: boolean
    mdOnly: boolean
    mdAndDown: boolean
    mdAndUp: boolean
    lgOnly: boolean
    lgAndDown: boolean
    lgAndUp: boolean
    xlOnly: boolean
  }
}

declare module 'vuetify/styles' {
  const styles: string
  export default styles
}

declare module 'vuetify/components' {
  import { Plugin } from 'vue'
  const components: Plugin
  export default components
}

declare module 'vuetify/directives' {
  import { Plugin } from 'vue'
  const directives: Plugin
  export default directives
}

declare module 'vuetify/labs/components' {
  import { Plugin } from 'vue'
  const components: Plugin
  export default components
}
