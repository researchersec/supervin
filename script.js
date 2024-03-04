document.addEventListener("DOMContentLoaded", function() {
    fetch('prices.json') // Load data from exported JSON file
        .then(response => response.json())
        .then(data => {
            // Calculate price changes for last week, last month, and last year
            const currentDate = new Date();
            const lastWeekDate = new Date(currentDate.getTime() - (7 * 24 * 60 * 60 * 1000));
            const lastMonthDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, currentDate.getDate());
            const lastYearDate = new Date(currentDate.getFullYear() - 1, currentDate.getMonth(), currentDate.getDate());
            
            data.forEach(entry => {
                entry.lastWeekChange = calculatePriceChange(entry.price_1, entry.timestamp, lastWeekDate);
                entry.lastMonthChange = calculatePriceChange(entry.price_1, entry.timestamp, lastMonthDate);
                entry.lastYearChange = calculatePriceChange(entry.price_1, entry.timestamp, lastYearDate);
            });

            const table = $('#priceTable').DataTable({
                data: data,
                columns: [
                    { title: "Name" },
                    { title: "Price 1" },
                    { title: "Price 6" },
                    { title: "Timestamp" },
                    { title: "Last Week Change" },
                    { title: "Last Month Change" },
                    { title: "Last Year Change" }
                ]
            });
        })
        .catch(error => console.error('Error fetching data:', error));
});

// Function to calculate price change
function calculatePriceChange(currentPrice, timestamp, comparisonDate) {
    // Convert timestamp to Date object
    const entryDate = new Date(timestamp);

    // Check if the entry date is within the comparison period
    if (entryDate >= comparisonDate) {
        return "N/A"; // No change if within the comparison period
    } else {
        // Calculate price change percentage
        const changePercentage = ((currentPrice - entryPrice) / entryPrice) * 100;
        return `${changePercentage.toFixed(2)}%`;
    }
}
