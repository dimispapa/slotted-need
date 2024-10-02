import {
    displayMessages,
    displayMessage,
    updateStatusStyle,
    updatePaidStatusStyle,
    ajaxSetupToken,
    debounce,
    initTooltips,
    generateSelectOptions,
    generateOptionsList,
    toggleSpinner

} from "./utils.js";

$(document).ready(function () {

    // Global constants definition
    const deleteModalElement = document.getElementById('DeleteOrderItemConfirmationModal');
    const deleteModal = new bootstrap.Modal(document.getElementById('DeleteOrderItemConfirmationModal'));
    const confirmDeleteBtn = document.getElementById("confirm-delete-order-item-btn");
    const csrftoken = document.querySelector("meta[name='csrf-token']").content;
    const pageSize = 25;

    // Setup AJAX to include CSRF token
    ajaxSetupToken(csrftoken);

    // Initialize DataTable with AJAX source and server-side processing
    let table = $('#orderitem-table').DataTable({
        serverSide: true, // Enable server-side processing
        processing: true, // Enables processing animation
        orderCellsTop: true, // Place sorting icons to top row
        fixedHeader: true, // Fix the header when scrolling
        searching: false, // Disable global search as using column filters
        scrollY: '60vh', // Enable vertical scrolling
        scrollX: true, // Enable horizontal scrolling
        responsive: true, // Enable responsive layout for smaller screens
        pageLength: pageSize,
        ajax: {
            url: '/api/order-items/',
            type: 'GET',
            data: function (d) {
                // Map DataTables parameters to API query parameters

                // Calculate page number and page size
                let start = parseInt(d.start) || 0;
                let length = parseInt(d.length) || pageSize;
                let page = Math.floor(start / length) + 1;

                // Assign page and page size
                d.page = page;
                d.length = length;

                // Filtering parameters based on filters.py
                d.id = $('#filter-id').val();
                d.order_id = $('#filter-order').val();
                d.client_name = $('#filter-client').val();
                d.product = $('#filter-product').val();
                d.design_options = $('#filter-design-options').val();
                d.product_finish = $('#filter-product-finish').val();
                d.item_component_finishes = $('#filter-component-finishes').val();
                d.value_min = $('#filter-value-min').val();
                d.value_max = $('#filter-value-max').val();
                d.item_status = $('#filter-item-status').val();
                d.priority_level = $('#filter-priority-level').val();
                d.paid_status = $('#filter-paid-status').val();

                // Ordering parameters
                // WARNING: "order" is a reserved array name to store sorting instructions
                // Avoid using the "order" attribute to store other data that can cause conflicts.
                if (d.order && d.order.length > 0) {
                    let orderColumnIndex = d.order[0].column;
                    let orderDir = d.order[0].dir;
                    let orderColumn = d.columns[orderColumnIndex];
                    d.ordering = (orderDir === 'desc' ? '-' : '') + (orderColumn.name ? orderColumn.name : orderColumn.data);
                }

                return d;
            },
            dataSrc: function (json) {
                // Map API response to DataTables expected format
                json.recordsTotal = json.count;
                json.recordsFiltered = json.count;
                return json.results;
            },
        },
        columns: [{
                data: 'id',
                className: 'sortable'
            },
            {
                data: 'order.id',
                name: 'order__id',
                className: 'sortable'
            },
            {
                data: 'order.client.client_name',
                name: 'order__client__client_name',
                className: 'sortable'
            },
            {
                data: 'product.name',
                name: 'product__name',
                className: 'sortable'
            },
            {
                data: 'option_values',
                orderable: false, // Disable ordering,
                className: 'not-sortable p2',
                render: function (data, type, row) {
                    if (type === 'display') {
                        let list = generateOptionsList('option_values', data);
                        return list;
                    }
                    return data;
                }
            },
            {
                data: 'product_finish',
                name: 'product_finish__name',
                className: 'sortable',
                render: function (data, type, row) {
                    if (type === 'display') {
                        return data ? data.name : '-';
                    }
                    return data;
                }
            },
            {
                data: 'item_component_finishes',
                orderable: false, // Disable ordering
                className: 'not-sortable p2',
                render: function (data, type, row) {
                    if (type === 'display') {
                        let list = generateOptionsList('component_finishes', data);
                        return list;
                    }
                    return data;
                }
            },
            {
                data: 'item_value',
                className: 'sortable',
                render: $.fn.dataTable.render.number(',', '.', 0, '€')
            },
            { // Item Status
                data: 'item_status',
                className: 'sortable',
                render: function (data, type, row) {
                    if (type === 'display') {
                        let select = `<select class="form-select-sm item-status fw-bolder text-wrap" data-id="${row.id}">`;
                        // Use global variable passed from context into JS and generate select options
                        let options = generateSelectOptions(itemStatusChoices, data);
                        select += options;
                        select += '</select>';
                        // Add a spinner
                        select += `
                        <span class="text-center inline-spinner-div">
                            <div class="spinner-border text-primary d-none" role="status" id="item-status-spinner-${row.id}">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </span>
                        `;
                        return select;
                    }
                    return data;
                }
            },
            { // Priority Level Status
                data: 'priority_level',
                className: 'sortable',
                render: function (data, type, row) {
                    if (type === 'display') {
                        let select = '<select class="form-select-sm priority-status fw-bolder text-wrap" data-id="' + row.id + '">';
                        // Use global variable passed from context into JS and generate select options
                        let options = generateSelectOptions(priorityLevelChoices, data);
                        select += options;
                        select += '</select>';
                        // Add a spinner
                        select += `
                        <span class="text-center inline-spinner-div">
                            <div class="spinner-border text-primary d-none" role="status" id="priority-status-spinner-${row.id}">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </span>
                        `;
                        return select;
                    }
                    return data;
                }
            },
            { // Paid Status
                data: 'order.paid',
                name: 'order__paid',
                className: 'sortable',
                render: function (data, type, row) {
                    if (type === 'display') {
                        // Use global variable passed from context into JS
                        let optionStr = paidStatusChoices[data];
                        return `
                        <button class="btn btn-sm fw-bolder text-wrap paid-status"
                        data-order-id="${row.order.id}" data-value="${data}">
                        ${optionStr}
                        </button>
                        `
                    }
                    return data;
                }
            },
            {
                data: null,
                orderable: false,
                className: 'not-sortable',
                searchable: false,
                render: function (data, type, row) {
                    return `
                    <button type="button" id="delete-order-item-btn-${row.id}" name="delete_order"
                    class="btn btn-sm btn-danger delete-order-item-btn" value="${row.id}">
                    <i class="fa-solid fa-trash"></i>
                    </button>
                    `;
                }
            },
        ],
        // Default ordering by priority_level descending
        order: [
            [9, 'desc']
        ],
        // Callback after every draw (initial load and subsequent updates)
        drawCallback: function (settings) {
            // update status styles
            updateStatusStyle();
        },
    });

    // Prevent triggering sorting when a user clicks in any of the inputs.
    // Sorting should apply when the user clicks any of the column headers
    $('#orderitem-table').on('click mousedown touchstart', 'input, select, button', function (e) {
        e.stopPropagation();
    });

    // Event listeners for filter inputs with debounce
    $('#filter-id, #filter-order, #filter-client, #filter-product, #filter-value-min, ' +
        '#filter-value-max, #filter-item-status, #filter-priority-level, #filter-paid-status, ' +
        '#filter-design-options, #filter-product-finish, #filter-component-finishes').on('keyup change', debounce(function () {
        table.ajax.reload();
    }, 300));

    // Handle change for item_status
    $('#orderitem-table').on('change', '.item-status', function () {
        // get order item id and new status
        let orderitemId = $(this).data('id');
        let newStatus = $(this).val();
        // show spinner
        let spinner = document.getElementById(`item-status-spinner-${orderitemId}`);
        toggleSpinner(spinner);

        // API AJAX patch call to update backend data
        $.ajax({
            url: `/api/order-items/${orderitemId}/`,
            type: 'PATCH',
            data: JSON.stringify({
                'item_status': newStatus
            }),
            contentType: 'application/json',
            success: function (response) {
                // Reload the table without resetting pagination
                table.ajax.reload(toggleSpinner(spinner), false);
            },
            error: function (xhr, status, error) {
                console.error('Error updating item status:', error);
                // Reload the table to revert changes
                table.ajax.reload(toggleSpinner(spinner), false);
            },
        });
    });

    // Handle change for priority_level to update backend data
    $('#orderitem-table').on('change', '.priority-status', function () {
        // Get order item id and new priority status
        var orderitemId = $(this).data('id');
        var newPriority = $(this).val();
        // show spinner
        let spinner = document.getElementById(`priority-status-spinner-${orderitemId}`);
        toggleSpinner(spinner);

        // API AJAX patch call
        $.ajax({
            url: `/api/order-items/${orderitemId}/`,
            type: 'PATCH',
            data: JSON.stringify({
                'priority_level': newPriority
            }),
            contentType: 'application/json',
            success: function (response) {
                // Reload the table without resetting pagination
                table.ajax.reload(toggleSpinner(spinner), false);
            },
            error: function (xhr, status, error) {
                console.error('Error updating priority level:', error);
                // Reload the table to revert changes
                table.ajax.reload(toggleSpinner(spinner), false);
            },

        });
    });


    // Event delegation for delete buttons within the DataTable
    $('#orderitem-table tbody').on('click', '.delete-order-item-btn, .delete-order-item-btn *', (event) => {
        // Use .closest() to find the button in case the icon is clicked
        let deleteBtn = $(event.target).closest('.delete-order-item-btn');
        if (deleteBtn.length) {
            // stop propagation to prevent event bubbling up the parents
            event.preventDefault();
            event.stopPropagation();
            // Get order item ID from the button value
            let orderItemId = deleteBtn.val();
            // Set the order item ID as an attribute on the modal
            deleteModalElement.setAttribute('data-order-item-id', orderItemId);
            // Show the confirmation modal
            deleteModal.show();
        }
    });

    // add event listener that handles first delete button that will trigger the modal
    document.addEventListener("click", (event) => {
        // get delete button as reference point. Allow clicking on icon inside
        let deleteBtn = event.target.closest('.delete-order-item-btn')
        if (deleteBtn) {
            // get orderId from the button value
            let orderItemId = deleteBtn.value;
            // Set orderId as attribute for the modal to be used for front-end deletion
            deleteModalElement.setAttribute('data-order-item-id', orderItemId);
            // show the confirmation delete modal
            deleteModal.show();
        }
    });

    // add event listener on confirm delete button that will handle the deletion
    confirmDeleteBtn.addEventListener('click', () => {
        // Get order ID from modal attribute
        let orderItemId = deleteModalElement.getAttribute('data-order-item-id');
        if (orderItemId) {
            // Delete item
            deleteOrderItem(orderItemId);
            // Clear the data attribute
            deleteModalElement.removeAttribute('data-order-item-id');
        }
    });

    // initialize tooltips
    initTooltips();

    // Define function that deletes an order item and remaining items index
    function deleteOrderItem(orderItemId) {
        // show spinner
        let spinner = document.getElementById('delete-spinner');
        toggleSpinner(spinner);

        // API delete call
        $.ajax({
            url: `/api/order-items/${orderItemId}/`,
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken,
                // To identify AJAX request in the backend
                'X-Requested-With': 'XMLHttpRequest',
            },
            success: function (response) {
                // Reload the table to show changes
                table.ajax.reload(toggleSpinner(spinner), false);
                // display message
                if (response.success) {
                    displayMessage(response.message, 'success');
                }
            },
            error: function (xhr, status, error) {
                // Reload the table to revert changes
                table.ajax.reload(toggleSpinner(spinner), false);
                // display message
                let errorMessage = error || 'An error occurred while deleting the order item.';
                displayMessage(errorMessage, 'error');
            }
        });
    };

    // function deleteOrderItem(orderId) {
    //     // show spinner
    //     let spinner = document.getElementById('delete-spinner');
    //     toggleSpinner(spinner);
    //     // call delete_order API to handle deletion in the backend
    //     fetch(`/api/delete-order/${orderId}/`, {
    //             method: 'POST',
    //             headers: {
    //                 'X-CSRFToken': csrftoken,
    //                 // To identify AJAX request in the backend
    //                 'X-Requested-With': 'XMLHttpRequest',
    //             }
    //         })
    //         .then(response => {
    //             // handle bad reponse status
    //             if (!response.ok) {
    //                 if (response.status === 403) {
    //                     throw new Error('You do not have permission to delete this order.');
    //                 } else if (response.status === 404) {
    //                     throw new Error('Order was not found.');
    //                 } else {
    //                     throw new Error('Network response was not ok.');
    //                 }
    //             }
    //             return response.json();
    //         })
    //         .then(data => {
    //             if (data.success) {
    //                 // get order row element to target for deletion
    //                 const orderRow = document.getElementById(`order-${orderId}`);
    //                 // delete row from table to handle deletion in the front-end
    //                 // (will eliminate the need to redirect page)
    //                 if (orderRow) {
    //                     orderRow.remove();
    //                 }
    //                 // Display success messages
    //                 if (data.messages && data.messages.length > 0) {
    //                     displayMessages(data.messages);
    //                 }
    //             } else {
    //                 // Display error messages
    //                 if (data.messages && data.messages.length > 0) {
    //                     displayMessages(data.messages);
    //                 }
    //             }
    //             // hide spinner
    //             toggleSpinner(spinner);
    //         })
    //         // handle other errors
    //         .catch((error) => {
    //             console.error(`There was a problem with deleting order ${orderId}:`, error);
    //             displayMessages([{
    //                 level: 40,
    //                 level_tag: 'error',
    //                 message: `An error occurred: ${error.message}`
    //             }]);
    //         });
    // };

    // Function that opens the paid status modal and performs an AJAX call for order details
    function openPaidStatusModal(orderId) {

        // Show the modal
        $('#paidStatusModal').modal('show');

        // Clear previous data
        $('#paidStatusModal .modal-body').html('<p>Loading...</p>');

        // Fetch order details via AJAX
        $.ajax({
            url: `/api/${orderId}/details/`,
            method: 'GET',
            success: function (data) {
                // Populate the modal with order and client details
                populatePaidStatusModal(data);
            },
            error: function (error) {
                console.error('Error fetching order details:', error);
                $('#paidStatusModal .modal-body').html('<p>Error loading data.</p>');
            }
        });
    }

    // Event delegation for dynamically added buttons
    $('#orderitem-table tbody').on('click', '.paid-status', function () {
        let orderId = $(this).data('order-id');
        openPaidStatusModal(orderId);
    });

    // Function that populates the paid status modal with order details
    function populatePaidStatusModal(data) {
        // Construct HTML content for the modal
        let clientInfo = `
            <h5>Client Details</h5>
            <p>Name: ${data.client.name}</p>
            <p>Phone: ${data.client.phone}</p>
            <p>Email: ${data.client.email}</p>
        `;

        let orderItems = '<h5>Order Items</h5><ul>';
        data.order_items.forEach(item => {
            orderItems += `<li><strong>${item.str}</strong>
            <ul>
                <li><em>Design:</em> ${item.option_values}</li>
                <li><em>Product Finish:</em> ${item.product_finish || 'None'}</li>
                <li><em>Component Finishes:</em> ${item.item_component_finishes}</li>
            </ul>
            </li>`;
        });
        orderItems += '</ul>';

        // Generate `paid_status` options dynamically
        let paidStatusOptions = '';
        for (let [value, display] of Object.entries(paidStatusChoices)) {
            paidStatusOptions += `<option value="${value}" ${data.paid_status == value ? 'selected' : ''}>${display}</option>`;
        }

        let paidStatusForm = `
            <form id="paidStatusForm">
                <div class="form-group col-3 mb-2 mb-mb-3 fw-bold">
                    <label for="id_paid_status">Payment Status</label>
                    <select name="paid_status" id="id_paid_status" class="form-select paid-status fw-bold">
                        ${paidStatusOptions}
                    </select>
                </div>
                <input type="hidden" name="order_id" value="${data.order_id}">
                <button type="submit" class="btn btn-primary fw-bold">Update Payment Status</button>
            </form>
        `;

        $('#paidStatusModal .modal-body').html(clientInfo + orderItems + paidStatusForm);

        // Apply paid status style + listener
        let paidStatus = document.getElementById('id_paid_status');
        updatePaidStatusStyle(paidStatus);
        paidStatus.addEventListener('change', (event) => updatePaidStatusStyle(event.target));

        // Attach form submission handler
        $('#paidStatusForm').on('submit', function (e) {
            e.preventDefault();
            submitPaidStatusForm();
        });
    }

    function submitPaidStatusForm() {
        let formData = {
            'order_id': $('#paidStatusForm input[name="order_id"]').val(),
            'paid_status': $('#paidStatusForm select[name="paid_status"]').val()
        };

        $.ajax({
            url: `/api/update-paid-status/`,
            method: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': csrftoken,
                // To identify AJAX request in the backend
                'X-Requested-With': 'XMLHttpRequest',
            },
            success: function (response) {
                // Close the modal
                $('#paidStatusModal').modal('hide');

                // Reload the DataTable to reflect changes
                $('#orderitem-table').DataTable().ajax.reload(null, false);
            },
            error: function (error) {
                console.error('Error updating payment status:', error);
                displayMessages([{
                    level: 40,
                    level_tag: 'error',
                    message: `Failed to update payment status: ${error.message}`
                }]);
            }
        });
    }

})