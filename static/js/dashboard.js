import {
    ajaxSetupToken,
    displayMessage,
    formatWithThousandsSeparator,
    generateOptionsList,
    generateSelectOptions
} from "./utils.js";

$(document).ready(function () {

    // Define constants
    const csrftoken = document.querySelector("meta[name='csrf-token']").content;
    const pageSize = 25;

    // Setup AJAX to include CSRF token
    ajaxSetupToken(csrftoken);

    // Function to fetch and render the Debtors chart
    function RenderProdRevChart(filters = {}) {
        // API AJAX call to fetch revenue data and initialize product revenue chart
        $.ajax({
            url: '/api/product-revenue-data/',
            type: 'GET',
            data: filters,
            dataType: 'json',
            success: function (data) {
                // get product revenue chart element
                let ctx = document.getElementById('productRevenueChart').getContext('2d');

                // Destroy existing chart if it exists to prevent duplication
                if (window.productRevenueChart instanceof Chart) {
                    window.productRevenueChart.destroy();
                }

                // initialise new chart
                window.productRevenueChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Revenue (€)',
                            data: data.values,
                            backgroundColor: 'rgba(110, 196, 133, 0.6)',
                            borderColor: 'rgba(110, 196, 133, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Revenue (€)'
                                }
                            },
                            x: {
                                title: {
                                    display: false,
                                    text: 'Products'
                                }
                            }
                        },
                        plugins: {
                            title: {
                                display: true,
                                text: 'Revenue by Product'
                            },
                            legend: {
                                display: false
                            }
                        },
                        responsive: true,
                        maintainAspectRatio: true
                    }
                });

            },
            // Error handling
            error: function (xhr, status, error) {
                // display message
                let errorMessage = `
                                    Error fetching revenue data:
                                    error ${xhr.status} - ${error}: ${xhr.responseText ? xhr.responseText : ''}
                                    `;
                displayMessage(errorMessage, 'error');
            }
        });
    };

    // Handle Apply Product Revenue Filters Button Click
    $('#apply-prod-rev-filters').on('click', function () {
        // Gather filter values
        let revenueMin = $('#filter-prod-rev-min').val();
        let revenueMax = $('#filter-prod-rev-max').val();
        let dateFrom = $('#filter-prod-date-from').val();
        let dateTo = $('#filter-prod-date-to').val();

        // Build filters object
        let filters = {};

        if (revenueMin) {
            filters.revenue_min = revenueMin;
        }
        if (revenueMax) {
            filters.revenue_max = revenueMax;
        }
        if (dateFrom) {
            filters.date_from = dateFrom;
        }
        if (dateTo) {
            filters.date_to = dateTo;
        }

        // Fetch and render chart with filters
        RenderProdRevChart(filters);
    });

    // Handle Clear Product Revenue Filters Button Click
    $('#clear-prod-rev-filters').on('click', function () {
        // Clear filter values
        $('#filter-prod-rev-min').val('');
        $('#filter-prod-rev-max').val('');
        $('#filter-prod-date-from').val('');
        $('#filter-prod-date-to').val('');

        // Fetch and render chart without filters
        RenderProdRevChart();
    });

    // Function to fetch and render the Debtors chart
    function RenderDebtorsChart(filters = {}) {
        // API AJAX call to fetch debtors data and initialize debtors chart
        $.ajax({
            url: '/api/debtors-data/',
            type: 'GET',
            data: filters,
            dataType: 'json',
            success: function (data) {
                // get product revenue chart element
                let ctx = document.getElementById('debtorsChart').getContext('2d');
                // initialize chartjs chart
                let debtorsChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Debtors (€)',
                            data: data.values,
                            backgroundColor: 'rgba(75, 192, 192, 0.6)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Amounts Owed (€)'
                                }
                            },
                            x: {
                                title: {
                                    display: false,
                                    text: 'Clients'
                                }
                            }
                        },
                        plugins: {
                            title: {
                                display: true,
                                text: 'Amounts Owed by Client'
                            },
                            legend: {
                                display: false
                            }
                        },
                        responsive: true,
                        maintainAspectRatio: true
                    }
                });

                // Update Total amount owed
                let totalAmountOwed = formatWithThousandsSeparator(data.total);
                $('#total-debtor-bal').val(totalAmountOwed);
            },
            // Error handling
            error: function (xhr, status, error) {
                // display message
                let errorMessage = `
                                    Error fetching debtor data:
                                    error ${xhr.status} - ${error}: ${xhr.responseText ? xhr.responseText : ''}
                                    `;
                displayMessage(errorMessage, 'error');
            }
        });
    };

    // Function to fetch and render the Item Status by Product chart
    function RenderItemStatusProductChart(filters = {}) {
        // API AJAX call to fetch order items status data and initialize the doughnut chart
        $.ajax({
            url: '/api/item-status-product-data/',
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                let ctx = document.getElementById('orderItemStatusProductChart').getContext('2d');
                let orderItemsStatusChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: data.datasets
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Open Items by Status'
                            },
                            legend: {
                                display: true,
                                position: 'top',
                            },
                            tooltip: {
                                enabled: true
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                stacked: true,
                                title: {
                                    display: false,
                                    text: 'Count of Items'
                                },
                                ticks: {
                                    stepSize: 1
                                }
                            },
                            x: {
                                stacked: true,
                                title: {
                                    display: false,
                                    text: 'Item Status'
                                }
                            }
                        },
                    }
                });

                // Update Total Items display input
                let totalItems = formatWithThousandsSeparator(data.total_items);
                $('#total-open-items').val(totalItems);
            },
            // Error handling
            error: function (xhr, status, error) {
                // display message
                let errorMessage = `
                                    Error fetching item status data:
                                    error ${xhr.status} - ${error}: ${xhr.responseText ? xhr.responseText : ''}
                                    `;
                displayMessage(errorMessage, 'error');
            }
        });
    };

    // Function to fetch and render the Item Status by Product chart
    function RenderItemStatusConfigChart(filters = {}) {
        // API AJAX call to fetch order items status data and initialize the doughnut chart
        $.ajax({
            url: '/api/item-status-config-data/',
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                let ctx = document.getElementById('orderItemStatusConfigChart').getContext('2d');
                let orderItemsStatusChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Configuration Count',
                            data: data.values,
                            backgroundColor: data.colors,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Pending Items by Configuration'
                            },
                            legend: {
                                display: true,
                                position: 'top',
                            },
                            tooltip: {
                                enabled: true
                            }
                        },
                    }
                });
            },
            // Error handling
            error: function (xhr, status, error) {
                // display message
                let errorMessage = `
                                    Error fetching item status data:
                                    error ${xhr.status} - ${error}: ${xhr.responseText ? xhr.responseText : ''}
                                    `;
                displayMessage(errorMessage, 'error');
            }
        });
    };

    // Initialize DataTable with AJAX source and server-side processing
    let table = $('#orderitem-home-table').DataTable({
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

                // Append filter_type parameter
                d.filter_type = 'home_dashboard';

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
                    // for display purposes show the Font Awesome icon
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
                    // for filtering and sorting, return the underlying data
                    return data;
                },
                type: 'num' // to convert to binary for sorting
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

    // initial load
    RenderProdRevChart();
    RenderDebtorsChart();
    RenderItemStatusProductChart();
    RenderItemStatusConfigChart();

});