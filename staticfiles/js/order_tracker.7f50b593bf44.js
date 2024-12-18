import {
    displayMessage,
    updateStatusStyle,
    updateItemStatusStyle,
    ajaxSetupToken,
    debounce,
    initTooltips,
    generateSelectOptions,
    toggleChildRow,
    toggleSpinner,
    clearDataTableFilters

} from './utils.js'

$(document).ready(function () {

    // Constant definitions
    const deleteModalElement = document.getElementById('DeleteOrderConfirmationModal');
    const deleteModal = new bootstrap.Modal(document.getElementById('DeleteOrderConfirmationModal'));
    const confirmDeleteBtn = document.getElementById("confirm-delete-order-btn");
    const archiveModalElement = document.getElementById('ArchiveOrderConfirmationModal');
    const archiveModal = new bootstrap.Modal(document.getElementById('ArchiveOrderConfirmationModal'));
    const confirmArchiveBtn = document.getElementById("confirm-archive-order-btn");
    const csrftoken = document.querySelector("meta[name='csrf-token']").content;
    const pageSize = 25;

    // Setup AJAX to include CSRF token
    ajaxSetupToken(csrftoken);

    // ************** SECTION A: FUNCTION DEFINITIONS ********************************************************************

    // Initialize DataTable with AJAX source and server-side processing
    let table = $('#orders-table').DataTable({
        serverSide: true, // Enable server-side processing
        processing: true, // Enables processing animation
        orderCellsTop: true, // Place sorting icons to top row
        fixedHeader: true, // Fix the header when scrolling
        searching: false, // Disable global search as using column filters
        scrollY: '60vh', // Enable vertical scrolling
        scrollX: true, // Enable horizontal scrolling
        responsive: true, // Enable responsive layout for smaller screens
        pageLength: pageSize,
        // callback function after creation but before drawing
        createdRow: (row, data, dataIndex) => {
            // add row id attribute as orderId
            $(row).attr('id', `order-${data.id}`);
        },
        ajax: {
            url: '/api/orders/',
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
                d.date_from = $('#filter-date-from').val();
                d.date_to = $('#filter-date-to').val();
                d.client_name = $('#filter-client').val();
                d.discount_min = $('#filter-discount-min').val();
                d.discount_max = $('#filter-discount-max').val();
                d.deposit_min = $('#filter-deposit-min').val();
                d.deposit_max = $('#filter-deposit-max').val();
                d.value_min = $('#filter-value-min').val();
                d.value_max = $('#filter-value-max').val();
                d.order_status = $('#filter-order-status').val();
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
            }
        },
        columns: [{
                data: null,
                orderable: false,
                className: 'not-sortable details-control',
                searchable: false,
                render: function (data, type, row) {
                    if (type === 'display') {
                        return `
                    <button type="button" class="btn btn-sm btn-info toggle-items-btn" data-bs-toggle="collapse"
                      data-bs-target="#order-items-${row.id}" aria-expanded="false"
                      aria-controls="order-items-${row.id}">
                      <i class="fa-solid fa-chevron-down"></i>
                    </button>
                    `;
                    }
                    return data;
                }
            },
            {
                data: 'id',
                className: 'sortable'
            },
            {
                data: 'created_on',
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
                data: 'client.client_name',
                name: 'client__client_name',
                className: 'sortable'
            },
            {
                data: 'discount',
                render: $.fn.dataTable.render.number(',', '.', 0, '€')
            },
            {
                data: 'deposit',
                render: $.fn.dataTable.render.number(',', '.', 0, '€')
            },
            {
                data: 'order_value',
                render: $.fn.dataTable.render.number(',', '.', 0, '€')
            },
            {
                data: 'order_status',
                render: function (data, type, row) {
                    if (type === 'display') {
                        // render the order status HTML
                        let orderStatusDiv = '<div>';
                        orderStatusDiv += renderOrderStatus(row.id, data, row.paid);
                        return orderStatusDiv += '</div>';
                    }
                    return data;
                }
            },
            {
                data: 'paid',
                render: function (data, type, row) {
                    if (type === 'display') {
                        let select = `<select class="form-select-sm paid-status fw-bolder text-wrap" data-id="${row.id}">`;
                        // Use global variable passed from context into JS and generate select options
                        let options = generateSelectOptions(paidStatusChoices, data);
                        select += options;
                        select += '</select>';
                        select += `
                            <span class="text-center inline-spinner-div">
                                <div class="spinner-border text-primary d-none" role="status" id="paid-status-spinner-${row.id}">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                            </span>`
                        return select;
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

                    let deleteBtn = `
                    <div class="btn-group" role="group" aria-label="Button group with nested dropdown">
                        <button type="button" id="delete-order-btn-${row.id}" name="delete_order"
                        class="btn btn-sm btn-danger delete-order-btn" value="${row.id}" aria-label="Delete order">
                        <i class="fa-solid fa-trash"></i>
                        </button>
                    `;
                    let archiveBtn = `
                    <button class="btn btn-sm btn-secondary archive-order-btn ms-1 ms-md-2"
                    id="archive-order-btn-${row.id}" value="${row.id}" aria-label="Archive order">
                    <i class="fa-regular fa-folder-open"></i>
                    </button>`;

                    return deleteBtn + archiveBtn + '</div>';
                }
            },
        ],
        // Default ordering by order id descending
        order: [
            [1, 'desc']
        ],
        // Callback after every draw (initial load and subsequent updates)
        drawCallback: function (settings) {
            // update status styles
            updateStatusStyle();
            // get the rows from the API
            let rows = this.api().rows()
            // Iterate through the rows
            rows.every(function (rowIdx, tableLoop, rowLoop) {
                // get the row data
                let data = this.data();
                // Find the DataTable row
                let row = $(`#order-${data.id}`);
                // update row styles
                updateRowStyle(row, data);
                // initialize tooltips
                initTooltips();
                // add event listeners
                processEventListeners();
                console.log('data table loaded');
            })

        },
    });

    // Function that renders the order status
    function renderOrderStatus(orderId, orderStatus) {

        // Use global variable passed from context into JS to map the badge value into string
        let badge = `
        <span class="badge position-relative align-middle item-status" id="order-status-badge-${orderId}"
        data-id="${orderId}" data-value="${orderStatus}">${orderStatusChoices[orderStatus]}
        `;
        // create exclamation badge to show when order is delivered but unpaid
        let exclamation = `
        <span id="exclamation-${orderId}" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
            <i class="fa-solid fa-exclamation fs-6"></i>
            <span class="visually-hidden">Alert: delivered but unpaid </span>
        </span>               
        `;

        return badge + exclamation + '</span>';

    };

    // Function that styles the row based on status
    function updateRowStyle(row, data) {

        // Delivered and Not Paid
        if (data.order_status == 4 && data.paid == 1) {
            $(row).removeClass('table-light opacity-50 shadow-none');
            $(row).addClass('table-danger');
            $(`#exclamation-${data.id}`).removeClass('d-none');
            $(`#archive-order-btn-${data.id}`).addClass('d-none');
            // Delivered and Fully Paid
        } else if (data.order_status == 4 && data.paid == 2) {
            $(row).removeClass('table-danger');
            $(row).addClass('table-light opacity-50 shadow-none');
            $(`#exclamation-${data.id}`).addClass('d-none');
            $(`#archive-order-btn-${data.id}`).removeClass('d-none');
            // All other cases
        } else {
            $(row).removeClass('table-light opacity-50 shadow-none');
            $(row).removeClass('table-danger');
            $(`#exclamation-${data.id}`).addClass('d-none');
            $(`#archive-order-btn-${data.id}`).addClass('d-none');
        }
    };

    // Function that deletes an order
    function deleteOrder(orderId) {
        // show spinner
        let spinner = document.getElementById('action-spinner');
        toggleSpinner(spinner);

        // API delete call
        $.ajax({
            url: `/api/orders/${orderId}/`,
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
                                    An error occurred while deleting order ${orderId}:
                                    ${xhr.responseJSON.detail}
                                    ` || 'An error occurred while deleting the order item.';
                displayMessage(errorMessage, 'error');
            }
        });
    };

    // Function that archives an order
    function archiveOrder(orderId) {
        // show spinner
        let spinner = document.getElementById('action-spinner');
        toggleSpinner(spinner);

        // API archive call for action
        $.ajax({
            url: `/api/orders/${orderId}/archive/`,
            method: 'POST',
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
                                    An error occurred while archiving order ${orderId}:
                                    ${xhr.responseJSON.detail}
                                    ` || 'An error occurred while archiving the order.';
                displayMessage(errorMessage, 'error');
            }
        });
    };

    // ************** SECTION B: EVENT LISTENERS & HANDLERS *****************************************************************

    function processEventListeners() {

        // Prevent triggering sorting when a user clicks in any of the inputs.
        // Sorting should apply when the user clicks any of the column headers
        $('#orderitem-table').on('click mousedown touchstart', '.filter', function (e) {
            e.stopPropagation();
        });

        // Event listeners for filter inputs with debounce
        $('#filter-id, #filter-client, #filter-discount-min, #filter-discount-max, ' +
            '#filter-deposit-min, #filter-deposit-max, #filter-value-min, #filter-value-max, ' +
            '#filter-order-status, #filter-paid-status, #filter-date-from, #filter-date-to').on('keyup change', debounce(function () {
            // apply filters
            table.ajax.reload();
        }, 300));

        // Handle change for paid_status and update the backend with AJAX call
        $('#orders-table').on('change', '.paid-status', function () {
            // get order id and new status
            let orderId = $(this).data('id');
            let newStatus = $(this).val();

            // show spinner
            let spinner = document.getElementById(`paid-status-spinner-${orderId}`);
            toggleSpinner(spinner);

            // API AJAX patch call
            $.ajax({
                url: `/api/orders/${orderId}/`,
                type: 'PATCH',
                data: JSON.stringify({
                    'paid': newStatus
                }),
                contentType: 'application/json',
                success: function (response) {
                    // hide the spinner on completion
                    toggleSpinner(spinner);
                    // Get order details
                    let orderData = response;
                    // Find the DataTable row
                    let row = $(`#order-${orderId}`)
                    // Refresh the row styles
                    updateRowStyle(row, orderData);
                },
                error: function (xhr, status, error) {
                    console.error('Error updating paid status:', error);
                    // Reload the table to revert changes
                    table.ajax.reload(toggleSpinner(spinner), false);
                },
            });
        });

        // Handle change for item_status and update the backend with AJAX call
        $('#orders-table').on('change', '.item-status', function () {
            // get order item id and new status
            let orderitemId = $(this).data('id');
            let newStatus = $(this).val();

            // show spinner
            let spinner = document.getElementById(`item-status-spinner-${orderitemId}`);
            toggleSpinner(spinner);

            // API AJAX patch call
            $.ajax({
                url: `/api/order-items/${orderitemId}/`,
                type: 'PATCH',
                data: JSON.stringify({
                    'item_status': newStatus
                }),
                contentType: 'application/json',
                success: function (response) {
                    // Get order details
                    let orderData = response.order;
                    // Find the DataTable row
                    let row = $(`#order-${orderData.id}`)
                    // get the new order status badge html
                    let orderStatusBadgeHTML = renderOrderStatus(orderData.id, orderData.order_status, orderData.paid);
                    // Update the badge
                    let orderStatusBadge = $(`#order-status-badge-${orderData.id}`);
                    let orderStatusDiv = document.createElement('div');
                    orderStatusDiv.innerHTML = orderStatusBadgeHTML;
                    orderStatusBadge.replaceWith(orderStatusDiv);
                    // get the new badge element
                    let newOrderStatusBadge = $(`#order-status-badge-${orderData.id}`);
                    // Refresh badge status styles
                    updateItemStatusStyle(newOrderStatusBadge[0]);
                    // Refresh the row styles
                    updateRowStyle(row, orderData);

                    // hide the spinner on completion
                    toggleSpinner(spinner);
                },
                error: function (xhr, status, error) {
                    console.error('Error updating paid status:', error);
                    // Reload the table to revert changes
                    table.ajax.reload(toggleSpinner(spinner), false);
                },
            });
        });

        // Handle change for item_status and update the backend with AJAX call
        $('#orders-table').on('change', '.priority-status', function () {
            // get order item id and new status
            let orderitemId = $(this).data('id');
            let newStatus = $(this).val();

            // show spinner
            let spinner = document.getElementById(`priority-status-spinner-${orderitemId}`);
            toggleSpinner(spinner);

            // API AJAX patch call
            $.ajax({
                url: `/api/order-items/${orderitemId}/`,
                type: 'PATCH',
                data: JSON.stringify({
                    'priority_level': newStatus
                }),
                contentType: 'application/json',
                success: function (response) {
                    // hide the spinner on completion
                    toggleSpinner(spinner);
                },
                error: function (xhr, status, error) {
                    console.error('Error updating paid status:', error);
                    // Reload the table to revert changes
                    table.ajax.reload(toggleSpinner(spinner), false);
                },
            });
        });

        // Handle change for paid_status and update the backend with AJAX call
        $('#orders-table').on('change', '.paid-status', function () {
            // get order id and new status
            let orderId = $(this).data('id');
            let newStatus = $(this).val();

            // show spinner
            let spinner = document.getElementById(`paid-status-spinner-${orderId}`);
            toggleSpinner(spinner);

            // API AJAX patch call
            $.ajax({
                url: `/api/orders/${orderId}/`,
                type: 'PATCH',
                data: JSON.stringify({
                    'paid': newStatus
                }),
                contentType: 'application/json',
                success: function (response) {
                    // hide the spinner on completion
                    toggleSpinner(spinner);
                    // Get order details
                    let orderData = response;
                    // Find the DataTable row
                    let row = $(`#order-${orderId}`)
                    // Refresh the row styles
                    updateRowStyle(row, orderData);
                },
                error: function (xhr, status, error) {
                    console.error('Error updating paid status:', error);
                    // Reload the table to revert changes
                    table.ajax.reload(toggleSpinner(spinner), false);
                },
            });
        });

        // Add event listener for clicks on clear filter btn
        $('#clear-filters-btn').on('click', function () {
            // clear filters on front-end and reload table
            clearDataTableFilters(table);
        });

        // add event listener that handles first delete button that will trigger the modal
        document.addEventListener("click", (event) => {
            // get delete button as reference point. Allow clicking on icon inside
            let deleteBtn = event.target.closest('.delete-order-btn');
            if (deleteBtn) {
                // get orderId from the button value
                let orderId = deleteBtn.value;
                // Set orderId as attribute for the modal to be used for front-end deletion
                deleteModalElement.setAttribute('data-order-id', orderId);
                // show the confirmation delete modal
                deleteModal.show();
            }
        });

        // add event listener on confirm delete button that will handle the deletion
        confirmDeleteBtn.addEventListener('click', () => {
            // Get order ID from modal attribute
            let orderId = deleteModalElement.getAttribute('data-order-id');
            if (orderId) {
                // Delete item
                deleteOrder(orderId);
                // Clear the data attribute
                deleteModalElement.removeAttribute('data-order-id');
            }
        });

        // add event listener that handles first archive button that will trigger the modal
        document.addEventListener("click", (event) => {
            // get delete button as reference point. Allow clicking on icon inside
            let archiveBtn = event.target.closest('.archive-order-btn');
            if (archiveBtn) {
                // get orderId from the button value
                let orderId = archiveBtn.value;
                // Set orderId as attribute for the modal to be used for front-end deletion
                archiveModalElement.setAttribute('data-order-id', orderId);
                // show the confirmation delete modal
                archiveModal.show();
            }
        });

        // add event listener on confirm delete button that will handle the deletion
        confirmArchiveBtn.addEventListener('click', () => {
            // Get order ID from modal attribute
            let orderId = archiveModalElement.getAttribute('data-order-id');
            if (orderId) {
                // Delete item
                archiveOrder(orderId);
                // Clear the data attribute
                archiveModalElement.removeAttribute('data-order-id');
            }
        });

        // add event listener to show/hide the row child with item details
        $('#orders-table tbody').on('click', 'td.details-control', function () {
            let tr = $(this).closest('tr');
            let row = table.row(tr);

            toggleChildRow(tr, row, false);
        });
    }


});