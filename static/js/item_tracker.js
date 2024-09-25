$(document).ready(function() {

    // Global constants definition
    const csrftoken = document.querySelector("meta[name='csrf-token']").content;

    // Setup AJAX to include CSRF token
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e., locally.
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Initialize DataTable with AJAX source and server-side processing
    let table = $('#orderitem-table').DataTable({
        serverSide: true,  // Enable server-side processing
        processing: true,
        ajax: {
            url: '/api/order_items/',
            type: 'GET',
            data: function(d) {
                // Map DataTables parameters to API query parameters

                // Calculate page number and page size
                let start = parseInt(d.start) || 0;
                let length = parseInt(d.length) || 10;
                let page = Math.floor(start / length) + 1;

                // Assign page and page size
                d.page = page;
                d.length = length;

                // Filtering parameters based on filters.py
                d.order = $('#filter-order').val();
                d.client = $('#filter-client').val();
                d.product = $('#filter-product').val();
                d.price_min = $('#filter-price-min').val();
                d.price_max = $('#filter-price-max').val();
                d.item_status = $('#filter-item-status').val();
                d.priority_level = $('#filter-priority-level').val();
                d.payment_status = $('#filter-payment-status').val();

                // Ordering parameters
                if (d.order && d.order.length > 0) {
                    let orderColumnIndex = d.order[0].column;
                    let orderDir = d.order[0].dir;
                    let orderColumn = d.columns[orderColumnIndex].data;
                    d.ordering = (orderDir === 'desc' ? '-' : '') + orderColumn;
                }

                return d;
            },
            dataSrc: function(json) {
                // Map API response to DataTables expected format
                json.recordsTotal = json.count;
                json.recordsFiltered = json.count;  // Adjust if you have separate counts
                console.log(json.results);
                return json.results;
            },
        },
        columns: [
            { data: 'id' },
            { data: 'order.id', name: 'order__id' },
            { data: 'order.client.client_name', name: 'order__client__client_name' },
            { data: 'product.name', name: 'product__name' },
            { data: 'item_value' },
            { data: 'item_status', name: 'item_status', render: function(data, type, row) {
                if(type === 'display'){
                    var select = '<select class="form-control item-status" data-id="' + row.id + '">';
                    select += '<option value="">All</option>';
                    // Assuming itemStatusChoices is a global variable passed from the template
                    itemStatusChoices.forEach(function(option) {
                        select += '<option value="' + option[0] + '"' + (option[0] === data ? ' selected' : '') + '>' + option[1] + '</option>';
                    });
                    select += '</select>';
                    return select;
                }
                return data;
            }},
            { data: 'priority_level', name: 'priority_level', render: function(data, type, row) {
                if(type === 'display'){
                    var select = '<select class="form-control priority-level" data-id="' + row.id + '">';
                    select += '<option value="">All</option>';
                    priorityLevelChoices.forEach(function(option) {
                        select += '<option value="' + option[0] + '"' + (option[0] === data ? ' selected' : '') + '>' + option[1] + '</option>';
                    });
                    select += '</select>';
                    return select;
                }
                return data;
            }},
            { data: 'order.paid', name: 'payment_status', render: function(data, type, row) {
                if(type === 'display'){
                    var select = '<select class="form-control payment-status" data-id="' + row.id + '">';
                    select += '<option value="">All</option>';
                    paymentStatusChoices.forEach(function(option) {
                        select += '<option value="' + option[0] + '"' + (option[0] === data ? ' selected' : '') + '>' + option[1] + '</option>';
                    });
                    select += '</select>';
                    return select;
                }
                return data;
            }},
            { data: null, orderable: false, searchable: false, render: function(data, type, row) {
                return '<button class="btn btn-danger btn-sm delete-orderitem action-btn" data-id="' + row.id + '">Delete</button>';
            }},
        ],
        order: [[0, 'asc']],  // Default ordering by ID ascending
    });

})