document.addEventListener('DOMContentLoaded', function () {

    // fetch the options data using the view function API
    fetch('/api/get_options_data/')
        .then(response => {
            // error handling
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // parse data into variables
            const options = data.options;
            const optionValues = data.option_values;
            const finishes = data.finishes;
            const finishOptions = data.finish_options;

            // Get all product dropdowns
            const productDropdowns = document.querySelectorAll('.product-dropdown');

            // loop through the dropdowns (as it is a formset can have more than one product dropdowns)
            productDropdowns.forEach((dropdown, index) => {
                // add an event listener for changes
                dropdown.addEventListener('change', function () {
                    const productId = this.value;
                    // select the relevant option and finish containers (adding 1 to index as JS uses 0-based indexing)
                    const optionContainer = document.getElementById(`option-container-${index + 1}`);
                    const finishContainer = document.getElementById(`finish-container-${index + 1}`);

                    // Clear previous options and finishes
                    optionContainer.innerHTML = '';
                    finishContainer.innerHTML = '';

                    if (productId) {
                        // Add option dropdowns based on selected product
                        const relatedOptions = options.filter(option => option.product_id == productId);

                        relatedOptions.forEach(option => {
                            let optionSelectHTML = `
                        <div class="col-md-6">
                            <label for="option_${index}_${option.id}" class="form-label">${option.name}</label>
                            <select class="form-control" name="option_${index}_${option.id}" id="option_${index}_${option.id}">
                                <option value="">Select ${option.name}</option>
                    `;

                            // Add option values related to this option
                            const relatedOptionValues = optionValues.filter(ov => ov.option_id == option.id);
                            relatedOptionValues.forEach(optionValue => {
                                optionSelectHTML += `<option value="${optionValue.id}">${optionValue.value}</option>`;
                            });

                            optionSelectHTML += '</select></div>';
                            optionContainer.innerHTML += optionSelectHTML;
                        });

                    }
                });
            });
        })
        .catch(error => {
            console.error('Error fetching options data:', error);
        });


});