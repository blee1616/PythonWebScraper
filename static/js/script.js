document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const analyzeBtn = document.getElementById('analyzeBtn');
    const tickerInputContainer = document.getElementById('tickerInputContainer');
    const tickerInput = document.getElementById('tickerInput');
    const submitBtn = document.getElementById('submitBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const results = document.getElementById('results');
    const currentPrice = document.getElementById('currentPrice');
    const chartContainer = document.getElementById('chartContainer');
    const articles = document.getElementById('articles');
    
    // Chart instance
    let priceChart = null;

    // Event listeners
    analyzeBtn.addEventListener('click', function() {
        analyzeBtn.classList.add('hidden');
        tickerInputContainer.classList.remove('hidden');
        tickerInput.focus();
    });
    
    submitBtn.addEventListener('click', submitTicker);
    tickerInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            submitTicker();
        }
    });

    function submitTicker() {
        const ticker = tickerInput.value.trim().toUpperCase();
        if (!ticker) {
            alert('Please enter a valid ticker symbol');
            return;
        }
        
        // Show loading indicator
        tickerInputContainer.classList.add('hidden');
        loadingIndicator.classList.remove('hidden');
        results.classList.add('hidden');
        
        // Clear previous results
        currentPrice.textContent = '';
        articles.innerHTML = '';
        if (priceChart) {
            priceChart.destroy();
            priceChart = null;
        }
        
        // Fetch data from backend
        fetch(`/analyze/${ticker}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                displayResults(data, ticker);
            })
            .catch(error => {
                console.error('Error fetching stock data:', error);
                alert('Error fetching stock data. Please try again.');
                
                // Reset UI
                loadingIndicator.classList.add('hidden');
                analyzeBtn.classList.remove('hidden');
            });
    }
    
    function displayResults(data, ticker) {
        // Hide loading indicator
        loadingIndicator.classList.add('hidden');
        results.classList.remove('hidden');
        
        // Show the analyze button again for another search
        analyzeBtn.classList.remove('hidden');
        
        // Display current price
        currentPrice.textContent = `$${data.current_price}`;
        
        // Display chart
        displayChart(data.historical_prices, ticker);
        
        // Display articles
        displayArticles(data.articles);
    }
    
    function displayChart(historicalData, ticker) {
        const ctx = document.createElement('canvas');
        chartContainer.innerHTML = '';
        chartContainer.appendChild(ctx);
        
        priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: historicalData.dates,
                datasets: [{
                    label: `${ticker} Stock Price`,
                    data: historicalData.prices,
                    backgroundColor: 'rgba(52, 152, 219, 0.2)',
                    borderColor: 'rgba(52, 152, 219, 1)',
                    borderWidth: 2,
                    pointRadius: 3,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Price (USD)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                }
            }
        });
    }
    
    function displayArticles(articleData) {
        if (articleData.length === 0) {
            articles.innerHTML = '<p>No articles found for this stock.</p>';
            return;
        }
        
        articleData.forEach(item => {
            const article = document.createElement('div');
            article.className = 'article';
            
            const sentimentClass = item.sentiment.toLowerCase();
            
            article.innerHTML = `
                <div class="article-title">
                    ${item.title}
                    <span class="sentiment ${sentimentClass}">${item.sentiment}</span>
                </div>
            `;
            
            articles.appendChild(article);
        });
    }
});