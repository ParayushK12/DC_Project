import React, { useState, useRef, useEffect } from 'react'
import mermaid from 'mermaid'

export default function App() {
  const [mode, setMode] = useState('text') // 'text' or 'pdf'
  const [text, setText] = useState('')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [mermaidCode, setMermaidCode] = useState('')
  const previewRef = useRef(null)

  useEffect(() => {
    mermaid.initialize({ startOnLoad: false, securityLevel: 'loose' })
  }, [])

  useEffect(() => {
    renderMermaid(mermaidCode)
  }, [mermaidCode])

  const renderMermaid = async (code) => {
    const container = previewRef.current
    if (!container) return

    if (!code) {
      container.innerHTML = '<div class="placeholder">Diagram preview will appear here</div>'
      return
    }

    try {
      // create a wrapper and call mermaid.render
      const id = 'mermaid-' + Date.now()
      const { svg } = await mermaid.render(id, code)
      container.innerHTML = svg
    } catch (e) {
      container.innerHTML = '<pre class="error">Failed to render mermaid diagram: ' + e.message + '</pre>'
    }
  }

  const handleFileChange = (e) => {
    setFile(e.target.files?.[0] || null)
  }

  const submitText = async () => {
    setError(null)
    if (!text.trim()) {
      setError('Please enter some text')
      return
    }
    setLoading(true)
    try {
      const res = await fetch('http://localhost:5000/api/process-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || JSON.stringify(data))
      const code = data.mermaid_code || data.raw_mermaid || ''
      setMermaidCode(code)
    } catch (e) {
      setError('Error: ' + e.message)
    } finally {
      setLoading(false)
    }
  }

  const submitPdf = async () => {
    setError(null)
    if (!file) {
      setError('Please choose a PDF file')
      return
    }
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file)
      const res = await fetch('http://localhost:5000/api/process-pdf', {
        method: 'POST',
        body: fd
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || JSON.stringify(data))
      const code = data.mermaid_code || data.raw_mermaid || ''
      setMermaidCode(code)
    } catch (e) {
      setError('Error: ' + e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header>
        <h1>LLM → Blockdiagram (React)</h1>
        <p className="muted">Enter simple text or upload a PDF. The backend will summarize and generate Mermaid diagram code.</p>
      </header>

      <section className="controls">
        <div className="mode-toggle">
          <label>
            <input type="radio" checked={mode === 'text'} onChange={() => setMode('text')} /> Text
          </label>
          <label>
            <input type="radio" checked={mode === 'pdf'} onChange={() => setMode('pdf')} /> Document (PDF)
          </label>
        </div>

        {mode === 'text' ? (
          <div className="text-mode">
            <textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Paste your story or text here" />
            <div className="actions">
              <button onClick={submitText} disabled={loading}>{loading ? 'Processing…' : 'Generate Diagram'}</button>
            </div>
          </div>
        ) : (
          <div className="pdf-mode">
            <input type="file" accept="application/pdf" onChange={handleFileChange} />
            <div className="actions">
              <button onClick={submitPdf} disabled={loading}>{loading ? 'Processing…' : 'Upload & Generate'}</button>
            </div>
          </div>
        )}

        {error && <div className="error">{error}</div>}
      </section>

      <section className="preview">
        <h2>Diagram Preview</h2>
        <div className="preview-area" ref={previewRef} />
      </section>

      <footer>
        <small className="muted">Backend expected at http://localhost:5000 — make sure your Flask server is running.</small>
      </footer>
    </div>
  )
}
