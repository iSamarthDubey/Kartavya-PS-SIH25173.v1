/// <reference types="vite/client" />

declare interface ImportMetaEnv {
  readonly VITE_API_BASE?: string
  readonly VITE_API_PORT?: string
  readonly VITE_BACKEND_PORT?: string
  readonly VITE_API_URL?: string
  readonly SIEM_BACKEND_PORT?: string
  readonly ASSISTANT_PORT?: string
}

declare interface ImportMeta {
  readonly env: ImportMetaEnv
}
