document.addEventListener('DOMContentLoaded', function () {

    // Constant definitions
    const deleteModalElement = document.getElementById('DeleteOrderConfirmationModal');
    const deleteModal = new bootstrap.Modal(document.getElementById('DeleteOrderConfirmationModal'));
    const confirmDeleteBtn = document.getElementById("confirm-delete-order-btn");
    const csrftoken = document.querySelector("meta[name='csrf-token']").content;
    const messageContainer = document.getElementById('msg-container');

    // ************** SECTION A: FUNCTION DEFINITIONS ********************************************************************

    // Define function that updates the item_status dropdown bg colour 
    function updateSelectStyle() {
        // Get select elements
        let itemStatusSelects = document.querySelectorAll('.item-status-select');
        let paidStatusSelects = document.querySelectorAll('.paid-status-select');

        // loop through item status dropdowns
        itemStatusSelects.forEach(select => {
            // remove existing style classes
            select.classList.remove('bg-primary', 'bg-warning', 'bg-success', 'bg-secondary', 'text-dark');
            // Not Started
            if (select.value == 1) {
                select.classList.add('bg-primary');
                // In Progress
            } else if (select.value == 2) {
                select.classList.add('bg-warning', 'text-dark');
                // Made
            } else if (select.value == 3) {
                select.classList.add('bg-success');
                // Delivered
            } else if (select.value == 4) {
                select.classList.add('bg-secondary');
            }
            // Add listener to update styling on change
            select.addEventListener('change', updateSelectStyle);
        });

        // loop through dropdowns
        paidStatusSelects.forEach(select => {
            // remove existing style classes
            select.classList.remove('bg-pending', 'bg-secondary', 'text-decoration-line-through', 'text-light');
            // Not Paid
            if (select.value == 1) {
                select.classList.add('bg-pending');
                // Fully Paid
            } else if (select.value == 2) {
                select.classList.add('bg-secondary', 'text-decoration-line-through', 'text-light');
            }
            // Add listener to update styling on change
            select.addEventListener('change', updateSelectStyle);
        });

    };

    // Define function that deletes an order item and remaining items index
    function deleteOrder(orderId) {
        // call delete_order API to handle deletion in the backend
        fetch(`/api/delete-order/${orderId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    // To identify AJAX request in the backend
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => {
                console.log(response);
                // handle bad reponse status
                if (!response.ok) {
                    if (response.status === 403) {
                        throw new Error('You do not have permission to delete this order.');
                    } else if (response.status === 404) {
                        throw new Error('Order was not found.');
                    } else {
                        throw new Error('Network response was not ok.');
                    }
                }
                return response.json();
            })
            .then(data => {
                console.log(data);
                if (data.success) {
                    // get order row element to target for deletion
                    const orderRow = document.getElementById(`order-${orderId}`);
                    // delete row from table to handle deletion in the front-end
                    // (will eliminate the need to redirect page)
                    if (orderRow) {
                        orderRow.remove();
                    }
                    // Remove the hidden row containing order items
                    const hiddenRow = orderRow.nextElementSibling;
                    if (hiddenRow) {
                       hiddenRow.remove();
                    }
                    // Display success messages
                    if (data.messages && data.messages.length > 0) {
                        displayMessages(data.messages);
                    }
                } else {
                    // Display error messages
                    if (data.messages && data.messages.length > 0) {
                        displayMessages(data.messages);
                    }
                }
            })
            // handle other errors
            .catch((error) => {
                console.error(`There was a problem with deleting order ${orderId}:`, error);
                displayMessages([{
                    level: 40,
                    level_tag: 'error',
                    message: `An error occurred: ${error.message}`
                }]);
            });
    };

    // Function to display messages
    function displayMessages(messages) {
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
    }

    // ************** SECTION B: EVENT LISTENERS & HANDLERS *****************************************************************

    //   Handle item_status dropdown colouring dynamically
    let itemStatusSelects = document.querySelectorAll('.item-status-select');
    if (itemStatusSelects) {
        // Initial styling on page load
        updateSelectStyle();
    };

    // add event listener that handles first delete button that will trigger the modal
    document.addEventListener("click", (event) => {
        // get delete button as reference point. Allow clicking on icon inside
        let deleteBtn = event.target.closest('.delete-order-btn')
        if (deleteBtn) {
            // get orderId from the button value
            let orderId = deleteBtn.value;
            // Set orderId as attribute for the modal to be used for front-end deletion
            deleteModalElement.setAttribute('data-order-id', orderId);
            // show the confirmation delete modal
            deleteModal.show();
        }
    });

    // add event listener on confirm delete button that will handle the deletion
    confirmDeleteBtn.addEventListener('click', () => {
        // Get order ID from modal attribute
        orderId = deleteModalElement.getAttribute('data-order-id');
        if (orderId) {
            // Delete item
            deleteOrder(orderId);
            // Clear the data attribute
            deleteModalElement.removeAttribute('data-order-id');
        }
    });

});