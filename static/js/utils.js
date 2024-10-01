// Function to display messages
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
function updateStatusStyle(
    itemStatusClass = '.item-status',
    paidStatusClass = '.paid-status',
    priorityStatusClass = '.priority-status'
) {
    // get the elements on initial load
    let itemStatuses = document.querySelectorAll(itemStatusClass);
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
    let paidStatuses = document.querySelectorAll(paidStatusClass);
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
    let priorityStatuses = document.querySelectorAll(priorityStatusClass);
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
    // get status value differently depending if it's a select or badge element
    let statusValue = (status.tagName == 'BADGE') ? status.getAttribute('data-value') : status.value;

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
    let statusValue = (status.tagName == 'BUTTON') ? status.getAttribute('data-value') : status.value;
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

    // Low priority
    if (status.value == 1) {
        status.classList.add('bg-light', 'text-dark');
        // Medium priority
    } else if (status.value == 2) {
        status.classList.add('bg-warning', 'text-dark');
        // High priority
    } else if (status.value == 3) {
        status.classList.add('bg-danger', 'text-light');
    }
};

// initialize tooltips
function initTooltips() {
    $('[data-toggle="tooltip"]').tooltip()
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

// Function to reload table with new filters
function applyFilters(table) {
    table.ajax.reload();
};

// Debounce function to limit the rate of function execution
function debounce(func, delay) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    }
};

export {
    displayMessages,
    updateStatusStyle,
    updatePaidStatusStyle,
    applyFilters,
    debounce,
    ajaxSetupToken,
    initTooltips
};