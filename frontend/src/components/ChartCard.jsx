import React from 'react'
import './ChartCard.css'

function ChartCard({ title, data, type = 'bar' }) {
  // Simple chart visualization
  const maxValue = Math.max(...data.values)

  if (type === 'pie') {
    const total = data.values.reduce((a, b) => a + b, 0)
    const colors = ['#667eea', '#764ba2', '#f59e0b', '#ef4444']

    return (
      <div className="chart-card">
        <h3>{title}</h3>
        <div className="pie-chart">
          {data.labels.map((label, idx) => {
            const percentage = (data.values[idx] / total) * 100
            return (
              <div
                key={idx}
                className="pie-segment"
                style={{
                  background: colors[idx % colors.length],
                  width: `${percentage}%`
                }}
                title={`${label}: ${percentage.toFixed(1)}%`}
              />
            )
          })}
        </div>
        <div className="legend">
          {data.labels.map((label, idx) => (
            <div key={idx} className="legend-item">
              <span
                className="legend-dot"
                style={{ background: colors[idx % colors.length] }}
              />
              {label}: {data.values[idx]}
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="chart-card">
      <h3>{title}</h3>
      <div className="bar-chart">
        {data.labels.map((label, idx) => (
          <div key={idx} className="bar-item">
            <div className="bar">
              <div
                className="bar-fill"
                style={{ height: `${(data.values[idx] / maxValue) * 100}%` }}
              />
            </div>
            <span className="bar-label">{label}</span>
            <span className="bar-value">{data.values[idx]}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ChartCard
