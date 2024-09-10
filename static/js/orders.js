document.addEventListener('DOMContentLoaded', function () {

    const addOrderItemButton = document.getElementById('add-order-item');
    const totalFormsInput = document.getElementById('id_form-TOTAL_FORMS');

    // Handle adding new order item forms
    addOrderItemButton.addEventListener('click', function () {
        const orderItemsContainer = document.getElementById('order-items');
        let newFormIndex = parseInt(totalFormsInput.value);

        // Create a new empty form (with only product and quantity fields)
        let newForm = createNewOrderItemForm(newFormIndex);

        // Append the new form to the formset container
        orderItemsContainer.appendChild(newForm);

        // Populate the product dropdown dynamically
        let productSelect = newForm.querySelector('.product-dropdown');
        populateProductDropdown(productSelect);

        // Increment the total form count
        totalFormsInput.value = newFormIndex + 1;
    });

    // Populate product dropdowns for existing forms on page load
    document.querySelectorAll('.product-dropdown').forEach(selectElement => {
        populateProductDropdown(selectElement);
    });

    // Handle dynamic deletion of order items
    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('delete-order-item')) {
            deleteOrderItem(event.target);
            // update the running total
            updateOrderTotals();
        }
    });

    // add listener for changes to the form (focusing on dropdown selections)
    document.addEventListener('change', function (event) {
        // Handle dynamic product selection and show relevant options/finishes fields
        if (event.target.classList.contains('product-dropdown')) {
            // Call updateProductDetails first, and then updateOrderTotals            
            updateProductDetails(event.target)
                .then(() => {
                    // update the running total
                    updateOrderTotals();
                })
                .catch(error => {
                    console.error('Error in updating totals:', error);
                });
        };

        // Handle dynamic option_values selection and show related finishes fields
        if (event.target.classList.contains('options-dropdown')) {
            updateComponentFinishes(event.target);
        };
    });

    // Trigger update on input event when user is typing (for dynamic updates)
    document.addEventListener('input', function (event) {
        // if a user input is detected in the discount or quantity field
        if (
            event.target.classList.contains('discount-field') ||
            event.target.classList.contains('quantity-field')
        ) {
            // execute the updateItemValue function with 300ms delay
            updateItemValue(event.target)
            // update the running total
            updateOrderTotals();
        }
    });
});

function updateComponentFinishes(target) {
    let optionValueId = target.value;
    let formIndex = target.closest('.order-item-form').getAttribute('data-form-index');
    let compFinishesContainer = document.getElementById(`comp-finishes-container-${formIndex}`);

    if (optionValueId) {
        fetch(`/api/get_component_finishes/${optionValueId}/`)
            .then(response => {
                // Check if the response is OK (status in the range 200-299)
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                // Clear old finishes
                compFinishesContainer.innerHTML = '';
                // Populate finishes dynamically
                data.component_finishes.forEach(finish => {
                    let compFinishHTML = `
                        <div class="form-group">
                            <label for="${finish.component_slug}-${finish.id}">${finish.component_name} ${finish.name}</label>
                            <select class="form-control" name="${finish.component_slug}-${finish.id}">
                                <option value="">Select ${finish.name}</option>
                    `;
                    finish.finish_options.forEach(finishOption => {
                        compFinishHTML += `<option value="${finishOption.id}">${finishOption.name}</option>`;
                    });
                    compFinishHTML += '</select></div>';
                    compFinishesContainer.innerHTML += compFinishHTML;
                });
                if (compFinishesContainer.childElementCount > 0) {
                    // add heading
                    let compFinishesHeading = document.createElement("h5")
                    compFinishesHeading.innerHTML = "<h5>Component Finishes</h5>"
                    compFinishesContainer.prepend(compFinishesHeading)

                    // show the component-finishes-container
                    compFinishesContainer.classList.remove('hidden');
                }
            })
            .catch(error => {
                // Handle any errors that occurred during the fetch
                console.error('There was a problem fetching the component finish options:', error);
            });

    } else {
        // Hide the component finishes containers if no product is selected
        compFinishesContainer.classList.add('hidden');
    }
};

function updateProductDetails(target) {
    let productId = target.value;
    let formIndex = target.closest('.order-item-form').getAttribute('data-form-index');
    let optionsContainer = document.getElementById(`options-container-${formIndex}`);
    let finishesContainer = document.getElementById(`finishes-container-${formIndex}`);
    let basePriceField = document.getElementById(`id_form-${formIndex}-base_price`);
    let discountField = document.getElementById(`id_form-${formIndex}-discount`);
    let itemValueField = document.getElementById(`id_form-${formIndex}-item_value`);

    if (productId) {
        // Return a promise when a productId is present
        return new Promise((resolve, reject) => {
            // fetch product data from the API
            fetch(`/api/get_product_data/${productId}/`)
                .then(response => {
                    // Check if the response is OK (status in the range 200-299)
                    if (!response.ok) {
                        throw new Error('Network response was not ok ' + response.statusText);
                    }
                    return response.json();
                })
                .then(data => {
                    // Set the base price field with the product's base price
                    basePriceField.value = data.base_price;
                    // Calculate the item value automatically
                    let discount = parseFloat(discountField.value) || 0;
                    let basePrice = parseFloat(basePriceField.value) || 0;
                    itemValueField.value = (basePrice - discount).toFixed(2);
                    // Clear old options
                    optionsContainer.innerHTML = '';
                    // Populate options dynamically
                    data.options.forEach(option => {
                        let optionHTML = `
                        <div class="form-group">
                            <label for="option_${option.id}">${option.name}:</label>
                            <select class="form-control options-dropdown" name="option_${option.id}">
                                <option value="">Select ${option.name}</option>
                    `;
                        option.option_values.forEach(optionValue => {
                            optionHTML += `<option value="${optionValue.id}">${optionValue.value}</option>`;
                        });
                        optionHTML += '</select></div>';
                        optionsContainer.innerHTML += optionHTML;
                    });
                    // Show the options container if there are options
                    if (optionsContainer.childElementCount > 0) {
                        // add heading
                        let optionsHeading = document.createElement("h5")
                        optionsHeading.innerHTML = "<h5>Configuration Options</h5>"
                        optionsContainer.prepend(optionsHeading)
                        // Show the options container
                        optionsContainer.classList.remove('hidden');
                    }

                    // Clear old finishes
                    finishesContainer.innerHTML = '';
                    // Populate finishes dynamically
                    data.finishes.forEach(finish => {
                        let finishHTML = `
                        <div class="form-group">
                            <label for="product_finish_${finish.id}">Product ${finish.name}</label>
                            <select class="form-control" name="product_finish_${finish.id}">
                                <option value="">Select ${finish.name}</option>
                    `;
                        finish.finish_options.forEach(finishOption => {
                            finishHTML += `<option value="${finishOption.id}">${finishOption.name}</option>`;
                        });
                        finishHTML += '</select></div>';
                        finishesContainer.innerHTML += finishHTML;
                    });
                    // Show the finishes container if there are finishes
                    if (finishesContainer.childElementCount > 0) {
                        // add heading
                        let finishesHeading = document.createElement("h5")
                        finishesHeading.innerHTML = "<h5>Product Finishes</h5>"
                        finishesContainer.prepend(finishesHeading)
                        // show the finishes container
                        finishesContainer.classList.remove('hidden');
                    }
                    // Once the product details have been updated, resolve the promise
                    resolve();
                })
                .catch(error => {
                    // Handle any errors that occurred during the fetch
                    console.error('There was a problem fetching the product data:', error);
                    reject(error);
                });
        });

    } else {
        // Hide the options and finishes containers if no product is selected
        optionsContainer.classList.add('hidden');
        finishesContainer.classList.add('hidden');
        // set the base price and discount to zero to reset
        basePriceField.value = 0;
        discountField.value = 0;
        itemValueField.value = 0;
        // resolve the promise with an empty selection
        return Promise.resolve();
    }
};

function deleteOrderItem(target) {
    const orderItemsContainer = document.getElementById('order-items');
    let orderItemForm = target.closest('.order-item-form');

    if (orderItemForm) {
        // formset management update
        let formCount = document.getElementById('id_form-TOTAL_FORMS').value - 1
        document.getElementById('id_form-TOTAL_FORMS').setAttribute('value', formCount)

        // remove orderItemForm from container
        orderItemsContainer.removeChild(orderItemForm);

        // Re-index remaining forms to ensure they are correctly numbered
        let orderItemForms = document.querySelectorAll('.order-item-form');
        orderItemForms.forEach((form, index) => {
            form.setAttribute('data-form-index', index);
            // Update Order Item heading
            form.querySelector('h4').innerText = `Order Item #${index+1}`
            // update select and input elements
            form.querySelectorAll('input, select').forEach(field => {
                // Update field names and IDs to maintain the correct formset structure
                field.name = field.name.replace(/form-\d+-/, `form-${index}-`);
                field.id = field.id.replace(/form-\d+-/, `form-${index}-`);
            });
            // update label elements
            form.querySelectorAll('label').forEach(field => {
                // Update for to align label to correct elements
                field.htmlFor = field.htmlFor.replace(/form-\d+-/, `form-${index}-`);
            });
            // update options/finishes containers
            form.querySelectorAll('.form-container').forEach(field => {
                // update container ids
                field.id = field.id.replace(/-container-\d+/, `-container-${index}`);
            });
        });
    }
};

// Function to create a new order item form dynamically (with only product and quantity fields)
function createNewOrderItemForm(index) {
    let newForm = document.createElement('div');
    newForm.classList.add('card', 'mb-3', 'order-item-form');
    newForm.setAttribute('data-form-index', index);
    newForm.innerHTML = `
            <div class="card-body">
                <h4>Order Item #${index+1}</h4>

                <label for="id_form-${index}-product">Product:</label>
                <select class="form-control product-dropdown" id="id_form-${index}-product" name="form-${index}-product">
                    <option value="">Loading products...</option>
                </select>

                <label for="id_form-${index}-base_price">Base price:</label>
                <input type="number" name="form-${index}-base_price" class="form-control" step="0.01" id="id_form-${index}-base_price">
                
                <label for="id_form-${index}-discount">Discount:</label>
                <input type="number" name="form-${index}-discount" value="0.0" class="form-control discount-field" min="0" step="0.01" id="id_form-${index}-discount">
                
                <label for="id_form-${index}-quantity">Quantity:</label>
                <input type="number" class="form-control quantity-field" id="id_form-${index}-quantity" name="form-${index}-quantity" min="1" value="1">

                <label for="id_form-${index}-item_value">Item value:</label>
                <input type="number" name="form-${index}-item_value" class="form-control" readonly="" step="0.01" id="id_form-${index}-item_value">

                <div class="options form-container hidden" id="options-container-${index}"></div>
                <div class="finishes form-container hidden" id="finishes-container-${index}"></div>
                <div class="comp-finishes form-container hidden" id="comp-finishes-container-${index}"></div>

                <button type="button" class="btn btn-danger delete-order-item">Delete</button>
            </div>
        `;
    return newForm;
};

// Function to fetch and populate product dropdowns
function populateProductDropdown(selectElement) {
    fetch('/api/get_products/')
        .then(response => {
            // Check if the response is OK (status in the range 200-299)
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            selectElement.innerHTML = '<option value="">Select a product</option>'; // Reset dropdown
            data.products.forEach(product => {
                let optionHTML = `<option value="${product.id}">${product.name}</option>`;
                selectElement.innerHTML += optionHTML;
            });
        })
        .catch(error => console.error('Error fetching products:', error));
};

function updateOrderTotals() {
    const orderFormOrderValueField = document.getElementById('order_value');
    let totalOrderValue = 0;

    document.querySelectorAll('.order-item-form').forEach((form, index) => {
        let itemValueField = document.getElementById(`id_form-${index}-item_value`)
        let itemValue = parseFloat(itemValueField.value) || 0

        // Sum up item values for the order
        totalOrderValue += itemValue;
    });

    // Update the Order form with the calculated totals
    orderFormOrderValueField.value = totalOrderValue.toFixed(2);
}

function updateItemValue(target) {
    // Recalculate order value on discount change
    if (target.classList.contains('discount-field')) {
        let formIndex = target.name.match(/\d+/)[0];
        let basePriceField = document.getElementById(`id_form-${formIndex}-base_price`);
        let quantityField = document.getElementById(`id_form-${formIndex}-quantity`);
        let itemValueField = document.getElementById(`id_form-${formIndex}-item_value`);
        let discount = parseFloat(target.value) || 0;
        let basePrice = parseFloat(basePriceField.value) || 0;
        let quantity = parseInt(quantityField.value) || 0;
        itemValueField.value = ((basePrice - discount) * quantity).toFixed(2);
    }

    // Recalculate order value on quantity change
    if (target.classList.contains('quantity-field')) {
        let formIndex = target.name.match(/\d+/)[0];
        let basePriceField = document.getElementById(`id_form-${formIndex}-base_price`);
        let discountField = document.getElementById(`id_form-${formIndex}-discount`);
        let itemValueField = document.getElementById(`id_form-${formIndex}-item_value`);
        let quantity = parseInt(target.value) || 0;
        let basePrice = parseFloat(basePriceField.value) || 0;
        let discount = parseFloat(discountField.value) || 0;
        itemValueField.value = ((basePrice - discount) * quantity).toFixed(2);
    }
};