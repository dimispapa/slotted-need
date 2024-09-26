$(document).ready(function () {

    // Global constants definition
    const csrftoken = document.querySelector("meta[name='csrf-token']").content;
    const pageSize = 25;

    // Setup AJAX to include CSRF token
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e., locally.
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Initialize DataTable with AJAX source and server-side processing
    let table = $('#orderitem-table').DataTable({
        serverSide: true, // Enable server-side processing
        processing: true,  // Enables processing animation
        orderCellsTop: true,  // Place sorting icons to top row
        fixedHeader: true,  // Fix the header when scrolling
        searching: false,  // Disable global search as using column filters
        scrollY: true, // Enable vertical scrolling
        scrollX: true, // Enable horizontal scrolling
        pageLength: pageSize,
        ajax: {
            url: '/api/order_items/',
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
                d.component_finishes = $('#filter-component-finishes').val();
                d.value_min = $('#filter-value-min').val();
                d.value_max = $('#filter-value-max').val();
                d.item_status = $('#filter-item-status').val();
                d.priority_level = $('#filter-priority-level').val();
                d.payment_status = $('#filter-payment-status').val();

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
                data: 'id'
            },
            {
                data: 'order.id',
                name: 'order__id'
            },
            {
                data: 'order.client.client_name',
                name: 'order__client__client_name'
            },
            {
                data: 'product.name',
                name: 'product__name'
            },
            {
                data: 'option_values',
                orderable: false,  // Disable ordering
                render: function (data, type, row) {
                    if (type === 'display') {
                        if(!data || data.length === 0){
                            return '-';
                        }
                        let list = '<ul class="option-values-list">';
                        data.forEach(function(option) {
                            list += '<li>' + option.value + '</li>';
                        });
                        list += '</ul>';
                        return list;
                    }
                    return data;
                }
            },
            {
                data: 'product_finish',
                name: 'product_finish__name',
                render: function (data, type, row) {
                    if (type === 'display') {
                        return data ? data.name : '-';
                    }
                    return data;
                }
            },
            {
                data: 'item_component_finishes',
                orderable: false,  // Disable ordering
                render: function (data, type, row) {
                    if(type === 'display'){
                        if(!data || data.length === 0){
                            return '-';
                        }
                        let list = '<ul class="component-finish-list">';
                        data.forEach(function(cf) {
                            list += '<li>' + cf.component_finish_display + '</li>';
                        });
                        list += '</ul>';
                        return list;
                    }
                    return data;
                }
            },
            {
                data: 'item_value'
            },
            {
                data: 'item_status',
                render: function (data, type, row) {
                    if (type === 'display') {
                        let select = '<select class="form-select item-status" data-id="' + row.id + '">';
                        select += '<option value="">All</option>';
                        // Use global variable passed from context into JS
                        itemStatusChoices.forEach(function (option) {
                            select += '<option value="' + option[0] + '"' + (option[0] === data ? ' selected' : '') + '>' + option[1] + '</option>';
                        });
                        select += '</select>';
                        return select;
                    }
                    return data;
                }
            },
            {
                data: 'priority_level',
                render: function (data, type, row) {
                    if (type === 'display') {
                        let select = '<select class="form-select priority-level" data-id="' + row.id + '">';
                        select += '<option value="">All</option>';
                        // Use global variable passed from context into JS
                        priorityLevelChoices.forEach(function (option) {
                            select += '<option value="' + option[0] + '"' + (option[0] === data ? ' selected' : '') + '>' + option[1] + '</option>';
                        });
                        select += '</select>';
                        return select;
                    }
                    return data;
                }
            },
            {
                data: 'order.paid',
                name: 'order__paid',
                render: function (data, type, row) {
                    if (type === 'display') {
                        let select = '<select class="form-select payment-status" data-id="' + row.id + '">';
                        select += '<option value="">All</option>';
                        // Use global variable passed from context into JS
                        paymentStatusChoices.forEach(function (option) {
                            select += '<option value="' + option[0] + '"' + (option[0] === data ? ' selected' : '') + '>' + option[1] + '</option>';
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
                searchable: false,
                render: function (data, type, row) {
                    return '<button class="btn btn-danger btn-sm delete-orderitem action-btn" data-id="' + row.id + '"><i class="fa-solid fa-trash"></i></button>';
                }
            },
        ],
        // Default ordering by ID ascending
        id: [
            [0, 'asc']
        ],
    });

    // Prevent triggering sorting when a user clicks in any of the inputs.
    // Sorting should apply when the user clicks any of the column headers
    $('#orderitem-table').on('click mousedown touchstart', 'input, select, button', function(e) {
        e.stopPropagation();
    });

    // Function to reload table with new filters
    function applyFilters() {
        table.ajax.reload();
    }

    // Debounce function to limit the rate of function execution
    function debounce(func, delay) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), delay);
        }
    }

    // Event listeners for filter inputs with debounce
    $('#filter-id, #filter-order, #filter-client, #filter-product, #filter-value-min, ' +
        '#filter-value-max, #filter-item-status, #filter-priority-level, #filter-payment-status, ' +
        '#filter-design-options, #filter-product-finish, #filter-component-finishes').on('keyup change', debounce(function () {
        applyFilters();
    }, 300));

})