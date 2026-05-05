import { useState } from 'react'
import './App.css'

function formatValue(value) {
  if (value === null || value === undefined || value === '') {
    return 'Not provided'
  }

  if (Array.isArray(value)) {
    return value.length ? value.join(', ') : 'None'
  }

  if (typeof value === 'object') {
    return JSON.stringify(value)
  }

  return String(value)
}

function formatErrorDetail(detail) {
  if (!detail) {
    return null
  }

  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.msg || item?.message || String(item))
      .join(', ')
  }

  if (typeof detail === 'object') {
    return detail.message || JSON.stringify(detail)
  }

  return String(detail)
}

function App() {
  const [rawNotes, setRawNotes] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/structure-notes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ raw_notes: rawNotes }),
      });

      if (!response.ok) {
        let message = 'Failed to process notes. Is the backend running?';
        try {
          const errorData = await response.json();
          message = formatErrorDetail(errorData.detail) || message;
        } catch {
          // Keep the generic message when the backend does not return JSON.
        }
        throw new Error(message);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="container">
      <header>
        <h1>Clinic Assistant</h1>
        <p>Medical documentation helper</p>
        <p className="disclaimer">For documentation support only. This tool does not provide diagnosis or treatment advice.</p>
      </header>

      <main className="main-content">
        {/* LEFT COLUMN: Input */}
        <div className="input-section">
          <h2>Rough Notes</h2>
          <textarea 
            placeholder="Paste or type rough patient notes here..."
            value={rawNotes}
            onChange={(e) => setRawNotes(e.target.value)}
            disabled={isLoading}
          />
          <button 
            onClick={handleSubmit} 
            disabled={isLoading}
          >
            {isLoading ? 'Processing...' : 'Structure Notes'}
          </button>
          
          {error && <div className="error-message">Error: {error}</div>}
        </div>

        <div className="result-section">
          <h2>Structured Output</h2>
          
          {!result && !isLoading && (
            <p className="placeholder-text">Submit notes to see the structured output here.</p>
          )}

          {isLoading && (
            <div className="loading-spinner">Processing </div>
          )}

          {result && (
            <div className="result-card">
              <div className="result-block">
                <h3>Structured Summary</h3>
                <p>{result.structured_summary || 'No summary returned.'}</p>
              </div>

              <div className="result-block">
                <h3>Extracted Details</h3>
                {result.extracted_details && typeof result.extracted_details === 'object' ? (
                  <dl className="details-list">
                    {Object.entries(result.extracted_details).map(([label, value]) => (
                      <div className="detail-row" key={label}>
                        <dt>{label}</dt>
                        <dd>{formatValue(value)}</dd>
                      </div>
                    ))}
                  </dl>
                ) : (
                  <p>No details returned.</p>
                )}
              </div>

              <div className="result-block missing">
                <h3>Missing Information Flagged</h3>
                {result.missing_fields?.length ? (
                  <ul>
                    {result.missing_fields.map((field, index) => (
                      <li key={index}>{field}</li>
                    ))}
                  </ul>
                ) : (
                  <p>No missing fields flagged.</p>
                )}
              </div>

              {/* {result.sources?.length > 0 && (
                <div className="result-block">
                  <h3>Retrieved Reference Snippets</h3>
                  <ul className="sources-list">
                    {result.sources.map((s, index) => (
                      <li key={index}>
                        <strong>{s.source?.split('/').pop() || 'unknown'}</strong>
                        <p>{s.snippet}…</p>
                      </li>
                    ))}
                  </ul>
                </div>
              )} */}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
