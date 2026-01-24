import React, { useState, useEffect } from 'react'
import StatCard from '../components/StatCard'
import ChartCard from '../components/ChartCard'
import { TrendingUp, Droplets, Users, Calendar } from 'lucide-react'
import './Dashboard.css'

function Dashboard() {
  const [stats, setStats] = useState({
    totalWashes: 245,
    revenue: 12500,
    customers: 89,
    avgRating: 4.8
  })

  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Simulate API call
    setLoading(true)
    setTimeout(() => setLoading(false), 500)
  }, [])

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Welcome back! Here's your car wash performance overview.</p>
      </div>

      <div className="stats-grid">
        <StatCard
          icon={<Droplets />}
          label="Total Washes"
          value={stats.totalWashes}
          change="+12.5%"
          changeType="positive"
        />
        <StatCard
          icon={<TrendingUp />}
          label="Revenue"
          value={`$${stats.revenue.toLocaleString()}`}
          change="+8.2%"
          changeType="positive"
        />
        <StatCard
          icon={<Users />}
          label="Active Customers"
          value={stats.customers}
          change="+3.1%"
          changeType="positive"
        />
        <StatCard
          icon={<Calendar />}
          label="Avg Rating"
          value={stats.avgRating}
          change="+0.3"
          changeType="positive"
        />
      </div>

      <div className="charts-grid">
        <ChartCard
          title="Weekly Performance"
          data={{
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            values: [24, 32, 28, 45, 38, 52, 48]
          }}
        />
        <ChartCard
          title="Service Distribution"
          data={{
            labels: ['Basic', 'Premium', 'Deluxe', 'VIP'],
            values: [45, 35, 15, 5]
          }}
          type="pie"
        />
      </div>
    </div>
  )
}

export default Dashboard
