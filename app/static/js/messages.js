$(document).on('click', '#submit_msg', function (e) {
    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
    e.preventDefault();
    if($('#message').val().length > 0){
        $.ajax({
            type: 'POST',
            url: $('#message_form').attr('action'),
            data: $('#message_form').serialize(),
            success: function () {
                window.location.reload()
            },
            error: function () {
                error_popup()
            }
        })
    }
})