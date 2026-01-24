# Xtream Wash - Modern React Frontend

A modern, responsive car wash management dashboard built with React, featuring a sleek UI with multiple pages for dashboard analytics, daily records, and reports.

## Features

✨ **Modern Design**
- Clean, minimalist interface with gradient backgrounds
- Responsive grid layouts
- Smooth animations and transitions
- Dark mode support

📊 **Dashboard**
- Real-time statistics cards
- Interactive charts (bar & pie charts)
- Performance metrics and KPIs

📝 **Daily Record Form**
- Comprehensive form for logging car washes
- Multiple service types
- Resource usage tracking
- Form validation

📈 **Reports & Analytics**
- Weekly and monthly reports
- Detailed performance metrics
- Service type breakdown
- Revenue tracking

🎨 **Components**
- StatCard - Display key metrics
- FormField - Reusable form inputs
- Button - Action buttons with loading states
- ChartCard - Data visualization
- Navigation - Responsive navigation bar

## Tech Stack

- **React 18** - UI library
- **React Router v6** - Client-side routing
- **Vite** - Fast build tool
- **CSS3** - Modern styling with variables
- **Lucide React** - Beautiful icons

## Installation

```bash
cd frontend
npm install
```

## Development

```bash
npm run dev
```

The app will open at `http://localhost:3000`

## Build

```bash
npm run build
```

Output will be in the `dist/` directory.

## Project Structure

```
src/
├── components/       # Reusable components
│   ├── Navigation.jsx
│   ├── StatCard.jsx
│   ├── FormField.jsx
│   ├── Button.jsx
│   └── ChartCard.jsx
├── pages/           # Page components
│   ├── Dashboard.jsx
│   ├── DailyRecordForm.jsx
│   └── Reports.jsx
├── App.jsx          # Main app component
└── index.css        # Global styles
```

## Features Included

✅ Multiple pages with React Router
✅ Form handling and submission
✅ Responsive design (mobile-friendly)
✅ Dark mode toggle
✅ Interactive charts
✅ Loading states
✅ Success notifications
✅ CSS animations and transitions

## Customization

### Colors
Edit the CSS variables in `src/index.css`:

```css
:root {
  --primary: #667eea;
  --primary-dark: #764ba2;
  /* ... more variables */
}
```

### API Integration
Replace mock data in page components with real API calls:

```javascript
useEffect(() => {
  fetch('/api/dashboard')
    .then(res => res.json())
    .then(data => setStats(data))
}, [])
```

## Future Enhancements

- [ ] Connect to backend API
- [ ] User authentication
- [ ] Real-time data updates
- [ ] Export reports to PDF
- [ ] Advanced filtering and search
- [ ] Mobile app version
- [ ] WebSocket integration for live updates
