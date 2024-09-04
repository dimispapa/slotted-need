document.addEventListener('DOMContentLoaded', function () {
    // Get all product dropdowns
    const productDropdowns = document.querySelectorAll('.product-dropdown');

    productDropdowns.forEach((dropdown, index) => {
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
                const relatedOptions = options.filter(option => option.product == productId);

                relatedOptions.forEach(option => {
                    let optionSelectHTML = `
                        <div class="col-md-6">
                            <label for="option_${index}_${option.id}" class="form-label">${option.name}</label>
                            <select class="form-control" name="option_${index}_${option.id}" id="option_${index}_${option.id}">
                                <option value="">Select ${option.name}</option>
                    `;

                    optionSelectHTML += '</select></div>';
                    optionContainer.innerHTML += optionSelectHTML;
                });

            }
        });
    });
});