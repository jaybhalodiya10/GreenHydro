# GeoH2 Frontend

## Overview
A modern, interactive web frontend for the GeoH2 hydrogen cost analysis platform. The frontend provides an intuitive interface for viewing analysis results, running new analyses, and exploring visualizations.

## Features

### 🎨 **Modern UI/UX**
- Responsive design that works on all devices
- Beautiful gradient backgrounds and smooth animations
- Interactive hover effects and smooth transitions
- Professional color scheme and typography

### 📊 **Dashboard**
- Real-time backend status monitoring
- Quick action buttons for analysis and data refresh
- System health indicators
- Project statistics overview

### 📈 **Analysis Results**
- Hydrogen cost comparison (trucking vs pipeline)
- Detailed cost breakdowns with ranges
- Cost savings calculations and percentages
- Analysis summary with key metrics

### 🖼️ **Visualizations**
- Interactive chart gallery
- High-quality PNG image display
- Download functionality for all charts
- Descriptive information for each visualization

### 🔧 **Interactive Features**
- Smooth scrolling navigation
- Active section highlighting
- Loading modals for long operations
- Toast notifications for user feedback
- Responsive grid layouts

## File Structure

```
frontend/
├── index.html          # Main HTML file
├── styles.css          # CSS styling and animations
├── app.js             # JavaScript functionality and backend communication
└── README.md          # This file
```

## Technologies Used

- **HTML5**: Semantic markup and structure
- **CSS3**: Modern styling with CSS Grid, Flexbox, and animations
- **JavaScript (ES6+)**: Modern JavaScript with async/await
- **Bootstrap 5**: Responsive framework and components
- **Font Awesome**: Icon library for UI elements
- **Chart.js**: Chart rendering (ready for future enhancements)

## Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Backend server running on `http://localhost:8000`

### Installation
1. Ensure the backend server is running
2. Open `index.html` in your web browser
3. The frontend will automatically connect to the backend

### Usage

#### 1. **Dashboard**
- View system status and health indicators
- Check data availability and analysis status
- Use quick action buttons for common tasks

#### 2. **Analysis Results**
- Compare hydrogen costs between transport methods
- View cost ranges and averages
- See cost savings calculations
- Check analysis summary information

#### 3. **Visualizations**
- Browse through all generated charts
- Download high-resolution images
- Read descriptions of each visualization

#### 4. **Running Analysis**
- Click "Run Full Analysis" to start a new analysis
- Monitor progress with loading modal
- Receive notifications on completion

## Backend Integration

The frontend communicates with the backend through REST API endpoints:

### API Endpoints Used
- `GET /api/health` - Check backend status
- `GET /api/status` - Get project status
- `GET /api/results` - Get analysis results
- `GET /api/plots` - Get visualization files
- `POST /api/analyze` - Run full analysis

### Data Flow
1. **Initial Load**: Frontend checks backend status and loads available data
2. **Real-time Updates**: Status indicators show current system state
3. **User Actions**: Buttons trigger backend operations
4. **Results Display**: Data is fetched and displayed in real-time

## Customization

### Colors
Modify CSS variables in `styles.css`:
```css
:root {
    --primary-color: #0d6efd;
    --secondary-color: #6c757d;
    --success-color: #198754;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    --info-color: #0dcaf0;
}
```

### Backend URL
Change the backend URL in `app.js`:
```javascript
this.backendUrl = 'http://localhost:8000'; // Change this
```

### Chart Information
Modify chart descriptions in `app.js`:
```javascript
getChartInfo(plotName) {
    const chartInfo = {
        'lcoh_comparison.png': {
            title: 'LCOH Comparison',
            description: 'Your custom description here'
        }
        // ... more charts
    };
}
```

## Browser Support

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## Performance Features

- **Lazy Loading**: Images load as needed
- **Smooth Animations**: CSS transitions for better UX
- **Responsive Design**: Optimized for all screen sizes
- **Efficient DOM**: Minimal DOM manipulation
- **Error Handling**: Graceful fallbacks for failures

## Development

### Adding New Features
1. **New Sections**: Add HTML in `index.html`
2. **Styling**: Add CSS in `styles.css`
3. **Functionality**: Add JavaScript in `app.js`

### Testing
- Test on different screen sizes
- Verify backend connectivity
- Check error handling scenarios
- Validate user interactions

### Debugging
- Open browser developer tools
- Check console for errors
- Monitor network requests
- Verify API responses

## Troubleshooting

### Common Issues

#### Backend Connection Failed
- Ensure backend server is running on port 8000
- Check firewall settings
- Verify network connectivity

#### Images Not Loading
- Check backend plots directory
- Verify file permissions
- Check browser console for errors

#### Analysis Not Starting
- Verify backend status is "Connected"
- Check backend logs for errors
- Ensure all required data files exist

### Debug Mode
Enable debug logging in `app.js`:
```javascript
// Add this line for debug output
console.log('Debug mode enabled');
```

## Future Enhancements

- **Real-time Charts**: Interactive Chart.js visualizations
- **Data Export**: CSV/Excel download functionality
- **User Authentication**: Login and user management
- **Advanced Filtering**: Search and filter capabilities
- **Mobile App**: React Native or PWA version
- **Real-time Updates**: WebSocket integration
- **Multi-language**: Internationalization support

## Contributing

1. Follow existing code style and patterns
2. Test changes across different browsers
3. Ensure responsive design compatibility
4. Update documentation as needed
5. Test backend integration thoroughly

## License

MIT License - see LICENSE file in project root

## Support

For issues or questions:
1. Check browser console for errors
2. Verify backend server status
3. Review API endpoint responses
4. Check network connectivity
5. Consult backend documentation 