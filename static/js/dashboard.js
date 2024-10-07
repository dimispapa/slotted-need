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
                    labels: data.product_names,
                    datasets: [{
                        label: 'Revenue (€)',
                        data: data.revenue_values,
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
});
