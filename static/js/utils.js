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
    itemStatusClass='.item-status-select',
    paidStatusClass='.paid-status-select',
    priorityStatusClass='.priority-status-select'
) {
    // Get elements
    let itemStatuses = document.querySelectorAll(itemStatusClass);
    let paidStatuses = document.querySelectorAll(paidStatusClass);
    let priorityStatuses = document.querySelectorAll(priorityStatusClass);

    // loop through item status
    if (itemStatuses && itemStatuses.length > 0) {

        itemStatuses.forEach(status => {
            // remove existing style classes
            status.classList.remove('bg-pending', 'bg-warning', 'bg-success', 'bg-secondary', 'text-dark', 'text-light');

            // Not Started
            if (status.value == 1) {
                status.classList.add('bg-pending', 'text-dark');
                // In Progress
            } else if (status.value == 2) {
                status.classList.add('bg-warning', 'text-dark');
                // Made
            } else if (status.value == 3) {
                status.classList.add('bg-success', 'text-light');
                // Delivered
            } else if (status.value == 4) {
                status.classList.add('bg-secondary', 'text-light');
            }
            // Add listener to update styling on change
            status.addEventListener('change', updateStatusStyle);
        });
    }

    // loop through paid status
    if (paidStatuses && paidStatuses.length > 0) {

        paidStatuses.forEach(status => {
            // Set boostrap class prefix dynamically based on element type and also get status value integer
            let bsTag = (status.tagName == 'BUTTON') ? 'btn' : 'bg'
            let statusValue = (status.tagName == 'BUTTON') ? status.getAttribute('data-value') : status.value
            // remove existing style classes
            status.classList.remove(`${bsTag}-danger`, `${bsTag}-secondary`, 'text-light');

            // Not Paid
            if (statusValue == 1) {
                status.classList.add(`${bsTag}-danger`, 'text-light');
                // Fully Paid
            } else if (statusValue == 2) {
                status.classList.add(`${bsTag}-secondary`, 'text-light');
            }
            // Add listener to update styling on change
            status.addEventListener('change', updateStatusStyle);
        });
    }

    // loop through paid status
    if (priorityStatuses && priorityStatuses.length > 0) {

        priorityStatuses.forEach(status => {

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
            // Add listener to update styling on change
            status.addEventListener('change', updateStatusStyle);
        });
    }
};


export {
    displayMessages,
    updateStatusStyle
};