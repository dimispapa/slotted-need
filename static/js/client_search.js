document.addEventListener('DOMContentLoaded', function () {
    // define client form elements to target
    const clientNameInput = document.getElementById('client_name');
    const clientPhoneInput = document.getElementById('client_phone');
    const clientEmailInput = document.getElementById('client_email');

    // listen for user input
    clientNameInput.addEventListener('input', function () {
        const query = clientNameInput.value;

        // fetch data from API endpoint by passing the query client name input
        if (query.length > 2) {
            fetch(`/api/search_clients/?q=${query}`)
                .then(response => response.json())
                .then(data => {
                    let suggestions = document.getElementById('client-suggestions');
                    // create the div if not found
                    if (!suggestions) {
                        suggestions = document.createElement('div');
                        suggestions.setAttribute('id', 'client-suggestions');
                        clientNameInput.parentNode.appendChild(suggestions);
                    }
                    // clear the div first
                    suggestions.innerHTML = '';

                    // loop through the clients filtered/found
                    data.clients.forEach(client => {
                        // create suggestion item div
                        const suggestion = document.createElement('div');
                        suggestion.classList.add('suggestion-item');
                        // show client details
                        suggestion.textContent = `${client.name} (phone:${client.phone}, email:${client.email})`;
                        // if user clicks in phone or email then clear the suggestions as it means it is attempting to type new
                        suggestion.addEventListener('click', function () {
                            clientPhoneInput.value = client.phone;
                            clientEmailInput.value = client.email;
                            suggestions.innerHTML = ''; // Clear suggestions
                        });
                        // append the suggestion item in the suggestions parent div and move to next
                        suggestions.appendChild(suggestion);
                    });
                });
        }
    });
});