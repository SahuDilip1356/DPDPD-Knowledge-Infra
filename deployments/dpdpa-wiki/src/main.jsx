import { StrictMode } from 'react'
import { createRoot, hydrateRoot } from 'react-dom/client'
import './index.css'
import App, { preloadRoute } from './App.jsx'

const container = document.getElementById('root')
const path = window.location.pathname.replace(/\/+$/, '') || '/'
const app = (
  <StrictMode>
    <App />
  </StrictMode>
)

// Load this page's screen and data before the first render, so it renders
// synchronously and matches the prerendered HTML. Hydrate only HTML that was
// rendered for this path: the host serves 404.html for every unknown URL, and
// the workspace document has nothing in it to adopt.
preloadRoute(path)
  .catch(() => {})
  .then(() => {
    if (container.dataset.route === path) hydrateRoot(container, app)
    else createRoot(container).render(app)
  })
