// Update last updated time
function updateTime() {
    const now = new Date();
    document.getElementById('lastUpdated').textContent = now.toLocaleString();
}

// Load stock market data
async function loadStocks() {
    document.getElementById('stocksLoading').style.display = 'block';
    document.getElementById('stocksContent').style.display = 'none';
    
    try {
        const response = await fetch('/api/stocks');
        const data = await response.json();
        
        let html = '';
        for (const [key, stock] of Object.entries(data)) {
            const statusColor = stock.status === 'up' ? 'success' : 'danger';
            const statusIcon = stock.status === 'up' ? '▲' : '▼';
            
            html += `
                <div class="col-md-4 mb-3">
                    <div class="card border-${statusColor}">
                        <div class="card-body">
                            <h6 class="card-title">${stock.name}</h6>
                            <h4 class="mb-2">${stock.value}</h4>
                            <p class="mb-0 text-${statusColor}">
                                ${statusIcon} ${stock.change} (${stock.change_percent})
                            </p>
                        </div>
                    </div>
                </div>
            `;
        }
        
        document.getElementById('stocksContent').innerHTML = html;
        document.getElementById('stocksLoading').style.display = 'none';
        document.getElementById('stocksContent').style.display = 'flex';
    } catch (error) {
        document.getElementById('stocksContent').innerHTML = 
            '<div class="alert alert-danger">Error loading stock data</div>';
        document.getElementById('stocksLoading').style.display = 'none';
        document.getElementById('stocksContent').style.display = 'block';
    }
}

// Load weather data
async function loadWeather() {
    const location = document.getElementById('locationInput').value;
    document.getElementById('weatherLoading').style.display = 'block';
    document.getElementById('weatherContent').innerHTML = '';
    
    try {
        const response = await fetch(`/api/weather?location=${location}`);
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('weatherContent').innerHTML = 
                `<div class="alert alert-danger">${data.error}</div>`;
        } else {
            const iconUrl = `http://openweathermap.org/img/wn/${data.icon}@2x.png`;
            const html = `
                <div class="row align-items-center">
                    <div class="col-md-3 text-center">
                        <img src="${iconUrl}" alt="Weather Icon" style="width: 100px;">
                    </div>
                    <div class="col-md-9">
                        <h4>${data.location}</h4>
                        <h2>${Math.round(data.temperature)}°C</h2>
                        <p class="text-muted text-capitalize">${data.description}</p>
                        <div class="row mt-3">
                            <div class="col-6">
                                <p><i class="bi bi-thermometer-half"></i> Feels like: ${Math.round(data.feels_like)}°C</p>
                            </div>
                            <div class="col-6">
                                <p><i class="bi bi-droplet"></i> Humidity: ${data.humidity}%</p>
                            </div>
                            <div class="col-6">
                                <p><i class="bi bi-wind"></i> Wind: ${data.wind_speed} m/s</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('weatherContent').innerHTML = html;
        }
        
        document.getElementById('weatherLoading').style.display = 'none';
    } catch (error) {
        document.getElementById('weatherContent').innerHTML = 
            '<div class="alert alert-danger">Error loading weather data</div>';
        document.getElementById('weatherLoading').style.display = 'none';
    }
}

// Load news data
async function loadNews() {
    document.getElementById('worldNewsLoading').style.display = 'block';
    document.getElementById('techNewsLoading').style.display = 'block';
    
    try {
        const response = await fetch('/api/news');
        const data = await response.json();
        
        // World News
        let worldNewsHtml = '';
        data.world_news.slice(0, 5).forEach(article => {
            worldNewsHtml += `
                <div class="mb-3 pb-3 border-bottom">
                    <h6><a href="${article.url}" target="_blank" class="text-decoration-none">${article.title}</a></h6>
                    <p class="small text-muted mb-1">${article.source.name} - ${new Date(article.publishedAt).toLocaleDateString()}</p>
                    <p class="small">${article.description || ''}</p>
                </div>
            `;
        });
        
        // Tech News
        let techNewsHtml = '';
        data.tech_news.slice(0, 5).forEach(article => {
            techNewsHtml += `
                <div class="mb-3 pb-3 border-bottom">
                    <h6><a href="${article.url}" target="_blank" class="text-decoration-none">${article.title}</a></h6>
                    <p class="small text-muted mb-1">${article.source.name} - ${new Date(article.publishedAt).toLocaleDateString()}</p>
                    <p class="small">${article.description || ''}</p>
                </div>
            `;
        });
        
        document.getElementById('worldNewsContent').innerHTML = worldNewsHtml;
        document.getElementById('techNewsContent').innerHTML = techNewsHtml;
        
        document.getElementById('worldNewsLoading').style.display = 'none';
        document.getElementById('techNewsLoading').style.display = 'none';
        document.getElementById('worldNewsContent').style.display = 'block';
        document.getElementById('techNewsContent').style.display = 'block';
    } catch (error) {
        document.getElementById('worldNewsContent').innerHTML = 
            '<div class="alert alert-danger">Error loading news</div>';
        document.getElementById('techNewsContent').innerHTML = 
            '<div class="alert alert-danger">Error loading news</div>';
        document.getElementById('worldNewsLoading').style.display = 'none';
        document.getElementById('techNewsLoading').style.display = 'none';
    }
}

// Refresh all data
function refreshAll() {
    updateTime();
    loadStocks();
    loadWeather();
    loadNews();
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    updateTime();
    loadStocks();
    loadWeather();
    loadNews();
    
    // Auto-refresh every 15 minutes
    setInterval(refreshAll, 15 * 60 * 1000);
});