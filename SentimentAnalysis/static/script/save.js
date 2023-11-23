document.addEventListener('DOMContentLoaded', function () {
    // Set initial page number
    let currentPage = 1;

    // Elements
    const accordionContainer = document.getElementById('accordion-container');
    const prevPageButton = document.getElementById('prev-page2');
    const nextPageButton = document.getElementById('next-page2');

    // Function to load accordion items for a given page
    function loadAccordionItems(page) {
        fetch(`/paginate?page=${page}&items_per_page=5`)
            .then(response => response.json())
            .then(data => {
                generateAccordion(data.labels);
                currentPage = page;
                updateNavigationButtons(data.totalPages);
            })
            .catch(error => {
                console.error('Error loading accordion items:', error);
            });
    }

    // Function to generate accordion items
    function generateAccordion(data) {
        accordionContainer.innerHTML = ''; // Clear previous accordions

        data.forEach((item, index) => {
            const { id, label } = item;

            const accordionItem = document.createElement('div');
            accordionItem.classList.add('accordion-item');
            accordionItem.setAttribute('data-accordion-id', id);

            accordionItem.innerHTML = `
                <h2 class="accordion-header" id="heading${index}">
                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${index}" aria-expanded="false" aria-controls="collapse${index}">
                        ${label}
                    </button>
                </h2>
                <div id="collapse${index}" class="accordion-collapse collapse" aria-labelledby="heading${index}" data-bs-parent="#accordionExample">
                    <div class="accordion-body">
                        <div id="tableContainer${index}"></div>
                    </div>
                </div>
            `;

            accordionContainer.appendChild(accordionItem);

            // Add event listener for accordion expansion
            accordionItem.querySelector('.accordion-button').addEventListener('click', () => {
                if (!accordionItem.getAttribute('data-table-loaded')) {
                    fetch(`/get_table_data?id=${id}`)
                        .then(response => response.json())
                        .then(tableData => {
                            const tableContainer = document.getElementById(`tableContainer${index}`);
                            tableContainer.innerHTML = generateTableHTML(tableData);
                            accordionItem.setAttribute('data-table-loaded', 'true');
                        })
                        .catch(error => console.error('Error:', error));
                }
            });
        });
    }

    // Function to generate table HTML
    function generateTableHTML(data) {
        const tableRows = data.map(pair => `<tr><td>${pair.text}</td><td>${pair.sentiment}</td></tr>`);
        return `<table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Text</th>
                            <th>Sentiment</th>
                        </tr>
                    </thead>
                    <tbody>${tableRows.join('')}</tbody>
                </table>`;
    }

    // Function to update navigation buttons
    function updateNavigationButtons(totalPages) {
        prevPageButton.disabled = currentPage === 1;
        nextPageButton.disabled = currentPage === totalPages;
    }

    // Load initial accordion items
    loadAccordionItems(currentPage);

    // Event listeners for navigation buttons
    prevPageButton.addEventListener('click', function () {
        if (currentPage > 1) {
            loadAccordionItems(currentPage - 1);
        }
    });

    nextPageButton.addEventListener('click', function () {
        loadAccordionItems(currentPage + 1);
    });
});


// document.addEventListener('DOMContentLoaded', function () {
//     const accordionContainer = document.getElementById('accordion-container');
//     const paginationContainer = document.querySelector('.pagination');
//     const itemsPerPage = 5;

//     function generateAccordion(data) {
//         accordionContainer.innerHTML = ''; // Clear previous accordions

//         data.forEach((item, index) => {
//             const { id, label } = item; // Destructuring assignment

//             const accordionItem = document.createElement('div');
//             accordionItem.classList.add('accordion-item');
//             accordionItem.setAttribute('data-accordion-id', id);

//             accordionItem.innerHTML = `
//                 <h2 class="accordion-header" id="heading${index}">
//                     <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${index}" aria-expanded="false" aria-controls="collapse${index}">
//                         ${label}
//                     </button>
//                 </h2>
//                 <div id="collapse${index}" class="accordion-collapse collapse" aria-labelledby="heading${index}" data-bs-parent="#accordionExample">
//                     <div class="accordion-body">
//                         <div id="tableContainer${index}"></div>
//                     </div>
//                 </div>
//             `;

//             accordionContainer.appendChild(accordionItem);

//             // Add event listener for accordion expansion
//             accordionItem.querySelector('.accordion-button').addEventListener('click', () => {
//                 // Check if the table is already loaded
//                 if (!accordionItem.getAttribute('data-table-loaded')) {
//                     // Make an AJAX request to the Flask route to get table data
//                     fetch(`/get_table_data?id=${id}`)
//                         .then(response => response.json())
//                         .then(tableData => {
//                             // Generate and display the table
//                             const tableContainer = document.getElementById(`tableContainer${index}`);
//                             tableContainer.innerHTML = generateTableHTML(tableData);
//                             accordionItem.setAttribute('data-table-loaded', 'true');
//                         })
//                         .catch(error => console.error('Error:', error));
//                 }
//             });
//         });
//     }

//     function generateTableHTML(data) {
//         // Generate your table HTML based on the data from the Flask route
//         // Assuming each data entry is a pair with 'sentiment' and 'text'
//         const tableRows = data.map(pair => `<tr><td>${pair.text}</td><td>${pair.sentiment}</td></tr>`);
//         return `<table class="table table-striped">
//                     <thead>
//                         <tr>
//                             <th>Text</th>
//                             <th>Sentiment</th>
//                         </tr>
//                     </thead>
//                     <tbody>${tableRows.join('')}</tbody>
//                 </table>`;
//     }

//     function generatePaginationLinks(totalPages) {
//         paginationContainer.innerHTML = ''; // Clear previous pagination links
//         for (let i = 1; i <= totalPages; i++) {
//             const pageItem = `<li class="page-item"><a class="page-link" href="#" onclick="paginateAccordions(${i})">${i}</a></li>`;
//             paginationContainer.innerHTML += pageItem;
//         }
//     }

//     function paginateAccordions(page) {
//         // Make an AJAX request to the Flask route
//         fetch(`/paginate?page=${page}&items_per_page=${itemsPerPage}`)
//             .then(response => response.json())
//             .then(data => {
//                 generateAccordion(data.labels);
//                 generatePaginationLinks(data.totalPages);
//             })
//             .catch(error => console.error('Error:', error));
//     }

//     paginateAccordions(1); // Display initial accordions
// });