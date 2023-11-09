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

    // Function to update the sentiment history panel
    function updatePanelWithData(data) {
        // Clear the panel
        historyPanel.innerHTML = '';

        // Add new entries to the panel, up to a limit of 10 items
        data.entries.slice(0, 10).forEach(entry => {
            const listItem = document.createElement("li");
            listItem.className = "list-group-item";
            listItem.textContent = entry.text + " - Sentiment: " + entry.sentiment;
            historyPanel.appendChild(listItem);
        });

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