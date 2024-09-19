// Global constants definition for common Bootstrap style classes used accross
const OPTION_COL_STYLES = ['col-12', 'col-sm-6', 'col-md-4', 'col-lg-3', 'shadow', 'border',
    'mb-2', 'mb-md-3', 'pt-1', 'pt-md-2', 'rounded'
];

const OPTION_GROUP_STYLES = "col-12 form-group mb-2 mb-md-3";

document.addEventListener('DOMContentLoaded', function () {

    // ************** SECTION A: FUNCTION DEFINITIONS ********************************************************************

    // Define function to fetch and populate product dropdowns
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

    // Define function to update product details based on product selection
    function updateProductDetails(target) {

        let productId = target.value;
        let orderItem = target.closest('.order-item-form');
        let formIndex = orderItem.getAttribute('data-form-index');
        let optionsContainer = orderItem.querySelector('.options-form-container')
        // let finishesContainer = document.getElementById(`finishes-container-${formIndex}`);
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

                        // Populate product-level finishes dynamically
                        updateProductFinishes(data, productId, formIndex, optionsContainer);

                        // Populate options (and add listener to populate the selection's associated finishes) dynamically
                        populateProductOptions(data, productId, formIndex, optionsContainer);

                        if (optionsContainer.childElementCount > 0) {
                            // Show the options container
                            optionsContainer.classList.remove('d-none');
                        };

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
            // Hide the options and finishes container if no product is selected
            optionsContainer.classList.add('d-none');
            finishesContainer.classList.remove('d-none');
            // set the base price and discount to zero to reset
            basePriceField.value = 0;
            discountField.value = 0;
            itemValueField.value = 0;
            // resolve the promise with an empty selection
            return Promise.resolve();
        }
    };

    // Define function to populate product options
    function populateProductOptions(data, productId, formIndex, optionsContainer) {
        // Populate options dynamically
        if (data.options && data.options.length > 0) {
            data.options.forEach(option => {
                // create columns for options
                let optionCol = document.createElement('div');
                optionCol.classList.add(...OPTION_COL_STYLES);

                let optionDiv = document.createElement('div');
                optionDiv.classList.add('row');
                let optionDivHTML = `
                                <div class="${OPTION_GROUP_STYLES}">
                                    <label for="option-${formIndex}-${option.id}" class="form-label requiredField">${option.name}<span class="asteriskField">*</span></label>
                                    <select class="form-select options-dropdown" name="form-${formIndex}-option_${option.id}"
                                    id="option-${formIndex}-${option.id}" required aria-required="true">
                                        <option value="">------------</option>
                                </div>
                        `;
                option.option_values.forEach(optionValue => {
                    optionDivHTML += `<option value="${optionValue.id}">${optionValue.value}</option>`;
                });
                optionDivHTML += '</select>';
                optionDiv.innerHTML = optionDivHTML;
                optionCol.appendChild(optionDiv);

                // Create a finish row
                let finishRow = document.createElement('div');
                finishRow.classList.add('row');
                finishRow.id = `finish-${formIndex}-${option.id}`;
                optionCol.appendChild(finishRow);

                // append the column to the container
                optionsContainer.appendChild(optionCol);

                // Fetch finishes dynamically when the option value changes
                document.getElementById(`option-${formIndex}-${option.id}`).addEventListener('change', function () {
                    updateFinishes(formIndex, productId, option.id, this.value);
                });
            });
        }
    }

    // Define function to update product finishes
    function updateProductFinishes(data, productId, formIndex, optionsContainer) {
        if (data.component_finishes && data.component_finishes.length > 0) {
            // create a column for product finishes
            let finishCol = document.createElement('div');
            // add column styles from list constant
            finishCol.classList.add(...OPTION_COL_STYLES);
            // Create a finish div row
            let finishDiv = document.createElement('div');
            finishDiv.classList.add('row');
            // Populate component-level finishes (not driven by config options) dynamically
            data.component_finishes.forEach(finish => {
                let finishDivHTML = `
                            <div class="${OPTION_GROUP_STYLES}">
                                <label for="finish-${formIndex}-${finish.id}-${finish.component_id}" class="form-label">${finish.component_name} ${finish.name}</label>
                                <select class="form-select comp-finish-dropdown-${formIndex}" name="form-${formIndex}-component_finish-${finish.component_id}"
                                id="finish-${formIndex}-${finish.id}-${finish.component_id}">
                                    <option value="">------------</option>
                            </div>
                    `;
                finish.options.forEach(finishOption => {
                    finishDivHTML += `<option value="${finishOption.id}">${finishOption.name}</option>`;
                });
                finishDivHTML += '</select>';
                finishDiv.innerHTML += finishDivHTML;
                finishCol.appendChild(finishDiv);
            });

            // append the column to the container
            optionsContainer.appendChild(finishCol);

            // Add event listeners to each comp-finish dropdown to handle the deselection of others
            let targetClass = `.comp-finish-dropdown-${formIndex}`;
            document.querySelectorAll(targetClass).forEach(compFinishDropdown => {
                compFinishDropdown.addEventListener('change', function () {
                    deselectOtherFinishes(compFinishDropdown, targetClass);
                });
            });
        }
    }

    // Define function to update finishes based on selected option
    function updateFinishes(formIndex, productId, optionId, optionValueId) {

        let finishRow = document.getElementById(`finish-${formIndex}-${optionId}`);

        // Check if an actual option value was selected
        if (optionValueId) {
            fetch(`/api/get_finishes/${productId}/${optionValueId}/`)
                .then(response => {
                    // Check if the response is OK (status in the range 200-299)
                    if (!response.ok) {
                        throw new Error('Network response was not ok ' + response.statusText);
                    }
                    return response.json();
                })
                .then(data => {
                    // Clear old finishes
                    finishRow.innerHTML = '';
                    // Populate finishes dynamically
                    data.component_finishes.forEach(finish => {
                        let finishHTML = `
                            <div class="${OPTION_GROUP_STYLES}">
                                <label for="finish-${formIndex}-${optionValueId}-${finish.id}" class="form-label text-dark">${finish.name}</label>
                                <select class="form-select finish-dropdown-${formIndex}" id="finish-${formIndex}-${optionValueId}-${finish.id}"
                                name="form-${formIndex}-option_finish_component-${finish.component_id}">
                                    <option value="">------------</option>
                            </div>
                        `;
                        finish.finish_options.forEach(finishOption => {
                            finishHTML += `<option value="${finishOption.id}">${finishOption.name}</option>`;
                        });
                        finishHTML += '</select>';
                        finishRow.innerHTML += finishHTML;
                    });

                    // Add event listeners to each finish dropdown to handle the deselection of others
                    let targetClass = `.finish-dropdown-${formIndex}`;
                    document.querySelectorAll(targetClass).forEach(finishDropdown => {
                        finishDropdown.addEventListener('change', function () {
                            deselectOtherFinishes(finishDropdown, targetClass);
                        });
                    });

                })
                .catch(error => {
                    // Handle any errors that occurred during the fetch
                    console.error('There was a problem fetching the finish options:', error);
                });

        } else {
            // Hide the component finishes containers if no product is selected
            finishRow.classList.add('d-none');
        };
    };

    // Define function to deselect other finishes in the same option container
    function deselectOtherFinishes(selectedDropdown, targetClass) {
        // get the grandparent div container
        let grandParentDiv = selectedDropdown.parentElement.parentElement;
        // Loop through all finish dropdowns within the same finishRow
        grandParentDiv.querySelectorAll(targetClass).forEach(dropdown => {
            // If it's not the dropdown that was selected, reset its value
            if (dropdown !== selectedDropdown) {
                dropdown.value = '';
            }
        });
    }

    // Define function to create a new order item form dynamically (with only product and quantity fields)
    function addNewOrderItemForm() {

        const totalFormsInput = document.getElementById('id_form-TOTAL_FORMS');
        const orderItemsContainer = document.getElementById('order-items');
        // Get the current form count which will also be the index of the new form (as we use zero index for IDs of form elements)
        let newFormIndex = formCount = parseInt(totalFormsInput.value);
        let itemNum = newFormIndex + 1; // increment the item number showing on the heading

        // Clone the empty form template. Replace placeholders with appropriate index values and item heading number
        let newFormHtml = document.getElementById('empty-form-template').innerHTML.replace(/__prefix__/g, newFormIndex)
        newFormHtml = newFormHtml.replace(/__itemnum__/g, itemNum).replace(/form--/g, `form-${newFormIndex}-`);

        // Append the new form to the container
        orderItemsContainer.insertAdjacentHTML('beforeend', newFormHtml);

        // Increment the total forms count
        totalFormsInput.value = formCount + 1;
    };

    // Define function that deletes an order item and remaining items index
    function deleteOrderItem(target) {
        const orderItemsContainer = document.getElementById('order-items');
        let orderItemForm = target.closest('.order-item-form');

        if (orderItemForm) {
            // formset management update
            let newFormCount = document.getElementById('id_form-TOTAL_FORMS').value - 1
            document.getElementById('id_form-TOTAL_FORMS').setAttribute('value', newFormCount)

            // remove orderItemForm from container
            orderItemsContainer.removeChild(orderItemForm);

            // Re-index remaining forms to ensure they are correctly numbered
            // Select all elements with class .order-item-form but exclude those inside #empty-form-template with CSS pseudo-class selector
            let orderItemForms = document.querySelectorAll('.order-item-form:not(#empty-form-template .order-item-form)');
            orderItemForms.forEach((form, index) => {
                form.setAttribute('data-form-index', index);
                // Update Order Item heading (+1 as not zero indexing)
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
                // update relevant div containers that include this id
                form.querySelectorAll('div[id*="form-"]').forEach(div => {
                    // update container ids
                    div.id = div.id.replace(/form-\d+-/, `form-${index}-`);
                });
            });
        }
    };

    // Define function that updates the item value based on discount
    function updateOrderValue(target) {
        // if a user input is detected in the discount, quantity or base price field
        if (
            target.classList.contains('discount-field') ||
            target.classList.contains('quantity-field') ||
            target.classList.contains('base-price-field')
        ) {
            let formIndex = target.closest('.order-item-form').getAttribute('data-form-index');
            let basePriceField = document.getElementById(`id_form-${formIndex}-base_price`);
            let discountField = document.getElementById(`id_form-${formIndex}-discount`);
            let quantityField = document.getElementById(`id_form-${formIndex}-quantity`);
            let itemValueField = document.getElementById(`id_form-${formIndex}-item_value`);
            // Recalculate item value
            let discount = parseFloat(discountField.value) || 0;
            let basePrice = parseFloat(basePriceField.value) || 0;
            let quantity = parseInt(quantityField.value) || 0;
            itemValueField.value = ((basePrice - discount) * quantity).toFixed(2);
            // update the running total
            updateOrderTotals();
        }
    };

    // Define function that updates order total based on order item values
    function updateOrderTotals() {
        const orderFormOrderValueField = document.getElementById('order_value');
        let totalOrderValue = 0;

        // Select all elements with class .order-item-form but exclude those inside #empty-form-template
        document.querySelectorAll('.order-item-form:not(#empty-form-template .order-item-form)').forEach((_, index) => {

            let itemValueField = document.getElementById(`id_form-${index}-item_value`)
            let itemValue = parseFloat(itemValueField.value) || 0

            // Sum up item values for the order
            totalOrderValue += itemValue;
        });

        // Update the Order form with the calculated totals
        orderFormOrderValueField.value = totalOrderValue.toFixed(2);
    };

    // ************** SECTION B: EVENT LISTENERS & HANDLERS *****************************************************************

    // Populate product dropdowns for existing forms on page load
    document.querySelectorAll('.product-dropdown').forEach(selectElement => {
        populateProductDropdown(selectElement);
    });

    // Add Click event listener to handle adding new order item forms
    const addOrderItemButton = document.getElementById('add-order-item');
    addOrderItemButton.addEventListener('click', function () {

        // Create a new empty form
        addNewOrderItemForm();
    });

    // Add Click event listener to handle dynamic deletion of order items
    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('delete-order-item')) {
            if (confirm("Are you sure you want to delete the item?")) {
                deleteOrderItem(event.target);
                // update the running total
                updateOrderTotals();
            };
        };
    });

    // Add Change event listener for changes to the form
    document.addEventListener('change', function (event) {
        // If change is to product-dropdown, handle dynamic product selection and show relevant options/finishes fields
        if (event.target.classList.contains('product-dropdown')) {
            // Call updateProductDetails first, and then updateOrderValue         
            updateProductDetails(event.target)
                .then(() => {
                    // update the running totals
                    updateOrderValue(event.target);
                    updateOrderTotals();
                })
                .catch(error => {
                    console.error('Error in updating totals:', error);
                });
        };
    });

    // Add Input event listener to trigger update of item & order values 
    // when user is typing in those fields (for dynamic updates)
    document.addEventListener('input', function (event) {

        // execute the updateOrderValue function
        updateOrderValue(event.target)
    });


    // Handle the submission of the form depending on client details and user choice (if modal is triggered)
    document.getElementById('order-form').addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent default form submission

        const formData = new FormData(this); // Capture form data

        // Send a POST request to the API endpoint to check client details
        fetch('/api/check_client/', {
                method: 'POST',
                body: formData, // Send form data in request body
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken') // Include CSRF token for security
                }
            })
            .then(response => response.json())
            .then(data => {
                // if exact client match found, set input values and submit
                if (data.exact_match) {
                    document.getElementById('client-id-input').value = data.exact_match.id;
                    document.getElementById('client-action').value = 'use_existing';
                    this.submit();
                // if partial client match found show modal with partial match details
                } else if (data.partial_match) {
                    showModalWithClientDetails(data.partial_match);
                // if no match found
                } else {
                    // clear inputs then submit
                    document.getElementById('client-id-input').value = '';
                    document.getElementById('client-action').value = '';
                    this.submit();
                }
            });
    });

    // Define handler function for Client existing and asking for user input before submitting
    function showModalWithClientDetails(client) {

        // Fill in the modal with the partial match client details
        document.getElementById('modal-client-name').innerText = client.name;
        document.getElementById('modal-client-phone').innerText = client.phone;
        document.getElementById('modal-client-email').innerText = client.email;

        // Fill the modal with the new client details
        document.getElementById('modal-new-client-name').innerText = document.getElementById('client_name').value;
        document.getElementById('modal-new-client-phone').innerText = document.getElementById('client_phone').value;
        document.getElementById('modal-new-client-email').innerText = document.getElementById('client_email').value;

        // Handle "Use Existing Client"
        document.getElementById('use-existing-client-btn').addEventListener('click', function () {
            document.getElementById('client-id-input').value = client.id; // Set existing client ID
            document.getElementById('client-action').value = 'use_existing'; // Action to use existing client
            document.getElementById('order-form').submit(); // Now submit the form with the existing client
        });

        // Handle "Update Client Details"
        document.getElementById('update-client-details-btn').addEventListener('click', function () {
            document.getElementById('client-id-input').value = client.id; // Set existing client ID
            document.getElementById('client-action').value = 'update_client'; // Action to update client
            document.getElementById('order-form').submit(); // Submit the form as is (with updated client details)
        });

        // Show the modal
        let clientModal = new bootstrap.Modal(document.getElementById('clientConflictModal'));
        clientModal.show();

    }
});