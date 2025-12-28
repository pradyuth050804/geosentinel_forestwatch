import React from 'react';

function InsightsPanel({ explanation }) {
    return (
        <div className="insights-panel">
            <h2>🤖 AI-Powered Analysis</h2>

            <div className="insights-content">
                {explanation.explanation}
            </div>

            {explanation.confidence_score > 0 && (
                <div className="confidence-badge">
                    Confidence Score: {explanation.confidence_score}/100
                </div>
            )}

            {explanation.status === 'error' && (
                <div style={{ marginTop: '1rem', color: 'var(--accent)' }}>
                    ⚠️ AI explanation service unavailable. Please check API configuration.
                </div>
            )}
        </div>
    );
}

export default InsightsPanel;
