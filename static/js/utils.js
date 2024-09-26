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

export {
    displayMessages
};

