$(document).ready(function () {
    $('#more_info_modal').modal({backdrop: 'static', keyboard: false});
});


$(document).on('blur keyup change click focus', '#more_info_modal', function () {
    if ($('#industry').val() !== '0'){
        if ($('#country').val() === '235'){
            if($('#zip').val().length === 5){
                $('#g_submit_more').removeAttr('disabled')
            }else{
                $('#g_submit_more').attr('disabled', '')
            }
        }else{
            if($('#city').val().length > 2){
                $('#g_submit_more').removeAttr('disabled')
            }else{
                $('#g_submit_more').attr('disabled', '')
            }
        }
    }else{
        $('#g_submit_more').attr('disabled', '')
    }

});

$(document).on('blur keyup change click focus', '#country', function () {
    if (this.value === '235'){
        $('#city_div').css({'display':'none'});
        $('#city_div').val('');
        $('#zip_div').css({'display':'block'})
    }else{
         $('#city_div').css({'display':'block'});
         $('#zip_div').val('');
        $('#zip_div').css({'display':'none'})
    }
});

function submit_form_more(){
    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
    $.ajax({
        type: 'POST',
        url: '/auth/submit_more_info',
        data: $('#form_more').serialize(),
        success: function (data) {
            if(data['status'] === 'success'){
                $('#loading_modal').modal('toggle');
                $('#loading_modal').css({'display':'none'});
                document.location = data['url']
            }else{
                custom_error_popup(data['message'])
            }
        },
        error: function () {
            error_popup()
        }
    });

}