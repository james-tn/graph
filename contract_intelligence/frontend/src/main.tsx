import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Recover from "Failed to fetch dynamically imported module" errors caused by
// a redeploy invalidating chunk hashes while a stale index.html was cached.
// We reload the page once (guarded by sessionStorage) so the browser fetches
// a fresh index.html with the current chunk names.
const CHUNK_RELOAD_KEY = '__chunk_reload_attempted__'

function isDynamicImportError(message: unknown): boolean {
  if (typeof message !== 'string') return false
  return (
    message.includes('Failed to fetch dynamically imported module') ||
    message.includes('Importing a module script failed') ||
    message.includes('error loading dynamically imported module')
  )
}

function reloadOnce() {
  try {
    if (sessionStorage.getItem(CHUNK_RELOAD_KEY)) return
    sessionStorage.setItem(CHUNK_RELOAD_KEY, '1')
  } catch {
    // sessionStorage may be unavailable in private mode; reload anyway.
  }
  window.location.reload()
}

window.addEventListener('error', (event) => {
  if (isDynamicImportError(event.message)) {
    reloadOnce()
  }
})

window.addEventListener('unhandledrejection', (event) => {
  const reason = event.reason
  const message = reason instanceof Error ? reason.message : String(reason ?? '')
  if (isDynamicImportError(message)) {
    reloadOnce()
  }
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
