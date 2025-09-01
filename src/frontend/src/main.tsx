import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
// import DadaistApp from './DadaistApp.tsx'
// import ProfessionalApp from './ProfessionalApp.tsx'
// import TestApp from './TestApp.tsx'
import DashboardApp from './DashboardApp.tsx'

// Switch between app versions:
// - DadaistApp: Artistic, chaotic design with randomized elements
// - ProfessionalApp: Clean, conventional design for productivity focus  
// - DashboardApp: Full dashboard with real backend data integration

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <DashboardApp />
  </StrictMode>,
)
