document.addEventListener('DOMContentLoaded', function () {

    const orderItemsContainer = document.getElementById('order-items');
    const addOrderItemButton = document.getElementById('add-order-item');
    const totalFormsInput = document.getElementById('id_form-TOTAL_FORMS');

    // Function to fetch and populate product dropdowns
    function populateProductDropdown(selectElement) {
        fetch('/api/get_products/')
            .then(response => response.json())
            .then(data => {
                selectElement.innerHTML = '<option value="">Select a product</option>'; // Reset dropdown
                data.products.forEach(product => {
                    const optionHTML = `<option value="${product.id}">${product.name}</option>`;
                    selectElement.innerHTML += optionHTML;
                });
            })
            .catch(error => console.error('Error fetching products:', error));
    }

    // Function to create a new order item form dynamically (with only product and quantity fields)
    function createNewOrderItemForm(index) {
        const newForm = document.createElement('div');
        newForm.classList.add('card', 'mb-3', 'order-item-form');
        newForm.innerHTML = `
            <div class="card-body">
                <div class="form-group">
                    <label for="id_form-${index}-product">Product</label>
                    <select class="form-control product-dropdown" id="id_form-${index}-product" name="form-${index}-product">
                        <option value="">Loading products...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="id_form-${index}-quantity">Quantity</label>
                    <input type="number" class="form-control" id="id_form-${index}-quantity" name="form-${index}-quantity" min="1" value="1">
                </div>
                <div class="options-container" id="options-container-${index}" style="display: none;"></div>
                <div class="finishes-container" id="finishes-container-${index}" style="display: none;"></div>

                <button type="button" class="btn btn-danger delete-order-item" data-form-index="${index}">Delete</button>
            </div>
        `;
        return newForm;
    }


    // Handle adding new order item forms
    addOrderItemButton.addEventListener('click', function () {
        const currentFormCount = parseInt(totalFormsInput.value);

        // Create a new empty form (with only product and quantity fields)
        const newForm = createNewOrderItemForm(currentFormCount);

        // Append the new form to the formset container
        orderItemsContainer.appendChild(newForm);

        // Populate the product dropdown dynamically
        const productSelect = newForm.querySelector('.product-dropdown');
        populateProductDropdown(productSelect);

        // Increment the total form count
        totalFormsInput.value = currentFormCount + 1;
    });

    // Populate product dropdowns for existing forms on page load
    document.querySelectorAll('.product-dropdown').forEach(selectElement => {
        populateProductDropdown(selectElement);
    });

    // Handle dynamic deletion of order items
    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('delete-order-item')) {
            const formIndex = event.target.getAttribute('data-form-index');
            const orderItemForm = event.target.closest('.order-item-form');

            if (orderItemForm) {
                orderItemsContainer.removeChild(orderItemForm);

                formCount--;
                document.getElementById('id_form-TOTAL_FORMS').value = formCount;

                // Re-index remaining forms to ensure they are correctly numbered
                const orderItemForms = document.querySelectorAll('.order-item-form');
                orderItemForms.forEach((form, index) => {
                    form.querySelector('.delete-order-item').setAttribute('data-form-index', index);
                    form.querySelectorAll('input, select').forEach(field => {
                        // Update field names and IDs to maintain the correct formset structure
                        field.name = field.name.replace(/form-\d+-/, `form-${index}-`);
                        field.id = field.id.replace(/form-\d+-/, `form-${index}-`);
                    });
                });
            }
        }
    });

    // Handle dynamic product selection and show options/finishes fields
    document.addEventListener('change', function (event) {
        if (event.target.classList.contains('product-dropdown')) {
            const productId = event.target.value;
            const formIndex = event.target.name.match(/\d+/)[0];
            const optionsContainer = document.getElementById(`options-container-${formIndex}`);
            const finishesContainer = document.getElementById(`finishes-container-${formIndex}`);

            if (productId) {
                fetch(`/api/get_product_options/${productId}/`)
                    .then(response => response.json())
                    .then(data => {
                        // Populate options dynamically
                        optionsContainer.innerHTML = ''; // Clear old options
                        data.options.forEach(option => {
                            const optionHTML = `
                                <div class="form-group">
                                    <label for="option_${option.id}">${option.name}</label>
                                    <select class="form-control" name="option_${option.id}">
                                        <option value="">Select ${option.name}</option>
                            `;
                            option.option_values.forEach(optionValue => {
                                optionHTML += `<option value="${optionValue.id}">${optionValue.value}</option>`;
                            });
                            optionHTML += '</select></div>';
                            optionsContainer.innerHTML += optionHTML;
                        });

                        // Populate finishes dynamically
                        finishesContainer.innerHTML = ''; // Clear old finishes
                        data.finishes.forEach(finish => {
                            const finishHTML = `
                                <div class="form-group">
                                    <label for="finish_${finish.id}">${finish.name}</label>
                                    <select class="form-control" name="finish_${finish.id}">
                                        <option value="">Select ${finish.name}</option>
                            `;
                            finish.finish_options.forEach(finishOption => {
                                finishHTML += `<option value="${finishOption.id}">${finishOption.name}</option>`;
                            });
                            finishHTML += '</select></div>';
                            finishesContainer.innerHTML += finishHTML;
                        });

                        // Show the options and finishes containers
                        optionsContainer.style.display = 'block';
                        finishesContainer.style.display = 'block';
                    });
            } else {
                // Hide the options and finishes containers if no product is selected
                optionsContainer.style.display = 'none';
                finishesContainer.style.display = 'none';
            }
        }
    });

    // Handle dynamic deletion of order items
    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('delete-order-item')) {
            const form = event.target.closest('.order-item-form');
            form.remove();

            // Decrease the form count
            const currentFormCount = parseInt(totalFormsInput.value) - 1;
            totalFormsInput.value = currentFormCount;
        }
    });
});