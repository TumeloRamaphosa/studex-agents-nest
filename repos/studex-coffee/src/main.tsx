import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import SaB2BOnePager from './SaB2BOnePager.tsx'
import CIIE2026 from './CIIE2026.tsx'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

const router = createBrowserRouter([
  { path: '/', element: <App /> },
  { path: '/b2b', element: <SaB2BOnePager /> },
  { path: '/ciie2026', element: <CIIE2026 /> },
])

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
