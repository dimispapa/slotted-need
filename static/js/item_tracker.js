import {
    displayMessage,
    updateStatusStyle,
    updatePaidStatusStyle,
    ajaxSetupToken,
    debounce,
    initTooltips,
    generateSelectOptions,
    generateOptionsList,
    toggleSpinner,
    clearDataTableFilters

} from "./utils.js";

$(document).ready(function () {

    // Global constants definition
    const deleteModalElement = document.getElementById('DeleteOrderItemConfirmationModal');
    const deleteModal = new bootstrap.Modal(document.getElementById('DeleteOrderItemConfirmationModal'));
    const confirmDeleteBtn = document.getElementById("confirm-delete-order-item-btn");
    const csrftoken = document.querySelector("meta[name='csrf-token']").content;
    const pageSize = 25;
    const params = new URLSearchParams(window.location.search);

    // Setup AJAX to include CSRF token
    ajaxSetupToken(csrftoken);

    // Activate filter button if filter_type is 'critical'
    if (params.get('filter_type') === 'critical') {
        $('#critical-filter-btn').addClass('active btn-warning btn-pressed').removeClass('btn-outline-warning btn-unpressed');
    }

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
                d.page_size = length;

                // Filtering parameters based on filters.py
                d.id = $('#filter-id').val();
                d.order_id = $('#filter-order').val();
                d.date_from = $('#filter-date-from').val();
                d.date_to = $('#filter-date-to').val();
                d.client_name = $('#filter-client').val();
                d.product = $('#filter-product').val();
                d.design_options = $('#filter-design-options').val();
                d.product_finish = $('#filter-product-finish').val();
                d.item_component_finishes = $('#filter-component-finishes').val();
                d.value_min = $('#filter-value-min').val();
                d.value_max = $('#filter-value-max').val();
                d.priority_level = $('#filter-priority-level').val();
                d.item_status = $('#filter-item-status').val();
                d.paid_status = $('#filter-paid-status').val();
                d.exclude_completed = $('#filter-exclude-completed').is(':checked');

                // Check the critical filter button state
                if ($('#critical-filter-btn').hasClass('active')) {
                    d.filter_type = 'critical';
                } else {
                    // Otherwise remove critical filter param
                    d.filter_type = '';
                }

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
                data: 'order.created_on',
                name: 'order__created_on',
                className: 'sortable',
                render: function (data, type, row) {
                    if (type === 'display') {
                        let order_date = moment(data).format('DD/MM/YYYY');
                        return order_date;
                    }
                    return data;
                }
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
            { // Paid Status
                data: 'order.paid',
                name: 'order__paid',
                className: 'sortable',
                render: function (data, type, row) {
                    // for display purposes show the Font Awesome icon
                    if (type === 'display') {
                        // Use global variable passed from context into JS
                        let optionStr = paidStatusChoices[data];
                        return `
                        <button class="btn btn-sm fw-bolder text-wrap paid-status"
                        data-order-id="${row.order.id}" data-value="${data}">
                        ${optionStr}
                        </button>
                        `;
                    }
                    // for filtering and sorting, return the underlying data
                    return data;
                },
                type: 'num' // to convert to binary for sorting
            },
            // Completed
            {
                data: 'completed',
                className: 'sortable align-middle',
                render: function (data, type, row) {
                    if (type === 'display') {
                        return data === true ? '<p class="text-center mb-0"><i class="fa-solid fa-square-check text-success fs-2 fw-bolder" aria-label="Completed"></i></p>' : '';
                    }
                    return data;
                }
            },
            // Delete Button
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
            console.log('data table loaded');
        },
    });

    // Define function that deletes an order item and remaining items index
    function deleteOrderItem(orderItemId) {
        // show spinner
        let spinner = document.getElementById('delete-spinner');
        toggleSpinner(spinner);

        // API delete call
        $.ajax({
            url: `/api/order-items/${orderItemId}/`,
            method: 'DELETE',
            success: function (response) {
                // Reload the table to show changes
                table.ajax.reload(toggleSpinner(spinner), false);
                // display message
                if (response.success) {
                    displayMessage(response.message, 'success');
                }
            },
            // Error handling
            error: function (xhr, status, error) {
                // Reload the table to revert changes
                table.ajax.reload(toggleSpinner(spinner), false);
                // display message
                let errorMessage = `
                                    An error occurred while deleting order item ${orderItemId}:
                                    ${xhr.responseJSON.detail}
                                    ` || 'An error occurred while deleting the order item.';
                displayMessage(errorMessage, 'error');
            }
        });
    }

    // Function that opens the paid status modal and performs an AJAX call for order details
    function openPaidStatusModal(orderId) {

        // Show the modal
        $('#paidStatusModal').modal('show');

        // Clear previous data
        $('#paidStatusModal .modal-body').html('<p>Loading...</p>');

        // Fetch order details via AJAX
        $.ajax({
            url: `/api/orders/${orderId}/`,
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

    // Function that populates the paid status modal with order details
    function populatePaidStatusModal(data) {
        // set modal title label
        $('#paidStatusModalLabel').html(`Order #${data.id}`);
        // Construct HTML content for the modal
        let clientInfo = `
            <h5>Client Details</h5>
            <p>Name: ${data.client.client_name}</p>
            <p>Phone: ${data.client.client_phone}</p>
            <p>Email: ${data.client.client_email}</p>
        `;

        // Define the order items html elements
        let orderItems = '<h5>Order Items</h5><ul>';
        data.items.forEach(item => {
            // create an array of values from the option_value objects array
            let ovString = item.option_values.map((ov) => ov.value);
            // create an array of finish option names from the component finishes objects array
            let icfString = item.item_component_finishes.map((icf) => icf.component + ' - ' + icf.finish_option.name);
            // create an HTML element with the item details
            orderItems += `<li><strong>#${item.id} - ${item.product.name}</strong>
            <ul>
                <li>Design: <em>${ovString.join(", ")}</em></li>
                <li>Product Finish: <em>${item.product_finish || '-'}</em></li>
                <li>Component Finishes: <em>${icfString.join(", ")}</em></li>
            </ul>
            </li>`;
        });
        orderItems += '</ul>';

        // Generate `paid_status` options dynamically
        let paidStatusOptions = '';
        for (let [value, display] of Object.entries(paidStatusChoices)) {
            paidStatusOptions += `<option value="${value}" ${data.paid == value ? 'selected' : ''}>${display}</option>`;
        }

        let paidStatusForm = `
            <form id="paidStatusForm">
                <div class="form-group col-3 mb-2 mb-mb-3 fw-bold">
                    <label for="id_paid_status">Payment Status</label>
                    <select name="paid_status" id="id_paid_status" class="form-select paid-status fw-bold">
                        ${paidStatusOptions}
                    </select>
                </div>
                <input type="hidden" name="order_id" value="${data.id}">
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

    // Function that handles the submission of the paid status modal form
    function submitPaidStatusForm() {
        // get order id and new status
        let orderId = $('#paidStatusForm input[name="order_id"]').val();
        let newStatus = $('#paidStatusForm select[name="paid_status"]').val();

        // API AJAX patch call
        $.ajax({
            url: `/api/orders/${orderId}/`,
            method: 'PATCH',
            data: JSON.stringify({
                'paid': newStatus
            }),
            contentType: 'application/json',
            success: function (response) {

                // Reload the table to show changes, with callback function to hide modal but without resetting pagination
                table.ajax.reload(function () {
                        // Close the modal
                        $('#paidStatusModal').modal('hide');
                    },
                    false);
            },
            // Error handling
            error: function (xhr, status, error) {
                // display message
                let errorMessage = `
                                    Failed to update payment status for order item ${orderId}:
                                    ${xhr.responseJSON.detail}
                                    ` || 'Error updating payment status.';
                displayMessage(errorMessage, 'error');
            }
        });
    }

    // ************** SECTION B: EVENT LISTENERS & HANDLERS *****************************************************************
    // initialize tooltips
    initTooltips();

    // Prevent triggering sorting when a user clicks in any of the inputs.
    // Sorting should apply when the user clicks any of the column headers
    $('#orderitem-table').on('click mousedown touchstart', '.filter', function (e) {
        e.stopPropagation();
    });

    // Event listeners for filter inputs with debounce
    $('#filter-id, #filter-order, #filter-client, #filter-product, #filter-value-min, ' +
        '#filter-value-max, #filter-item-status, #filter-priority-level, #filter-paid-status, ' +
        '#filter-design-options, #filter-product-finish, #filter-component-finishes, ' +
        '#filter-exclude-completed, #filter-date-from, #filter-date-to'
    ).on('keyup change',
        debounce(function () {
            table.ajax.reload();
        }, 300));

    // Handle filter button click
    $('#critical-filter-btn').on('click', function () {
        $(this).toggleClass('active btn-warning btn-pressed btn-outline-warning btn-unpressed');
        // clear query parameter to effectively remove all filters in back-end
        if (!($(this).hasClass('active'))) {
            params.delete('filter_type');
        }

        // Refresh DataTable with the new filter state
        table.ajax.reload();
    });

    // Handle change for item_status
    $('#orderitem-table').on('change', '.item-status', function () {
        // get order item id and new status
        let orderItemId = $(this).data('id');
        let newStatus = $(this).val();
        // show spinner
        let spinner = document.getElementById(`item-status-spinner-${orderItemId}`);
        toggleSpinner(spinner);

        // API AJAX patch call to update item status in the backend
        $.ajax({
            url: `/api/order-items/${orderItemId}/`,
            type: 'PATCH',
            data: JSON.stringify({
                'item_status': newStatus
            }),
            contentType: 'application/json',
            success: function (response) {
                // hide the spinner
                toggleSpinner(spinner);
            },
            // Error handling
            error: function (xhr, status, error) {
                // Reload the table to revert changes
                table.ajax.reload(toggleSpinner(spinner), false);
                // display message
                let errorMessage = `
                                    Error updating item status for order item ${orderItemId}:
                                    ${xhr.responseJSON.detail}
                                    ` || 'An error occurred while deleting the order item.';
                displayMessage(errorMessage, 'error');
            }
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

        // API AJAX patch call to update priority status
        $.ajax({
            url: `/api/order-items/${orderitemId}/`,
            type: 'PATCH',
            data: JSON.stringify({
                'priority_level': newPriority
            }),
            contentType: 'application/json',
            success: function (response) {
                // hide spinner
                toggleSpinner(spinner);
            },
            // Error handling
            error: function (xhr, status, error) {
                // Reload the table to revert changes
                table.ajax.reload(toggleSpinner(spinner), false);
                // display message
                let errorMessage = `
                                    Error updating priority level for order item ${orderItemId}:
                                    ${xhr.responseJSON.detail}
                                    ` || 'An error occurred while deleting the order item.';
                displayMessage(errorMessage, 'error');
            }
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
        let deleteBtn = event.target.closest('.delete-order-item-btn');
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

    // Event delegation for dynamically added buttons
    $('#orderitem-table tbody').on('click', '.paid-status', function () {
        let orderId = $(this).data('order-id');
        openPaidStatusModal(orderId);
    });

    // Add event listener for clicks on clear filter btn
    $('#clear-filters-btn').on('click', function () {
        // clear query parameter to effectively remove all filters in back-end
        params.delete('filter_type');
        // clear filters on front-end and reload table
        clearDataTableFilters(table);
    });

});