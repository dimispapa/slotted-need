// ***** Util functions related to general DOM manipulation, generation of HTML elements and styling **********

// Function to display messages
function displayMessage(message, type) {

    // Use Bootstrap alert classes based on the message type
    let alertClass = 'alert-secondary';
    switch (type) {
        case 'debug':
        case 'success':
            alertClass = 'alert-success';
            break;
        case 'error':
            alertClass = 'alert-danger';
            break;
        case 'warning':
            alertClass = 'alert-warning';
            break;
        case 'info':
            alertClass = 'alert-info';
    }
    // Create the alert element
    let alert = `<div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                 </div>`;
    // Append to a container in your HTML
    $('#msg-container').html(alert);
};

function displayMessages(messages) {

    const messageContainer = document.getElementById('msg-container');
    // Clear existing messages
    messageContainer.innerHTML = '';

    messages.forEach(msg => {
        // Create a div for each message
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('alert', 'alert-dismissible', 'fade', 'show');
        // Determine the alert class based on message level
        switch (msg.level_tag) {
            case 'debug':
            case 'info':
                messageDiv.classList.add('alert-info');
                break;
            case 'success':
                messageDiv.classList.add('alert-success');
                break;
            case 'warning':
                messageDiv.classList.add('alert-warning');
                break;
            case 'error':
                messageDiv.classList.add('alert-danger');
                break;
            default:
                messageDiv.classList.add('alert-secondary');
        }

        messageDiv.setAttribute('role', 'alert');
        messageDiv.innerText = msg.message;

        // add a close button
        const closeBtn = document.createElement('button');
        closeBtn.type = 'button';
        closeBtn.classList.add('btn-close');
        closeBtn.setAttribute('data-bs-dismiss', 'alert');
        closeBtn.setAttribute('aria-label', 'Close');
        messageDiv.appendChild(closeBtn);

        // Append the message to the container
        messageContainer.appendChild(messageDiv);
    });
};

// Define function that updates statuses bg colour with default parameters set initially
function updateStatusStyle() {

    // get the elements on initial load
    let itemStatuses = document.querySelectorAll('.item-status');
    // loop through item status elements
    if (itemStatuses && itemStatuses.length > 0) {
        for (let status of itemStatuses) {
            // update status style
            updateItemStatusStyle(status);
            // Add listener to update styling on change
            status.addEventListener('change', (event) => updateItemStatusStyle(event.target));
        }
    }

    // get the elements on initial load
    let paidStatuses = document.querySelectorAll('.paid-status');
    // loop through paid status elements
    if (paidStatuses && paidStatuses.length > 0) {
        for (let status of paidStatuses) {
            // update status style
            updatePaidStatusStyle(status);
            // Add listener to update styling on change
            status.addEventListener('change', (event) => updatePaidStatusStyle(event.target));
        }
    }

    // get the elements on initial load
    let priorityStatuses = document.querySelectorAll('.priority-status');
    // loop through priority status elements
    if (priorityStatuses && priorityStatuses.length > 0) {
        for (let status of priorityStatuses) {
            // update status style
            updatePriorityStatusStyle(status);
            // Add listener to update styling on change
            status.addEventListener('change', (event) => updatePriorityStatusStyle(event.target));
        }
    }
};

function updateItemStatusStyle(status) {
    // remove existing style classes
    status.classList.remove('bg-pending', 'bg-warning', 'bg-success', 'bg-secondary', 'text-dark', 'text-light');
    // get status value differently depending if it's a select or different element
    let statusValue = (status.tagName == 'SELECT') ? status.value : status.getAttribute('data-value');

    // Not Started
    if (statusValue == 1) {
        status.classList.add('bg-pending', 'text-dark');
        // In Progress
    } else if (statusValue == 2) {
        status.classList.add('bg-warning', 'text-dark');
        // Made
    } else if (statusValue == 3) {
        status.classList.add('bg-success', 'text-light');
        // Delivered
    } else if (statusValue == 4) {
        status.classList.add('bg-secondary', 'text-light');
    }
};

function updatePaidStatusStyle(status) {
    // Set boostrap class prefix dynamically based on element type and also get status value integer
    let bsTag = (status.tagName == 'BUTTON') ? 'btn' : 'bg';
    // get status value differently depending if it's a select or different element
    let statusValue = (status.tagName == 'SELECT') ? status.value : status.getAttribute('data-value');
    // remove existing style classes
    status.classList.remove(`${bsTag}-danger`, `${bsTag}-secondary`, 'text-light');

    // Not Paid
    if (statusValue == 1) {
        status.classList.add(`${bsTag}-danger`, 'text-light');
        // Fully Paid
    } else if (statusValue == 2) {
        status.classList.add(`${bsTag}-secondary`, 'text-light');
    }
};

function updatePriorityStatusStyle(status) {
    // remove existing style classes
    status.classList.remove('bg-danger', 'bg-light', 'bg-warning', 'text-dark', 'text-light');
    // get status value differently depending if it's a select or different element
    let statusValue = (status.tagName == 'SELECT') ? status.value : status.getAttribute('data-value');

    // Low priority
    if (statusValue == 1) {
        status.classList.add('bg-light', 'text-dark');
        // Medium priority
    } else if (statusValue == 2) {
        status.classList.add('bg-warning', 'text-dark');
        // High priority
    } else if (statusValue == 3) {
        status.classList.add('bg-danger', 'text-light');
    }
};

// initialize tooltips
function initTooltips() {
    $('[data-toggle="tooltip"]').tooltip()
};

// Function that generates options for select html element
function generateSelectOptions(choices, selectedValue) {
    let options = '';
    for (let [value, string] of Object.entries(choices)) {
        options += `<option value="${value}" ${value == selectedValue ? 'selected' : ''}>${string}</option>`;
    }
    return options;
}

// Function that generates component finishes ul element
function generateOptionsList(type, data) {
    if (!data || data.length === 0) {
        return '-';
    }
    let list = `<ul class="${type}-list list-unstyled mb-0 lh-sm">`;
    for (let option of data) {

        if (type == 'component_finishes') {
            list += '<li>' + option.component_finish_display + '</li>';
        } else if (type == 'option_values') {
            list += '<li>' + option.value + '</li>';
        } else {
            list += '<li>' + option.name + '</li>';
        }
    };
    list += '</ul>';
    return list;
};

//*********** Util functions related to DataTables and AJAX operations *********************

// Function to set up AJAX with CSRF token
function ajaxSetupToken(csrftoken) {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e., locally.
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
};

// Debounce function to limit the rate of function execution
function debounce(func, delay) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    }
};

// Function to hide spinner
function toggleSpinner(spinner) {
    if (spinner.classList.contains('d-none')) {
        spinner.classList.remove('d-none')
    } else {
        spinner.classList.add('d-none')
    }
};

// Function that formats the order item data into html tr and td elements
function formatOrderItems(orderItems) {
    let html = '<table class="table table-sm table-hover table-bordered border-primary">';
    html += `
            <thead>
                <tr>
                    <th>Item ID</th>
                    <th>Product</th>
                    <th>Design Options</th>
                    <th>Product Finish</th>
                    <th>Component Finishes</th>
                    <th>Item Value</th>
                    <th>Item Status</th>
                    <th>Priority Level</th>
                    <th>Completed</th>
                </tr>
            </thead>
            <tbody>`;

    orderItems.forEach(function (item) {
        html += `
            <tr>
                <td>${item.id}</td>
                <td>${item.product.name}</td>
                <td>${generateOptionsList('option_values', item.option_values)}</td>
                <td>${item.product_finish ? item.product_finish : '-'}</td>
                <td>${generateOptionsList('component_finishes', item.item_component_finishes)}</td>
                <td>€${item.item_value}</td>
                <td>
                    <select class="form-select-sm fw-bolder text-wrap item-status" data-id="${item.id}">
                        ${generateSelectOptions(itemStatusChoices, item.item_status)}
                    </select>
                    <span class="text-center inline-spinner-div">
                        <div class="spinner-border text-primary d-none" role="status" id="item-status-spinner-${item.id}">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </span>
                </td>
                <td>
                    <select class="form-select-sm fw-bolder text-wrap priority-status" data-id="${item.id}">
                        ${generateSelectOptions(priorityLevelChoices, item.priority_level)}
                    </select>
                    <span class="text-center inline-spinner-div">
                        <div class="spinner-border text-primary d-none" role="status" id="priority-status-spinner-${item.id}">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </span>
                </td>
                <td>
                    ${item.completed === true ? '<p class="text-center mb-0"><i class="fa-solid fa-square-check text-success fs-2 fw-bolder" aria-label="Completed"></i></p>' : ''}
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    return html;
};

// Function that formats the order item data into html tr and td elements
function formatOrderItemsArchive(orderItems) {
    let html = '<table class="table table-sm table-hover table-bordered border-primary">';
    html += `
            <thead>
                <tr>
                    <th>Item ID</th>
                    <th>Product</th>
                    <th>Design Options</th>
                    <th>Product Finish</th>
                    <th>Component Finishes</th>
                    <th>Item Value</th>
                    <th>Item Status</th>
                </tr>
            </thead>
            <tbody>`;

    orderItems.forEach(function (item) {
        html += `
            <tr>
                <td>${item.id}</td>
                <td>${item.product.name}</td>
                <td>${generateOptionsList('option_values', item.option_values)}</td>
                <td>${item.product_finish ? item.product_finish : '-'}</td>
                <td>${generateOptionsList('component_finishes', item.item_component_finishes)}</td>
                <td>€${item.item_value}</td>
                <td>
                    <span class="badge align-middle item-status" id="order-status-badge-${item.id}"
                    data-id="${item.id}" data-value="${item.item_status}">${itemStatusChoices[item.item_status]}
                    </span>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    return html;
};

// Function that uses the order_items API to fetch item details for an order
function fetchOrderItems(orderId, archive, callback) {
    $.ajax({
        url: `/api/order-items/?order_id=${orderId}`,
        method: 'GET',
        success: function (data) {
            // store item data in a variable
            let orderItems = data.results || data;
            // format item data into html elements
            if (archive) {
                let orderItemsHtml = formatOrderItemsArchive(orderItems);
                // call the callback function to add and show order items
                callback(orderItemsHtml);
            } else {
                let orderItemsHtml = formatOrderItems(orderItems);
                // call the callback function to add and show order items
                callback(orderItemsHtml);
            }
        },
        error: function (xhr, status, error) {
            console.error('Error fetching order items:', xhr.responseText);
            // call callback function returning an error message div
            callback('<div>Error loading order items.</div>');
        }
    });
};

// Show/hide the child rows to show order items of orders
function toggleChildRow(tr, row, archive) {
    if (row.child.isShown()) {
        // Close the child row
        row.child.hide();
        tr.removeClass('shown');
    } else {
        // Open the child row
        // Fetch order items via AJAX
        let orderId = row.data().id;
        fetchOrderItems(orderId, archive, function (orderItemsHtml) {
            // callback function to add and show row child with order items
            row.child(orderItemsHtml).show();
            tr.addClass('shown');
            updateStatusStyle();
        });
    }
};

// Function that formats a number into a string with thousand separator commas
function formatWithThousandsSeparator(num) {
    let numAsString = num.toString();
    let characters = numAsString.split("").reverse();
    let parts = [];
    for (let i = 0; i < characters.length; i += 3) {
        let part = characters.slice(i, i + 3).reverse().join("");
        parts.unshift(part);
    }
    return parts.join(",");
};

// Function that clear filters on the DataTable
function clearDataTableFilters(table) {
    // get input elements and clear the values
    let inputs = $('#filter-row th input.form-control');
    for (let input of inputs) {
        input.value = '';
    };
    // get select elements and clear the values
    let selects = $('#filter-row th select');
    for (let select of selects) {
        select.value = 'All';
    };
    // Reload the table
    table.ajax.reload();
};

export {
    displayMessages,
    displayMessage,
    updateStatusStyle,
    updateItemStatusStyle,
    updatePaidStatusStyle,
    debounce,
    ajaxSetupToken,
    initTooltips,
    generateSelectOptions,
    generateOptionsList,
    toggleSpinner,
    toggleChildRow,
    fetchOrderItems,
    formatWithThousandsSeparator,
    clearDataTableFilters
};