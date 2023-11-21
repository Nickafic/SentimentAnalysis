// JavaScript code to load next and previous pages of sentiment history
document.addEventListener("DOMContentLoaded", function() {
    // Set initial page number
    let currentPage = 1;

    // Elements
    const historyPanel = document.getElementById("sentiment-history-panel");
    const prevPageButton = document.getElementById("prev-page");
    const nextPageButton = document.getElementById("next-page");

    // Function to load sentiment history data for a given page
    function loadSentimentHistory(page) {
        fetch(`/get_sentiment_history?page=${page}`)
            .then(response => response.json())
            .then(data => {
                updatePanelWithData(data);
            })
            .catch(error => {
                console.error('Error loading sentiment history:', error);
            });
    }

    // Function to update the sentiment history panel with a table
    function updatePanelWithData(data) {
        // Clear the panel
        historyPanel.innerHTML = '';

        // Create a table element
        const table = document.createElement("table");
        table.className = "table table-striped";

        // Create the table header
        const thead = document.createElement("thead");
        thead.className = "thead-dark";
        const headerRow = document.createElement("tr");

        // Add header cells (excluding 'Index')
        ['Text', 'Sentiment'].forEach(function(headerText) {
            const headerCell = document.createElement("th");
            headerCell.textContent = headerText;
            headerRow.appendChild(headerCell);
        });

        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Create the table body
        const tbody = document.createElement("tbody");

        // Add rows to the table
        data.entries.slice(0, 10).forEach(entry => {
            const row = document.createElement("tr");

            // Add data cells (excluding 'index')
            ['text', 'sentiment'].forEach(function(key) {
                const cell = document.createElement("td");
                cell.textContent = entry[key];
                row.appendChild(cell);
            });

            tbody.appendChild(row);
        });

        table.appendChild(tbody);

        // Append the table to the panel
        historyPanel.appendChild(table);

        // Update current page
        currentPage = data.page;

        // Enable/disable navigation buttons
        prevPageButton.disabled = currentPage === 1;
        nextPageButton.disabled = !data.hasMorePages;
    }

    // Load initial sentiment history data
    loadSentimentHistory(currentPage);

    // Event listeners for navigation buttons
    prevPageButton.addEventListener("click", function() {
        if (currentPage > 1) {
            loadSentimentHistory(currentPage - 1);
        }
    });

    nextPageButton.addEventListener("click", function() {
        loadSentimentHistory(currentPage + 1);
    });
});
