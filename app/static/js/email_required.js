$(document).ready(function () {
    if ($('#main_body').children('div').length === 0){
        $('#container').prepend('<div id="email_verify-banner" class="alert alert-info email_verify-banner no-highlight" role="alert">Please verify your email -- <span class="re_send_confirmation">click here to receive another confirmation</div>')
    }else{
        $('#main_body').prepend('<div id="email_verify-banner" class="alert alert-info email_verify-banner no-highlight" role="alert">Please verify your email -- <span class="re_send_confirmation">click here to receive another confirmation</div>')
    }
});


$(document).on('click', '.re_send_confirmation', function () {
    $.ajax({
        type: 'POST',
        url: '/auth/send_new_confirmation_email',
        success: function (data) {
            if (data['status'] === 'success'){
               $('#email_verify-banner').css({'background-color': '#4D80E4'});
               $('#email_verify-banner').html(data['message'])
           }else if(data['status'] === 'error'){
               $('#email_verify-banner').html(data['message'])
           }
        },
        error: function () {
            error_popup()
        }
    });
});