import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Outbox from './pages/Outbox'
import Anomalies from './pages/Anomalies'
import Devis from './pages/Devis'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/outbox" element={<Outbox />} />
          <Route path="/anomalies" element={<Anomalies />} />
          <Route path="/devis" element={<Devis />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
