$(document).ready(function() {

    // Global constants definition
    const csrftoken = document.querySelector("meta[name='csrf-token']").content;

    // Setup AJAX to include CSRF token
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e., locally.
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

})