import React from 'react'
import './Button.css'

function Button({
  children,
  type = 'button',
  className = 'btn-primary',
  loading = false,
  disabled = false,
  onClick,
  ...props
}) {
  return (
    <button
      type={type}
      className={`button ${className} ${loading ? 'loading' : ''}`}
      disabled={loading || disabled}
      onClick={onClick}
      {...props}
    >
      {loading ? (
        <>
          <span className="spinner"></span>
          Loading...
        </>
      ) : (
        children
      )}
    </button>
  )
}

export default Button
