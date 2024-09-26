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

// Define function that updates the item_status and paid_status dropdown bg colour
function updateSelectStyle() {
    // Get select elements
    let itemStatusSelects = document.querySelectorAll('.item-status-select');
    let paidStatusSelects = document.querySelectorAll('.paid-status-select');
    let priorityStatusSelects = document.querySelectorAll('.priority-status-select');

    // loop through item status dropdowns
    if (itemStatusSelects && itemStatusSelects.length > 0) {

        itemStatusSelects.forEach(select => {
            // remove existing style classes
            select.classList.remove('bg-pending', 'bg-warning', 'bg-success', 'bg-secondary', 'text-dark', 'text-light');

            // Not Started
            if (select.value == 1) {
                select.classList.add('bg-pending', 'text-dark');
                // In Progress
            } else if (select.value == 2) {
                select.classList.add('bg-warning', 'text-dark');
                // Made
            } else if (select.value == 3) {
                select.classList.add('bg-success', 'text-light');
                // Delivered
            } else if (select.value == 4) {
                select.classList.add('bg-secondary', 'text-light');
            }
            // Add listener to update styling on change
            select.addEventListener('change', updateSelectStyle);
        });
    }

    // loop through paid status dropdowns
    if (paidStatusSelects && paidStatusSelects.length > 0) {

        paidStatusSelects.forEach(select => {
            // remove existing style classes
            select.classList.remove('bg-danger-light', 'bg-secondary', 'text-dark', 'text-light');

            // Not Paid
            if (select.value == 1) {
                select.classList.add('bg-danger-light', 'text-dark');
                // Fully Paid
            } else if (select.value == 2) {
                select.classList.add('bg-secondary', 'text-light');
            }
            // Add listener to update styling on change
            select.addEventListener('change', updateSelectStyle);
        });
    }

    // loop through paid status dropdowns
    if (priorityStatusSelects && priorityStatusSelects.length > 0) {

        priorityStatusSelects.forEach(select => {
            // remove existing style classes
            select.classList.remove('bg-danger-light', 'bg-light', 'bg-warning', 'text-dark');

            // Low priority
            if (select.value == 1) {
                select.classList.add('bg-light', 'text-dark');
                // Medium priority
            } else if (select.value == 2) {
                select.classList.add('bg-warning', 'text-dark');
                // High priority
            } else if (select.value == 3) {
                select.classList.add('bg-danger-light', 'text-dark');
            }
            // Add listener to update styling on change
            select.addEventListener('change', updateSelectStyle);
        });
    }
};


export {
    displayMessages,
    updateSelectStyle
};