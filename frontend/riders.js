// Configuration
const CONFIG = {
    API_BASE: 'http://localhost:5000',
    MAP_DEFAULT_ZOOM: 12,
    MAP_CENTER: [40.7128, -74.0060], // NYC coordinates
    MAX_MARKERS: 1000, // Limit markers for performance
    COLORS: {
        pickup: '#4caf50',
        dropoff: '#f44336',
        route: '#4361ee',
        highlight: '#ffc107'
    }
};

// Global variables
let map;
let markers = [];
let currentMarkers = [];
let mapInitialized = false;

// Initialize the application when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    setupEventListeners();
    // Initial data load
    setTimeout(() => applyFilters(), 500);
});

// Set up event listeners for the UI
function setupEventListeners() {
    // Add event listeners for filter inputs
    const filterInputs = document.querySelectorAll('.filter-group input, .filter-group select');
    filterInputs.forEach(input => {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') applyFilters();
        });
    });

    // Add today's date as default end date
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('filter-end-date').value = today;

    // Set default start date to 30 days ago
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    document.getElementById('filter-start-date').value = thirtyDaysAgo.toISOString().split('T')[0];
}

// Initialize the map
function initMap() {
    if (mapInitialized) return;
    
    map = L.map('map').setView(CONFIG.MAP_CENTER, CONFIG.MAP_DEFAULT_ZOOM);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);
    
    mapInitialized = true;
}

// Main function to apply filters and update the UI
async function applyFilters() {
    try {
        showLoading(true);
        clearMap();
        
        const filters = getCurrentFilters();
        await Promise.all([
            fetchSummaryData(),
            fetchTripsData(filters)
        ]);
        
    } catch (error) {
        console.error('Error applying filters:', error);
        showError('Failed to load data. Please try again.');
    } finally {
        showLoading(false);
    }
}

// Get current filter values
function getCurrentFilters() {
    return {
        start: document.getElementById('filter-start-date').value,
        end: document.getElementById('filter-end-date').value,
        minDistance: document.getElementById('filter-min-km').value,
        maxDistance: document.getElementById('filter-max-km').value,
        limit: document.getElementById('filter-record-limit').value || 100
    };
}

// Fetch and display summary data
async function fetchSummaryData() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/api/summary`);
        if (!response.ok) throw new Error('Failed to fetch summary data');
        
        const data = await response.json();
        updateSummary({
            totalTrips: data.total_trips || 0,
            avgDistance: data.avg_distance_km || 0,
            avgFare: data.avg_fare_per_km || 0
        });
    } catch (error) {
        console.error('Error fetching summary:', error);
        throw error;
    }
}

// Fetch and display trip data
async function fetchTripsData(filters) {
    try {
        const params = new URLSearchParams();
        if (filters.start) params.set('start', filters.start);
        if (filters.end) params.set('end', filters.end);
        if (filters.minDistance) params.set('min_distance', filters.minDistance);
        if (filters.maxDistance) params.set('max_distance', filters.maxDistance);
        params.set('per_page', Math.min(filters.limit, CONFIG.MAX_MARKERS));

        const response = await fetch(`${CONFIG.API_BASE}/api/trips?${params.toString()}`);
        if (!response.ok) throw new Error('Failed to fetch trips data');
        
        const data = await response.json();
        updateMap(data.results || []);
        updateTopRoutes(data.results || []);
        updateTopFares(data.results || []);
        
    } catch (error) {
        console.error('Error fetching trips:', error);
        throw error;
    }
}

// Update the summary section with new data
function updateSummary({ totalTrips, avgDistance, avgFare }) {
    document.getElementById('total-trips').textContent = totalTrips.toLocaleString();
    document.getElementById('avg-distance').textContent = `${avgDistance ? avgDistance.toFixed(2) : 'N/A'} km`;
    document.getElementById('avg-fare').textContent = avgFare ? `$${avgFare.toFixed(2)}` : 'N/A';
}

// Update the map with trip markers
function updateMap(trips) {
    if (!mapInitialized || !trips.length) return;
    
    // Clear existing markers
    clearMap();
    
    // Add new markers
    trips.slice(0, CONFIG.MAX_MARKERS).forEach(trip => {
        addTripToMap(trip);
    });
    
    // Fit map bounds to show all markers
    if (currentMarkers.length > 0) {
        const group = L.featureGroup(currentMarkers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}

// Add a single trip to the map
function addTripToMap(trip) {
    if (!trip.pickup_lat || !trip.pickup_lon) return;
    
    // Add pickup marker
    const pickupMarker = L.circleMarker(
        [trip.pickup_lat, trip.pickup_lon],
        {
            radius: 5,
            fillColor: CONFIG.COLORS.pickup,
            color: '#fff',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        }
    ).addTo(map);
    
    // Add popup with trip details
    pickupMarker.bindPopup(createTripPopup(trip, 'pickup'));
    currentMarkers.push(pickupMarker);
    
    // Add dropoff marker if coordinates exist
    if (trip.dropoff_lat && trip.dropoff_lon) {
        const dropoffMarker = L.circleMarker(
            [trip.dropoff_lat, trip.dropoff_lon],
            {
                radius: 5,
                fillColor: CONFIG.COLORS.dropoff,
                color: '#fff',
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
            }
        ).addTo(map);
        
        dropoffMarker.bindPopup(createTripPopup(trip, 'dropoff'));
        currentMarkers.push(dropoffMarker);
        
        // Add line between pickup and dropoff
        const line = L.polyline(
            [[trip.pickup_lat, trip.pickup_lon], [trip.dropoff_lat, trip.dropoff_lon]],
            { color: CONFIG.COLORS.route, weight: 2, opacity: 0.5 }
        ).addTo(map);
        
        currentMarkers.push(line);
    }
}

// Create HTML content for trip popup
function createTripPopup(trip, type) {
    const date = new Date(trip[`${type}_datetime`] || trip.pickup_datetime);
    const formattedDate = date.toLocaleString();
    const distance = trip.trip_distance_km ? `${trip.trip_distance_km.toFixed(2)} km` : 'N/A';
    const fare = trip.fare_amount ? `$${trip.fare_amount.toFixed(2)}` : 'N/A';
    
    return `
        <div class="popup-content">
            <h4>${type === 'pickup' ? 'Pickup' : 'Drop-off'}</h4>
            <p><strong>Time:</strong> ${formattedDate}</p>
            <p><strong>Distance:</strong> ${distance}</p>
            <p><strong>Fare:</strong> ${fare}</p>
            ${trip.passenger_count ? `<p><strong>Passengers:</strong> ${trip.passenger_count}</p>` : ''}
        </div>
    `;
}

// Update the top routes list
function updateTopRoutes(trips) {
    const routesList = document.getElementById('top-routes-list');
    if (!routesList) return;
    
    // Group trips by route (simplified for example)
    const routeCounts = trips.reduce((acc, trip) => {
        if (!trip.pickup_lat || !trip.dropoff_lat) return acc;
        
        const routeKey = `${trip.pickup_lat.toFixed(2)},${trip.pickup_lon.toFixed(2)}-${trip.dropoff_lat.toFixed(2)},${trip.dropoff_lon.toFixed(2)}`;
        acc[routeKey] = (acc[routeKey] || 0) + 1;
        return acc;
    }, {});
    
    // Sort by count and take top 5
    const topRoutes = Object.entries(routeCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
    
    // Update the UI
    if (topRoutes.length === 0) {
        routesList.innerHTML = '<li>No route data available</li>';
        return;
    }
    
    routesList.innerHTML = topRoutes.map(([route, count]) => {
        const [start, end] = route.split('-');
        return `
            <li>
                <span>${start} → ${end}</span>
                <span class="badge">${count}</span>
            </li>
        `;
    }).join('');
}

// Update the top fares list
function updateTopFares(trips) {
    const faresList = document.getElementById('top-fares-list');
    if (!faresList) return;
    
    // Filter out trips without fare data and sort by fare
    const topFares = trips
        .filter(trip => trip.fare_amount)
        .sort((a, b) => (b.fare_amount || 0) - (a.fare_amount || 0))
        .slice(0, 5);
    
    // Update the UI
    if (topFares.length === 0) {
        faresList.innerHTML = '<li>No fare data available</li>';
        return;
    }
    
    faresList.innerHTML = topFares.map(trip => {
        const date = new Date(trip.pickup_datetime).toLocaleDateString();
        return `
            <li>
                <span>$${trip.fare_amount.toFixed(2)}</span>
                <small>${date}</small>
            </li>
        `;
    }).join('');
}

// Clear all markers from the map
function clearMap() {
    currentMarkers.forEach(marker => {
        if (map.hasLayer(marker)) {
            map.removeLayer(marker);
        }
    });
    currentMarkers = [];
}

// Show/hide loading state
function showLoading(show) {
    const loader = document.querySelector('.loading-overlay') || createLoader();
    loader.style.display = show ? 'flex' : 'none';
}

// Create loading overlay if it doesn't exist
function createLoader() {
    const loader = document.createElement('div');
    loader.className = 'loading-overlay';
    loader.innerHTML = `
        <div class="spinner"></div>
        <p>Loading data...</p>
    `;
    document.body.appendChild(loader);
    return loader;
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    // Add to the page and auto-remove after 5 seconds
    document.body.appendChild(errorDiv);
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Add CSS for loading and error states
const style = document.createElement('style');
style.textContent = `
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.8);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        font-size: 1.2rem;
        color: var(--primary-color);
    }
    
    .spinner {
        border: 4px solid rgba(67, 97, 238, 0.2);
        border-radius: 50%;
        border-top: 4px solid var(--primary-color);
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin-bottom: 1rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .error-message {
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--danger);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .popup-content {
        min-width: 200px;
    }
    
    .popup-content h4 {
        margin: 0 0 0.5rem 0;
        color: var(--primary-color);
    }
    
    .popup-content p {
        margin: 0.25rem 0;
        font-size: 0.9rem;
    }
    
    .badge {
        background: var(--primary-color);
        color: white;
        border-radius: 10px;
        padding: 0.15rem 0.5rem;
        font-size: 0.75rem;
        font-weight: 600;
    }
`;

document.head.appendChild(style);
