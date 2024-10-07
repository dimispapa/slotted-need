import {
    ajaxSetupToken,
    displayMessage
} from "./utils.js";

$(document).ready(function () {

    // Define constants
    const csrftoken = document.querySelector("meta[name='csrf-token']").content;

    // Setup AJAX to include CSRF token
    ajaxSetupToken(csrftoken);

    // API AJAX call to fetch revenue data and initialize product revenue chart
    $.ajax({
        url: '/api/product-revenue-data/',
        type: 'GET',
        dataType: 'json',
        success: function (response) {
            // get data
            let data = response;
            // get product revenue chart element
            let ctx = document.getElementById('productRevenueChart').getContext('2d');
            // initialize chartjs chart
            let revenueChart = new Chart(ctx, {
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
                                ${xhr.status} error - ${error}
                                `;
            displayMessage(errorMessage, 'error');
        }
    });

    // API AJAX call to fetch debtors data and initialize debtors chart
    $.ajax({
        url: '/api/debtors-data/',
        type: 'GET',
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
                            text: 'Amounts owed by Client'
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
                                ${xhr.status} error - ${error}
                                `;
            displayMessage(errorMessage, 'error');
        }
    });

    // API AJAX call to fetch order items status data and initialize the doughnut chart
    $.ajax({
        url: '/api/item-status-data/',
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            let ctx = document.getElementById('orderItemStatusChart').getContext('2d');
            let orderItemsStatusChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels, // e.g., ['Not Started', 'In Progress', ...]
                    datasets: [{
                        data: data.values, // e.g., [10, 5, 15, 20]
                        backgroundColor: [
                            '#e3ff2c', // Not Started
                            'rgb(255 193 7)', // In Progress
                            'rgb(25 135 84)', // Made
                            'rgb(108 117 125)' // Delivered
                        ],
                        borderColor: [
                            '#e3ff2c',
                            'rgb(255 193 7)',
                            'rgb(25 135 84)',
                            'rgb(108 117 125)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false, // Allows the chart to fill the container
                    plugins: {
                        title: {
                            display: true,
                            text: 'Order Items by Status'
                        },
                        legend: {
                            display: true,
                            position: 'top',
                        },
                        tooltip: {
                            enabled: true
                        }
                    }
                }
            });
        },
        // Error handling
        error: function (xhr, status, error) {
            // display message
            let errorMessage = `
                                Error fetching item status data:
                                ${xhr.status} error - ${error}
                                `;
            displayMessage(errorMessage, 'error');
        }
    });
});