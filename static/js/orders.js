document.addEventListener('DOMContentLoaded', function () {

    // ************** SECTION A: FUNCTION DEFINITIONS ********************************************************************

    // Define function that updates the item_status dropdown bg colour 
    function updateSelectStyle() {

        // Global constants definition
        let itemStatusSelects = document.querySelectorAll('.item-status-select');

        // loop through dropdowns
        itemStatusSelects.forEach(select => {
            // remove existing style classes
            select.classList.remove('bg-primary' ,'bg-pending', 'bg-success', 'bg-secondary');
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
      };

    // ************** SECTION B: EVENT LISTENERS & HANDLERS *****************************************************************

    //   Handle item_status dropdown colouring dynamically
    let itemStatusSelects = document.querySelectorAll('.item-status-select');
    if (itemStatusSelects) {
        // Initial styling on page load
        updateSelectStyle();
    };

});