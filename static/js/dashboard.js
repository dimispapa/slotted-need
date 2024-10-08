import {
    ajaxSetupToken,
    displayMessage,
    formatWithThousandsSeparator
} from "./utils.js";

$(document).ready(function () {

    // Define constants
    const csrftoken = document.querySelector("meta[name='csrf-token']").content;

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
            success: function (response) {
                // get data
                let data = response;
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
            success: function (response) {
                // get data
                let data = response;
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

    // API AJAX call to fetch order items status data and initialize the doughnut chart
    $.ajax({
        url: '/api/item-status-data/',
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            let ctx = document.getElementById('orderItemStatusChart').getContext('2d');
            let orderItemsStatusChart = new Chart(ctx, {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false, // Allows the chart to fill the container
                    plugins: {
                        title: {
                            display: true,
                            text: 'Open Order Items by Status'
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

    // initial load
    RenderProdRevChart();
    RenderDebtorsChart();

});