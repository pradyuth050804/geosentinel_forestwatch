import React from 'react';

function ImagePanel({ images, dates }) {
    return (
        <div className="image-panel">
            <div className="image-card">
                <img
                    src={`${images.before}?t=${Date.now()}`}
                    alt="Before deforestation"
                    onClick={() => window.open(images.before, '_blank')}
                    style={{ cursor: 'pointer' }}
                    title="Click to view full size"
                />
                <div className="image-label">
                    📅 Before ({dates.before})
                </div>
            </div>

            <div className="image-card">
                <img
                    src={`${images.after}?t=${Date.now()}`}
                    alt="After deforestation"
                    onClick={() => window.open(images.after, '_blank')}
                    style={{ cursor: 'pointer' }}
                    title="Click to view full size"
                />
                <div className="image-label">
                    📅 After ({dates.after})
                </div>
            </div>

            <div className="image-card">
                <img
                    src={`${images.highlight}?t=${Date.now()}`}
                    alt="Deforestation detection"
                    onClick={() => window.open(images.highlight, '_blank')}
                    style={{ cursor: 'pointer' }}
                    title="Click to view full size"
                />
                <div className="image-label">
                    🔍 Deforestation Detected
                </div>
            </div>
        </div>
    );
}

export default ImagePanel;
