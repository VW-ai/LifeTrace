import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
// import DadaistApp from './DadaistApp.tsx'
import ProfessionalApp from './ProfessionalApp.tsx'

// Switch between design systems by commenting/uncommenting:
// - DadaistApp: Artistic, chaotic design with randomized elements
// - ProfessionalApp: Clean, conventional design for productivity focus

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ProfessionalApp />
  </StrictMode>,
)
