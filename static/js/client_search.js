document.addEventListener('DOMContentLoaded', function () {
    // define client form elements to target
    const clientNameInput = document.getElementById('client_name');
    const clientPhoneInput = document.getElementById('client_phone');
    const clientEmailInput = document.getElementById('client_email');

    // listen for user input
    clientNameInput.addEventListener('input', function () {
        const query = clientNameInput.value.trim(); // Make sure there's no extra space

        // fetch data from API endpoint by passing the query client name input
        if (query.length > 2) {
            const fetchUrl = `/api/search_clients/?q=${encodeURIComponent(query)}`; // Safely encode query
            console.log('Fetching from URL:', fetchUrl); // Log the URL
            fetch(fetchUrl)
                .then(response => {
                    console.log('Fetch response:', response);
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                // handle response data
                .then(data => {
                    console.log('Data:', data)
                    // define suggestions div
                    let suggestions = document.getElementById('client-suggestions');
                    // show the div
                    suggestions.classList.add('show');
                    // clear the div first
                    suggestions.innerHTML = '';

                    // loop through the clients filtered/found
                    data.clients.forEach(client => {
                        // create suggestion item div
                        const suggestion = document.createElement('div');
                        suggestion.classList.add('suggestion-item');
                        // show client details
                        suggestion.textContent = `${client.name} (phone:${client.phone}, email:${client.email})`;

                        // Add event listener for hover effect
                        suggestion.addEventListener('mouseenter', function () {
                            clearActiveSuggestion(); // Clear any previously highlighted suggestion
                            suggestion.classList.add('active'); // Highlight current suggestion
                        });

                        // handle click event for the suggestion
                        suggestion.addEventListener('click', function () {
                            clientNameInput.value = client.name;
                            clientPhoneInput.value = client.phone;
                            clientEmailInput.value = client.email;
                            suggestions.innerHTML = ''; // Clear suggestions
                            suggestions.classList.remove('show'); // Hide the dropdown
                        });
                        // append the suggestion item in the suggestions parent div and move to next
                        suggestions.appendChild(suggestion);
                    });
                });
        } else {
            suggestions.innerHTML = '';
            suggestions.classList.remove('show'); // Hide dropdown if query is too short
        }
    });

    // Hide dropdown on mouseleave
    suggestions.addEventListener('mouseleave', function () {
        suggestions.classList.remove('show');
    });

    // Clear previously active suggestion
    function clearActiveSuggestion() {
        const activeItem = document.querySelector('.suggestion-item.active');
        if (activeItem) {
            activeItem.classList.remove('active');
        }
    }

});