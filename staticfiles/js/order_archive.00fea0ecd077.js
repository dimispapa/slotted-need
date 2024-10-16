import {
    displayMessage,
    updateStatusStyle,
    ajaxSetupToken,
    debounce,
    initTooltips,
    toggleChildRow,
    toggleSpinner,
    clearDataTableFilters

} from './utils.js'

$(document).ready(function () {

    // Constant definitions
    const deleteModalElement = document.getElementById('DeleteOrderConfirmationModal');
    const deleteModal = new bootstrap.Modal(document.getElementById('DeleteOrderConfirmationModal'));
    const confirmDeleteBtn = document.getElementById("confirm-delete-order-btn");
    const unArchiveModalElement = document.getElementById('UnArchiveOrderConfirmationModal');
    const unArchiveModal = new bootstrap.Modal(document.getElementById('UnArchiveOrderConfirmationModal'));
    const confirmUnArchiveBtn = document.getElementById("confirm-un-archive-order-btn");
    const csrftoken = document.querySelector("meta[name='csrf-token']").content;
    const pageSize = 25;

    // Setup AJAX to include CSRF token
    ajaxSetupToken(csrftoken);

    // ************** SECTION A: FUNCTION DEFINITIONS ********************************************************************

    // Initialize DataTable with AJAX source and server-side processing
    let table = $('#order-archive-table').DataTable({
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
                // Filter queryset for archived orders using query parameter 
                d.archived = true;

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
                        // Use global variable passed from context into JS to map the badge value into string
                        return `
                        <span class="badge align-middle item-status" id="order-status-badge-${row.id}"
                        data-id="${row.id}" data-value="${data}">${orderStatusChoices[data]}
                        </span>`;
                    }
                    return data;
                }
            },
            {
                data: 'paid',
                render: function (data, type, row) {
                    if (type === 'display') {
                        // Use global variable passed from context into JS to map the badge value into string
                        return `
                        <span class="badge align-middle paid-status" id="paid-status-badge-${row.id}"
                        data-id="${row.id}" data-value="${data}">${paidStatusChoices[data]}</span>
                        `;
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
                    let unArchiveBtn = `
                    <button class="btn btn-sm btn-warning un-archive-order-btn ms-1 ms-md-2"
                    id="un-archive-order-btn-${row.id}" value="${row.id}" aria-label="Un-archive order">
                    <i class="fa-solid fa-file-arrow-down"></i>
                    </button>`;

                    return deleteBtn + unArchiveBtn + '</div>';
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
        },
    });

    // Prevent triggering sorting when a user clicks in any of the inputs.
    // Sorting should apply when the user clicks any of the column headers
    $('#order-archive-table').on('click mousedown touchstart', 'input, select, button', function (e) {
        e.stopPropagation();
    });

    // Event listeners for filter inputs with debounce
    $('#filter-id, #filter-client, #filter-discount-min, #filter-discount-max, ' +
        '#filter-deposit-min, #filter-deposit-max, #filter-value-min, #filter-value-max, ' +
        '#filter-order-status, #filter-paid-status, #filter-date-from, #filter-date-to').on('keyup change', debounce(function () {
        // apply filters
        table.ajax.reload();
    }, 300));

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
    function unArchiveOrder(orderId) {
        // show spinner
        let spinner = document.getElementById('action-spinner');
        toggleSpinner(spinner);

        // API unarchive call for action
        $.ajax({
            url: `/api/orders/${orderId}/unarchive/`,
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
                                    An error occurred while un-archiving order ${orderId}:
                                    ${xhr.responseJSON.detail}
                                    ` || 'An error occurred while un-archiving the order.';
                displayMessage(errorMessage, 'error');
            }
        });
    };

    // initialize tooltips
    initTooltips();

    // ************** SECTION B: EVENT LISTENERS & HANDLERS *****************************************************************

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
        let unArchiveBtn = event.target.closest('.un-archive-order-btn');
        if (unArchiveBtn) {
            // get orderId from the button value
            let orderId = unArchiveBtn.value;
            // Set orderId as attribute for the modal to be used for front-end deletion
            unArchiveModalElement.setAttribute('data-order-id', orderId);
            // show the confirmation delete modal
            unArchiveModal.show();
        }
    });

    // add event listener on confirm delete button that will handle the deletion
    confirmUnArchiveBtn.addEventListener('click', () => {
        // Get order ID from modal attribute
        let orderId = unArchiveModalElement.getAttribute('data-order-id');
        if (orderId) {
            // Delete item
            unArchiveOrder(orderId);
            // Clear the data attribute
            unArchiveModalElement.removeAttribute('data-order-id');
        }
    });

    // add event listener to show/hide the row child with item details
    $('#order-archive-table tbody').on('click', 'td.details-control', function () {
        let tr = $(this).closest('tr');
        let row = table.row(tr);

        toggleChildRow(tr, row, true);
    });

    // Add event listener for clicks on clear filter btn
    $('#clear-filters-btn').on('click', function () {
        // clear filters on front-end and reload table
        clearDataTableFilters(table);
    });

});