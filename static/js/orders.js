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
                    let optionHTML = `<option value="${product.id}">${product.name}</option>`;
                    selectElement.innerHTML += optionHTML;
                });
            })
            .catch(error => console.error('Error fetching products:', error));
    }

    // Function to create a new order item form dynamically (with only product and quantity fields)
    function createNewOrderItemForm(index) {
        let newForm = document.createElement('div');
        newForm.classList.add('card', 'mb-3', 'order-item-form');
        newForm.innerHTML = `
            <div class="card-body">
                <h4>Order Item #${index+1}</h4>
                <div class="form-group">
                    <label for="id_form-${index}-product">Product:</label>
                    <select class="form-control product-dropdown" id="id_form-${index}-product" name="form-${index}-product">
                        <option value="">Loading products...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="id_form-${index}-quantity">Quantity:</label>
                    <input type="number" class="form-control" id="id_form-${index}-quantity" name="form-${index}-quantity" min="1" value="1">
                </div>
                <div class="options-container hidden" id="options-container-${index}"></div>
                <div class="finishes-container hidden" id="finishes-container-${index}"></div>

                <button type="button" class="btn btn-danger delete-order-item" data-form-index="${index}">Delete</button>
            </div>
        `;
        return newForm;
    }


    // Handle adding new order item forms
    addOrderItemButton.addEventListener('click', function () {
        let currentFormCount = parseInt(totalFormsInput.value);

        // Create a new empty form (with only product and quantity fields)
        let newForm = createNewOrderItemForm(currentFormCount);

        // Append the new form to the formset container
        orderItemsContainer.appendChild(newForm);

        // Populate the product dropdown dynamically
        let productSelect = newForm.querySelector('.product-dropdown');
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
            let formIndex = event.target.getAttribute('data-form-index');
            let orderItemForm = event.target.closest('.order-item-form');

            if (orderItemForm) {
                orderItemsContainer.removeChild(orderItemForm);
                
                let formCount = document.getElementById('id_form-TOTAL_FORMS').value--
                document.getElementById('id_form-TOTAL_FORMS').setAttribute('value', formCount)

                // Re-index remaining forms to ensure they are correctly numbered
                let orderItemForms = document.querySelectorAll('.order-item-form');
                orderItemForms.forEach((form, index) => {
                    form.querySelector('.delete-order-item').setAttribute('data-form-index', index);
                    form.querySelectorAll('input, select').forEach(field => {
                        // Update field names and IDs to maintain the correct formset structure
                        field.name = field.name.replace(/form-\d+-/, `form-${index}-`);
                        field.id = field.id.replace(/form-\d+-/, `form-${index}-`);
                    // Update Order Item heading
                    form.querySelector('h4').innerText = `Order Item #${index+1}`

                    });
                });
            }
        }
    });

    // Handle dynamic product selection and show options/finishes fields
    document.addEventListener('change', function (event) {
        if (event.target.classList.contains('product-dropdown')) {
            let productId = event.target.value;
            let formIndex = event.target.name.match(/\d+/)[0];
            let optionsContainer = document.getElementById(`options-container-${formIndex}`);
            let finishesContainer = document.getElementById(`finishes-container-${formIndex}`);
            debugger;
            if (productId) {
                fetch(`/api/get_product_options/${productId}/`)
                    .then(response => {
                        // Check if the response is OK (status in the range 200-299)
                        if (!response.ok) {
                            throw new Error('Network response was not ok ' + response.statusText);
                        }
                        return response.json();
                    })
                    .then(data => {
                        debugger;
                        // Populate options dynamically
                        optionsContainer.innerHTML = ''; // Clear old options
                        data.options.forEach(option => {
                            let optionHTML = `
                                <div class="form-group">
                                    <label for="option_${option.id}">${option.name}:</label>
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
                            let finishHTML = `
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
                        optionsContainer.classList.remove('hidden');
                        finishesContainer.classList.remove('hidden');
                    })
                    .catch(error => {
                        // Handle any errors that occurred during the fetch
                        console.error('There was a problem with the fetch operation:', error);
                    });

            } else {
                // Hide the options and finishes containers if no product is selected
                optionsContainer.classList.add('hidden');
                finishesContainer.classList.add('hidden');
            }
        }
    });

    // Handle dynamic deletion of order items
    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('delete-order-item')) {
            let form = event.target.closest('.order-item-form');
            form.remove();

            // Decrease the form count
            let currentFormCount = parseInt(totalFormsInput.value) - 1;
            totalFormsInput.value = currentFormCount;
        }
    });
});