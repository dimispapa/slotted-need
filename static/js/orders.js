document.addEventListener('DOMContentLoaded', function () {

    // ************** SECTION A: FUNCTION DEFINITIONS ********************************************************************

    // Define function that updates the item_status dropdown bg colour 
    function updateSelectStyle() {

        // Get select elements
        let itemStatusSelects = document.querySelectorAll('.item-status-select');
        let paidStatusSelects = document.querySelectorAll('.paid-status-select');

        // loop through item status dropdowns
        itemStatusSelects.forEach(select => {
            // remove existing style classes
            select.classList.remove('bg-primary', 'bg-pending', 'bg-success', 'bg-secondary');
            // Not Started
            if (select.value == 1) {
                select.classList.add('bg-primary');
                // In Progress
            } else if (select.value == 2) {
                select.classList.add('bg-pending');
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
            select.classList.remove('bg-notice', 'bg-secondary', 'text-decoration-line-through', 'text-light');
            // Not Paid
            if (select.value == 1) {
                select.classList.add('bg-notice');
                // Fully Paid
            } else if (select.value == 2) {
                select.classList.add('bg-secondary', 'text-decoration-line-through', 'text-light');
            }
            // Add listener to update styling on change
            select.addEventListener('change', updateSelectStyle);
        });

    };

    // ************** SECTION B: EVENT LISTENERS & HANDLERS *****************************************************************

    //   Handle item_status dropdown colouring dynamically
    let itemStatusSelects = document.querySelectorAll('.item-status-select');
    if (itemStatusSelects) {
        // Initial styling on page load
        updateSelectStyle();
    };

});