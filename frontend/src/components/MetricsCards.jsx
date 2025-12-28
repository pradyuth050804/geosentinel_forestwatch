import React from 'react';

function MetricsCards({ metrics }) {
    const formatNumber = (num) => {
        return new Intl.NumberFormat('en-US', {
            maximumFractionDigits: 2
        }).format(num);
    };

    const cards = [
        {
            icon: '🌳',
            value: `${formatNumber(metrics.deforested_area_hectares)} ha`,
            label: 'Deforested Area',
            subtitle: `${formatNumber(metrics.deforested_area_m2)} m²`
        },
        {
            icon: '📊',
            value: `${formatNumber(metrics.forest_loss_percentage)}%`,
            label: 'Forest Loss',
            subtitle: `of total ${formatNumber(metrics.total_area_hectares)} ha`
        },
        {
            icon: '🔢',
            value: metrics.number_of_patches,
            label: 'Deforestation Patches',
            subtitle: `Largest: ${formatNumber(metrics.largest_patch_hectares)} ha`
        },
        {
            icon: '✅',
            value: `${formatNumber(metrics.intact_forest_hectares)} ha`,
            label: 'Intact Forest',
            subtitle: `${formatNumber(100 - metrics.forest_loss_percentage)}% remaining`
        }
    ];

    return (
        <div className="metrics-grid">
            {cards.map((card, index) => (
                <div key={index} className="metric-card">
                    <div className="metric-icon">{card.icon}</div>
                    <div className="metric-value">{card.value}</div>
                    <div className="metric-label">{card.label}</div>
                    {card.subtitle && (
                        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                            {card.subtitle}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}

export default MetricsCards;
