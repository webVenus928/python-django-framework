

// Put the class .tr-link on any <tr> tag to make it a clickable row link
$(document).ready(function() {
    $(".tr-link").click(function() {
        window.location = $(this).data("href");
    });
});