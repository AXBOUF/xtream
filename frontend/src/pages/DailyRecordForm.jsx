import React, { useState } from 'react'
import FormField from '../components/FormField'
import Button from '../components/Button'
import { Check, AlertCircle } from 'lucide-react'
import './DailyRecordForm.css'

function DailyRecordForm() {
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    carPlate: '',
    customerName: '',
    phone: '',
    serviceType: 'basic',
    waterUsage: '',
    chemicalUsage: '',
    duration: '',
    notes: ''
  })

  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    // Simulate API call
    setTimeout(() => {
      console.log('Form Data:', formData)
      setLoading(false)
      setSubmitted(true)

      // Reset form after 2 seconds
      setTimeout(() => {
        setFormData({
          date: new Date().toISOString().split('T')[0],
          carPlate: '',
          customerName: '',
          phone: '',
          serviceType: 'basic',
          waterUsage: '',
          chemicalUsage: '',
          duration: '',
          notes: ''
        })
        setSubmitted(false)
      }, 2000)
    }, 1000)
  }

  return (
    <div className="form-page">
      <div className="form-header">
        <h1>Daily Car Wash Record</h1>
        <p>Record daily wash details and track resource usage</p>
      </div>

      {submitted && (
        <div className="success-message">
          <Check size={24} />
          <span>Record submitted successfully!</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="daily-form">
        <div className="form-section">
          <h2>Basic Information</h2>
          <div className="form-grid">
            <FormField
              label="Date"
              type="date"
              name="date"
              value={formData.date}
              onChange={handleChange}
              required
            />
            <FormField
              label="Car Plate"
              type="text"
              name="carPlate"
              placeholder="Enter car plate number"
              value={formData.carPlate}
              onChange={handleChange}
              required
            />
            <FormField
              label="Customer Name"
              type="text"
              name="customerName"
              placeholder="Enter customer name"
              value={formData.customerName}
              onChange={handleChange}
              required
            />
            <FormField
              label="Phone Number"
              type="tel"
              name="phone"
              placeholder="Enter phone number"
              value={formData.phone}
              onChange={handleChange}
            />
          </div>
        </div>

        <div className="form-section">
          <h2>Service Details</h2>
          <div className="form-grid">
            <FormField
              label="Service Type"
              type="select"
              name="serviceType"
              value={formData.serviceType}
              onChange={handleChange}
              options={[
                { value: 'basic', label: 'Basic Wash' },
                { value: 'premium', label: 'Premium Wash' },
                { value: 'deluxe', label: 'Deluxe Wash' },
                { value: 'vip', label: 'VIP Service' }
              ]}
            />
            <FormField
              label="Duration (minutes)"
              type="number"
              name="duration"
              placeholder="Enter duration"
              value={formData.duration}
              onChange={handleChange}
              min="0"
            />
          </div>
        </div>

        <div className="form-section">
          <h2>Resource Usage</h2>
          <div className="form-grid">
            <FormField
              label="Water Usage (liters)"
              type="number"
              name="waterUsage"
              placeholder="Enter water usage"
              value={formData.waterUsage}
              onChange={handleChange}
              min="0"
            />
            <FormField
              label="Chemical Usage (liters)"
              type="number"
              name="chemicalUsage"
              placeholder="Enter chemical usage"
              value={formData.chemicalUsage}
              onChange={handleChange}
              min="0"
            />
          </div>
        </div>

        <div className="form-section">
          <FormField
            label="Notes"
            type="textarea"
            name="notes"
            placeholder="Add any additional notes..."
            value={formData.notes}
            onChange={handleChange}
          />
        </div>

        <div className="form-actions">
          <Button
            type="submit"
            loading={loading}
            className="btn-primary"
          >
            Submit Record
          </Button>
          <Button
            type="button"
            className="btn-secondary"
            onClick={() => setFormData({
              date: new Date().toISOString().split('T')[0],
              carPlate: '',
              customerName: '',
              phone: '',
              serviceType: 'basic',
              waterUsage: '',
              chemicalUsage: '',
              duration: '',
              notes: ''
            })}
          >
            Clear Form
          </Button>
        </div>
      </form>
    </div>
  )
}

export default DailyRecordForm
