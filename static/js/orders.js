document.addEventListener('DOMContentLoaded', function () {

    // Constant definitions
    const deleteModalElement = document.getElementById('DeleteOrderConfirmationModal');
    const deleteModal = new bootstrap.Modal(document.getElementById('DeleteOrderConfirmationModal'));
    const confirmDeleteBtn = document.getElementById("confirm-delete-order-btn");

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
    function deleteOrder(order) {
        debugger;
        if (order) {
            // delete row from table
            document.getElementById('orders-table').deleteRow(order.rowIndex);
        }
    };

    // ************** SECTION B: EVENT LISTENERS & HANDLERS *****************************************************************

    //   Handle item_status dropdown colouring dynamically
    let itemStatusSelects = document.querySelectorAll('.item-status-select');
    if (itemStatusSelects) {
        // Initial styling on page load
        updateSelectStyle();
    };

    // Add Click event listeners to handle dynamic deletion of order items
    document.addEventListener('click', function (event) {

        // get delete button as reference point. Allow clicking on icon inside
        let deleteBtn = event.target.closest('.delete-order-btn')
        if (deleteBtn) {
            // Set order item delete button as attribute for the modal
            deleteModalElement.setAttribute('data-target', deleteBtn.value);
            // Show confirmation modal
            deleteModal.show();
        }
    });

    confirmDeleteBtn.addEventListener('click', function (event) {

        // Get order item element to target for delete
        deleteBtnValue = deleteModalElement.getAttribute('data-target');
        targetOrder = document.getElementById(`order-${deleteBtnValue}`);
        // Delete item
        deleteOrder(targetOrder);
    });

});