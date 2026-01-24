import React from 'react'
import './StatCard.css'

function StatCard({ icon, label, value, change, changeType }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">
        {icon}
      </div>
      <div className="stat-content">
        <p className="stat-label">{label}</p>
        <p className="stat-value">{value}</p>
        <p className={`stat-change ${changeType}`}>
          {changeType === 'positive' ? '↑' : '↓'} {change}
        </p>
      </div>
    </div>
  )
}

export default StatCard
