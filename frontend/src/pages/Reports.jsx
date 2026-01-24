import React, { useState } from 'react'
import './Reports.css'
import { BarChart3, PieChart, TrendingUp } from 'lucide-react'

function Reports() {
  const [timeRange, setTimeRange] = useState('week')

  const reportData = {
    week: {
      totalWashes: 245,
      waterSaved: 1200,
      revenue: 3500,
      avgDuration: 28
    },
    month: {
      totalWashes: 980,
      waterSaved: 4800,
      revenue: 14000,
      avgDuration: 27
    }
  }

  const current = reportData[timeRange]

  return (
    <div className="reports-page">
      <div className="reports-header">
        <h1>Reports & Analytics</h1>
        <p>Track performance metrics and trends over time</p>
      </div>

      <div className="time-selector">
        <button
          className={`time-btn ${timeRange === 'week' ? 'active' : ''}`}
          onClick={() => setTimeRange('week')}
        >
          Weekly
        </button>
        <button
          className={`time-btn ${timeRange === 'month' ? 'active' : ''}`}
          onClick={() => setTimeRange('month')}
        >
          Monthly
        </button>
      </div>

      <div className="reports-grid">
        <div className="report-card">
          <div className="report-icon">
            <TrendingUp />
          </div>
          <div className="report-content">
            <h3>Total Washes</h3>
            <p className="report-value">{current.totalWashes}</p>
            <span className="report-meta">+15% from previous period</span>
          </div>
        </div>

        <div className="report-card">
          <div className="report-icon">
            <BarChart3 />
          </div>
          <div className="report-content">
            <h3>Water Usage</h3>
            <p className="report-value">{current.waterSaved}L</p>
            <span className="report-meta">-5% compared to last period</span>
          </div>
        </div>

        <div className="report-card">
          <div className="report-icon">
            <PieChart />
          </div>
          <div className="report-content">
            <h3>Total Revenue</h3>
            <p className="report-value">${current.revenue.toLocaleString()}</p>
            <span className="report-meta">+12% growth</span>
          </div>
        </div>

        <div className="report-card">
          <div className="report-icon">
            <BarChart3 />
          </div>
          <div className="report-content">
            <h3>Avg Duration</h3>
            <p className="report-value">{current.avgDuration} min</p>
            <span className="report-meta">-2 min improvement</span>
          </div>
        </div>
      </div>

      <div className="detailed-report">
        <h2>Service Type Performance</h2>
        <table className="report-table">
          <thead>
            <tr>
              <th>Service Type</th>
              <th>Count</th>
              <th>Revenue</th>
              <th>Avg Duration</th>
              <th>Rating</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Basic Wash</td>
              <td>120</td>
              <td>$1,200</td>
              <td>20 min</td>
              <td>⭐⭐⭐⭐ (4.2)</td>
            </tr>
            <tr>
              <td>Premium Wash</td>
              <td>85</td>
              <td>$1,700</td>
              <td>35 min</td>
              <td>⭐⭐⭐⭐⭐ (4.8)</td>
            </tr>
            <tr>
              <td>Deluxe Wash</td>
              <td>30</td>
              <td>$900</td>
              <td>45 min</td>
              <td>⭐⭐⭐⭐⭐ (4.9)</td>
            </tr>
            <tr>
              <td>VIP Service</td>
              <td>10</td>
              <td>$700</td>
              <td>60 min</td>
              <td>⭐⭐⭐⭐⭐ (5.0)</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Reports
