import {
    displayMessages,
    updateStatusStyle,
    ajaxSetupToken,
    applyFilters,
    debounce,
    initTooltips,

} from './utils.js'

$(document).ready(function () {

    // Constant definitions
    const deleteModalElement = document.getElementById('DeleteOrderConfirmationModal');
    const deleteModal = new bootstrap.Modal(document.getElementById('DeleteOrderConfirmationModal'));
    const confirmDeleteBtn = document.getElementById("confirm-delete-order-btn");
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
        // conditionally add bootstrap classes for each row when loaded
        createdRow: function (row, data, dataIndex) {
            if (data.order_status == 4 && data.paid == 1) {
                $(row).addClass('table-danger');
            } else if (data.order_status == 4 && data.paid == 2) {
                $(row).addClass('table-light opacity-50 shadow-none')
            }
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
                d.length = length;

                // Filtering parameters based on filters.py
                d.id = $('#filter-id').val();
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
                className: 'not-sortable',
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
                        let badge = `<badge class="badge position-relative order-status-badge align-middle item-status" 
                        data-id="${row.id}" data-value="${data}">${orderStatusChoices[data]}</badge>`;
                        return badge;
                    }
                    return data;
                }
            },
            {
                data: 'paid',
                render: function (data, type, row) {
                    if (type === 'display') {
                        let select = `<select class="form-select-sm paid-status fw-bolder text-wrap" data-id="${row.id}">`;
                        // Use global variable passed from context into JS and iterate through each key-value pair
                        Object.entries(paidStatusChoices).forEach(([optionInt, optionStr]) => {
                            select += '<option value="' + optionInt + '"' + (optionInt == data ? ' selected' : '') + '>' + optionStr + '</option>';
                        });
                        select += '</select>';
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
                    return `
                    <button type="button" id="delete-order-btn-${row.id}" name="delete_order"
                    class="btn btn-sm btn-danger delete-order-btn" value="${row.id}">
                    <i class="fa-solid fa-trash"></i>
                    </button>
                    `;
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
    $('#orderitem-table').on('click mousedown touchstart', 'input, select, button', function (e) {
        e.stopPropagation();
    });

    // Event listeners for filter inputs with debounce
    $('#filter-id, #filter-client, #filter-discount-min, #filter-discount-max, ' +
        '#filter-deposit-min, #filter-deposit-max, #filter-value-min, #filter-value-max, ' +
        '#filter-order-status, #filter-paid-status').on('keyup change', debounce(function () {
        applyFilters(table);
    }, 300));

    // Define function that deletes an order item and remaining items index
    function deleteOrder(orderId) {
        // call delete_order API to handle deletion in the backend
        fetch(`/api/delete-order/${orderId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    // To identify AJAX request in the backend
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => {
                console.log(response);
                // handle bad reponse status
                if (!response.ok) {
                    if (response.status === 403) {
                        throw new Error('You do not have permission to delete this order.');
                    } else if (response.status === 404) {
                        throw new Error('Order was not found.');
                    } else {
                        throw new Error('Network response was not ok.');
                    }
                }
                return response.json();
            })
            .then(data => {
                console.log(data);
                if (data.success) {
                    // get order row element to target for deletion
                    const orderRow = document.getElementById(`order-${orderId}`);
                    // delete row from table to handle deletion in the front-end
                    // (will eliminate the need to redirect page)
                    if (orderRow) {
                        orderRow.remove();
                    }
                    // Remove the hidden row containing order items
                    const hiddenRow = orderRow.nextElementSibling ? orderRow.nextElementSibling : null;
                    if (hiddenRow) {
                        hiddenRow.remove();
                    }
                    // Display success messages
                    if (data.messages && data.messages.length > 0) {
                        displayMessages(data.messages);
                    }
                } else {
                    // Display error messages
                    if (data.messages && data.messages.length > 0) {
                        displayMessages(data.messages);
                    }
                }
            })
            // handle other errors
            .catch((error) => {
                console.error(`There was a problem with deleting order ${orderId}:`, error);
                displayMessages([{
                    level: 40,
                    level_tag: 'error',
                    message: `An error occurred: ${error.message}`
                }]);
            });
    };

    // initialize tooltips
    initTooltips();

    // ************** SECTION B: EVENT LISTENERS & HANDLERS *****************************************************************

    //   Handle status dropdowns change colouring dynamically
    // Initial styling on page load
    updateStatusStyle();

    // add event listener that handles first delete button that will trigger the modal
    document.addEventListener("click", (event) => {
        // get delete button as reference point. Allow clicking on icon inside
        let deleteBtn = event.target.closest('.delete-order-btn')
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

});