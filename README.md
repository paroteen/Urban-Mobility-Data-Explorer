# Urban Mobility Data Explorer

A comprehensive full-stack application for analyzing and visualizing New York City taxi trip data. This project demonstrates end-to-end data processing, from raw data ingestion to interactive visualization.

## Team Members
- Kayisire Kira Armel
- Israel Ayong
- Sheja Dorian
- Kenny Crepin Rukoro

## Video Demonstration
[![Project Demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg)](https://youtu.be/YOUR_VIDEO_ID)

## Features

### Data Processing Pipeline
- **Data Cleaning**: Robust preprocessing of raw NYC taxi trip data
- **Data Validation**: Ensures data quality and consistency
- **ETL Process**: Efficient extraction, transformation, and loading of trip data

### Backend (Flask API)
- RESTful API endpoints for data retrieval
- Efficient querying with SQLite
- CORS support for frontend integration
- Data aggregation and analysis endpoints

### Frontend (Interactive Dashboard)
- Interactive map visualization using Leaflet
- Real-time data filtering and visualization
- Responsive design for all device sizes
- Intuitive user interface for data exploration

## Tech Stack

### Backend
- Python 3.10+
- Flask
- SQLite3
- Pandas (for data processing)
- Flask-CORS

### Frontend
- HTML5, CSS3, JavaScript (ES6+)
- Leaflet.js for interactive maps
- Chart.js for data visualization
- Modern CSS with Flexbox/Grid

## Project Structure

```
.
├── backend/
│   ├── __pycache__/
│   ├── api_routes.py       # API endpoint definitions
│   ├── app.py              # Flask application
│   ├── clean_data.py       # Data cleaning and preprocessing
│   ├── clean_transform.py  # Data transformation logic
│   ├── data_cleaning.py    # Data quality functions
│   ├── database.py         # Database connection and queries
│   ├── init_db.py          # Database initialization
│   ├── load_data.py        # Data loading utilities
│   ├── requirements.txt    # Python dependencies
│   └── schema.sql          # Database schema
├── data/
│   ├── logs/               # Processing logs and reports
│   ├── processed/          # Cleaned and processed data
│   └── raw/                # Raw data files (gitignored)
├── database/
│   ├── cleaned_data_10k.csv
│   ├── nyc_taxi.db         # SQLite database
│   └── schema.sql
├── docs/
│   ├── ERD Diagram.jpeg
│   ├── cleaned_schema.md   # Data model documentation
│   └── validation_rules.md # Data validation rules
├── frontend/
│   ├── riders.html         # Main dashboard
│   ├── riders.css          # Styling
│   └── riders.js           # Frontend logic
├── .gitignore
├── README.md
└── requirements.txt
```

## Installation

### Prerequisites
- Python 3.10 or higher
- Node.js and npm (for frontend development)
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/paroteen/Urban-Mobility-Data-Explorer.git
   cd Urban-Mobility-Data-Explorer
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python backend/init_db.py
   python backend/load_data.py
   ```

4. **Run the Flask server**
   ```bash
   python backend/app.py
   ```

5. **Open the frontend**
   - Open `frontend/riders.html` in a modern web browser
   - The frontend expects the backend to be running at `http://localhost:5000`

## Usage

1. **Viewing Trip Data**
   - The map displays pickup and dropoff locations
   - Click on markers to view trip details
   - Use the date range picker to filter trips by date

2. **Analyzing Patterns**
   - The dashboard shows key metrics and visualizations
   - Filter data using the sidebar controls
   - Hover over charts for detailed information

## Data Model

### Key Entities
- **Trips**: Core entity containing trip details
- **Locations**: Pickup and dropoff points
- **Time Slots**: Temporal analysis of trip patterns

### Database Schema
See [docs/cleaned_schema.md](docs/cleaned_schema.md) for detailed schema documentation.

## API Endpoints

### Trips
- `GET /api/trips` - Get paginated list of trips
- `GET /api/trips/<trip_id>` - Get details of a specific trip
- `GET /api/trips/stats` - Get trip statistics

### Analytics
- `GET /api/analytics/hourly` - Hourly trip patterns
- `GET /api/analytics/daily` - Daily trip patterns
- `GET /api/analytics/locations` - Popular locations

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- [NYC Taxi & Limousine Commission](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page) for the dataset
- [OpenStreetMap](https://www.openstreetmap.org/) for map tiles
- [Leaflet](https://leafletjs.com/) for interactive maps
- [Chart.js](https://www.chartjs.org/) for data visualization
