$(document).ready(function () {
    $("#submit_resume").click(function() {
        $('#recruiting_enroll_resume').modal('toggle');
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        var fd = new FormData();
        var files = $('#resume')[0].files[0];
        fd.append('resume', files);
        $.ajax({
                    url: '/enroll_resume_upload',
                    type: 'post',
                    data: fd,
                    contentType: false,
                    processData: false,
                    success: function(response){
                        if (response['value'] === 'success'){
                            var data = response;
                            $('#loading_modal').modal('hide');
                            for (i = 0; i < data['institutions'].length; i++){
                                $('#institutions_confirm').append('<li class="institution_attended" id="' + data['institutions'][i]['id'].toString() +'">' + data['institutions'][i]['name'].toString() + '<button style="margin-left: 15px" type="button" class="close remove_institution">\n' +
                                    '                                  <span aria-hidden="true" style="color: red">&times;</span>\n' +
                                    '                                </button></li>');
                            }
                            for (i = 0; i < data['employers'].length; i++){
                                $('#employers_confirm').append('<li class="employer_attended" id="' +  data['employers'][i]['id'].toString() +'">' + data['employers'][i]['name'].toString() + '<button style="margin-left: 15px" type="button" class="close remove_employer">\n' +
                                    '                                  <span aria-hidden="true" style="color: red">&times;</span>\n' +
                                    '                                </button></li>');
                            }
                            $('#recruiting_enroll_confirm').modal({backdrop: 'static', keyboard: false});

                        }else{

                        }
                    },
                    error: function () {
                        error_popup()
                    }
                });
    })
});


$(document).on('click', '#submit_new_institution', function () {
    var n = check_input_length($('#institution_name'), 3);
    var l = check_input_length($('#institution_city'), 5);
    if (n && l){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        var data = {'i':$('#institution_name').val(), 'l':$('#institution_city').val()};
        $.ajax({
            type: 'POST',
            url: '/add_institution_recruiting',
            data: data,
            success: function (response) {
                if (response['status'] === 'success'){
                    $('#institutions_confirm').append('<li class="institution_attended" id="'+ response['id'].toString() +'">' + $("#institution_name").val() + '<button style="margin-left: 15px" type="button" class="close remove_institution" >\n' +
                    '                                  <span aria-hidden="true" style="color: red">×</span>\n' +
                    '                                </button></li>')
                    $('#institution_name').val('');
                    $('#institution_city').val('');
                    $('#add_institution').modal('hide');
                    $('#loading_modal').modal('toggle');
                    ensure_minimums(document.getElementById('confirm_data_btn'))
                }else{
                    $('#institution_name').val('');
                    $('#institution_city').val('');
                    $('#add_institution').modal('hide');
                    $('#loading_modal').modal('toggle');
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                error_popup()
            }
        })
    }

})

$(document).on('click', '#submit_new_employer', function () {
    var name = check_input_length($('#employer_name'), 4);
    var start = check_date($('#employer_start'));
    var end = check_date($('#employer_end'));
    var description = check_input_length($('#employer_description'), 29);
    if($('#employer_is_current').is(':checked')){
        if(name && start && description){
            $('#loading_modal').modal({backdrop: 'static', keyboard: false});
            var data = {'name':$('#employer_name').val(), 'is_current':true,
                'start':$('#employer_start').val(), 'end':$('#employer_end').val(), 'description':$('#employer_description').val()};
            $.ajax({
                type: 'POST',
                url: '/add_employer_recruiting',
                data: data,
                success: function (response) {
                    if (response['status'] === 'success'){
                        $('#employers_confirm').append('<li class="employer_attended" id="'+ response['id'].toString() +'">' + $("#employer_name").val() + '<button style="margin-left: 15px" type="button" class="close remove_employer" >\n' +
                        '                                  <span aria-hidden="true" style="color: red">×</span>\n' +
                        '                                </button></li>')
                        $('#employer_name').val('');
                        $('#employer_description').val('');
                        $('#employer_is_current').removeAttr('checked')
                        $('#add_employer').modal('hide');
                        $('#loading_modal').modal('toggle')
                        ensure_minimums(document.getElementById('confirm_data_btn'))
                    }else{
                        $('#employer_name').val('');
                        $('#employer_description').val('');
                        $('#employer_is_current').removeAttr('checked');
                        $('#add_employer').modal('hide');
                        $('#loading_modal').modal('toggle')
                    }
                },
                error: function () {
                    error_popup()
                }
            })

        }
    }else{
        if(name && start && description && end){
            $('#loading_modal').modal({backdrop: 'static', keyboard: false});
            var data = {'name':$('#employer_name').val(), 'is_current':false,
                'start':$('#employer_start').val(), 'end':$('#employer_end').val(), 'description':$('#employer_description').val()};
           $.ajax({
                type: 'POST',
                url: '/add_employer_recruiting',
                data: data,
                success: function (response) {
                    if (response['status'] === 'success'){
                        $('#employers_confirm').append('<li class="employer_attended" id="'+ response['id'].toString() +'">' + $("#employer_name").val() + '<button style="margin-left: 15px" type="button" class="close remove_employer" >\n' +
                        '                                  <span aria-hidden="true" style="color: red">×</span>\n' +
                        '                                </button></li>')
                        $('#employer_name').val('');
                        $('#employer_description').val('');
                        $('#employer_is_current').removeAttr('checked')
                        $('#add_employer').modal('hide');
                        $('#loading_modal').modal('toggle')
                        ensure_minimums(document.getElementById('confirm_data_btn'))
                    }else{
                        $('#employer_name').val('');
                        $('#employer_description').val('');
                        $('#employer_is_current').removeAttr('checked');
                        $('#add_employer').modal('hide');
                        $('#loading_modal').modal('toggle')
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }

});

$(document).on('click', '.remove_institution', function () {
    var element = $(this.parentElement);
    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
    $.ajax({
        type: 'POST',
        url: '/remove_institution',
        data: {'id': $(this.parentElement).attr('id')},
        success: function () {
            element.remove();
            $('#loading_modal').modal('hide');
            ensure_minimums(document.getElementById('confirm_data_btn'))
        },
        error: function () {
            error_popup()
        }
    })
});

$(document).on('click', '.remove_employer', function () {
    var element = $(this.parentElement);
    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
    $.ajax({
        type: 'POST',
        url: '/remove_employer',
        data: {'id': $(this.parentElement).attr('id')},
        success: function () {
            element.remove();
            $('#loading_modal').modal('hide');
            ensure_minimums(document.getElementById('confirm_data_btn'))
        },
        error: function () {
            error_popup()
        }
    });
});

$(document).on('click', '#confirm_data_btn', function () {
   var b = ensure_minimums(this);
    if (b) {
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
            url: '/recruiting_step_change/2',
            type: 'POST',
            success: function (response) {
                if (response['status'] === 'success') {
                    $('#recruiting_enroll_confirm').modal('hide');
                    $('#recruiting_enroll_questions').modal({backdrop: 'static', keyboard: false})
                    $('#loading_modal').modal('hide');
                }
            },
            error: function () {
                error_popup()
            }
        })
    }
    });

$(document).on('blur', '.register-industry', function () {
    check_industries_selected($(this), 3)
});

$(document).on('click', '.remove_city', function () {
    $(this.parentElement).remove()
});

$(document).on('click', '#submit_more_questions', function () {
    var cities = check_cities();
    var industries = check_industries(3);
    var industries_list = $('#industry').val()
    if($('#laid_off').val().length > 0){
        date = check_date($('#laid_off'))
    }else{
        date = true
    }

    var cities_list = []
    $('span.city_for_recruiting_text').each(function () {
        cities_list.push($(this).text())
    })
    if($('#l_specific').is(':checked')){
        if(industries && date){
            $('.confetti_wrapper').css({'display':'block'})
            $('#loading_modal').modal({backdrop: 'static', keyboard: false});
            var data = {'laid_off':$('#laid_off').val(), 'experience': $('#experience').val(),
            'industries':industries_list, 'cities':cities_list, 'l_specific':false, 'additional':$('#more_info').val()};
            $.ajax({
                type: 'POST',
                url: '/complete_recruiting_registration',
                data: data,
                success: function (response) {
                    if(response['status'] ==='success'){
                        $('#recruiting_enroll_questions').modal('hide');
                        $('#loading_modal').modal('hide');
                        window.location.reload()
                    }else{
                        custom_error_popup(response['message'])
                    }

                },
                error: function () {
                    error_popup()
                }
            });
        }
    }else{
        if(industries && cities && date){
            $('.confetti_wrapper').css({'display':'block'})
            $('#loading_modal').modal({backdrop: 'static', keyboard: false});
            var data = {'laid_off':$('#laid_off').val(), 'experience': $('#experience').val(),
            'industries':industries_list, 'cities':cities_list, 'l_specific':true, 'additional':$('#more_info').val()};
            $.ajax({
                type: 'POST',
                url: '/complete_recruiting_registration',
                data: data,
                success: function (response) {
                   if(response['status'] ==='success'){
                        $('#recruiting_enroll_questions').modal('hide');
                        $('#loading_modal').modal('hide');
                        window.location.reload()
                    }else{
                        custom_error_popup(response['message'])
                    }
                },
                error: function () {
                    error_popup()
                }
            });
        }
    }
});

$(document).on('DOMSubtreeModified', '#accepted_cities', function () {
    check_cities()
});

$(document).on('click', '#edit_recruiting_profile', function () {
    $('#edit_profile_modal').modal({backdrop: 'static', keyboard: false})
});

$(document).on('click', '#edit_more', function () {
    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
    $.get('/recruiting_more_info', {}, function (response) {
        $('#questions_header').text('Edit your preferences')
        $('#more_info').val(response['bio']);
        $('#laid_off').val(response['laid_off']);
        $('#experience').val(response['experience']);
        if(response['l_specific'] === 'false'){
            $('#l_specific').attr('checked', 'checked')
            $('#location_specific_false').css({'display':'block'})
            $('#location_specific_true').css({'display':'none'})
        }else{
            var arr = [];
            $('#l_specific').removeAttr('checked')
            $('#location_specific_false').css({'display':'none'})
            $('#location_specific_true').css({'display':'block'})
            $('span.city_for_recruiting_text').each(function () {
                arr.push($(this).text())
            });
            for(var i=0;i<response['cities'].length;i++){
                if (arr.includes(response['cities'][i])){
                }else{
                    $('#accepted_cities').append('<li class="city_for_recruiting"><span class="city_for_recruiting_text">' + response['cities'][i].toString() + '</span><button style="margin-left: 15px" type="button" class="close remove_city"><span aria-hidden="true" style="color: red">×</span></button></li>')
                }
            }
            check_cities()
        }
        $('#industry').selectpicker('val', response['industries'])

        $('#loading_modal').modal('toggle');
        $('#recruiting_enroll_questions').modal({backdrop: 'static', keyboard: false});
        if($('#questions_header_cont').children().length === 1){
            $('#questions_header_cont').append('<button type="button" class="close close-editing" data-dismiss="modal" aria-label="Close">\n' +
            '                          <span aria-hidden="true" style="color: red">&times;</span>\n' +
            '                        </button>')
        }

        $('#edit_profile_modal').modal('toggle')
    })
});

$(document).on('click', '#close', function () {
    $('#recruiting_enroll_confirm').css({'display':'none'})
    $('#recruiting_enroll_confirm').modal('hide')
    setTimeout(window.location.reload(), 1000)
})

$(document).on('click', '#update_e_i', function () {
    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
    $.get('/enroll_resume_upload', {}, function (response) {
        var i_arr = []
        $('.just_name_i').each(function () {
            i_arr.push($(this).text())
        })
        var e_arr = []
        $('.just_name_e').each(function () {
            e_arr.push($(this).text())
        });
        for (i = 0; i < response['institutions'].length; i++){
            if (i_arr.includes(response['institutions'][i]['name'].toString())){

            }else{
                $('#institutions_confirm').append('<li class="institution_attended" id="' + response['institutions'][i]['id'].toString() +'"><span class="just_name_i">' + response['institutions'][i]['name'].toString() + '</span> <button style="margin-left: 15px" type="button" class="close remove_institution">\n' +
                '                                  <span aria-hidden="true" style="color: red">&times;</span>\n' +
                '                                </button></li>');
            }
        }
        for (i = 0; i < response['employers'].length; i++){
            if (e_arr.includes(response['employers'][i]['name'].toString())){

            }else{
                $('#employers_confirm').append('<li class="employer_attended" id="' +  response['employers'][i]['id'].toString() +'"><span class="just_name_e">' + response['employers'][i]['name'].toString() + '</span><button style="margin-left: 15px" type="button" class="close remove_employer">\n' +
                '                                  <span aria-hidden="true" style="color: red">&times;</span>\n' +
                '                                </button></li>');
            }
        }
        $('#loading_modal').modal('hide');
        $('#recruiting_enroll_confirm').modal({backdrop: 'static', keyboard: false});
        if($('#things_header').children().length === 1){
            $('#things_header').append('<button type="button" class="close close-editing" data-dismiss="modal" aria-label="Close">\n' +
            '                          <span aria-hidden="true" style="color: red">&times;</span>\n' +
            '                        </button>')
        }
        $('#edit_profile_modal').modal('toggle')
    $('#recruiting_enroll_confirm_header').text('Edit Institutions & Employers');
    $('#confirm_data_btn').prop('id', 'close');
})})

$(document).on('click', '.close-editing', function () {
    $(this.parentElement.parentElement.parentElement.parentElement).modal('hide')
    $('#edit_profile_modal').modal('show')

})

$(document).on('click', '#upload_new_resume', function () {
    $('#edit_profile_modal').modal('toggle');
    $('#edit_resume').modal({backdrop: 'static', keyboard: false})
})

$(document).on('click','#edit_resume_submit', function() {
    $('#edit_resume').modal('toggle');
    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
    var fd = new FormData();
    var files = $('#resume')[0].files[0];
    fd.append('resume', files);
    $.ajax({
                url: '/auth/resume',
                type: 'post',
                data: fd,
                contentType: false,
                processData: false,
                success: function(response){
                    if (response['status'] === 'success'){
                        $('#loading_modal').css({'display':'none'})
                        window.location.reload()
                    }else{
                        custom_error_popup(response['message'])
                    }
                },
                error: function () {
                    error_popup()
                }
            });
})

$(document).ready(function () {
    var autocomplete_institution;
    var autocomplete_recruiting;
    autocomplete_institution = new google.maps.places.Autocomplete((document.getElementById('institution_city')), {
        types: ['(cities)'],
    });
    autocomplete_recruiting = new google.maps.places.Autocomplete((document.getElementById('city_relocations')), {
        types: ['(cities)'],
    });

    google.maps.event.addListener(autocomplete_institution, 'place_changed', function () {
        var near_place = autocomplete_institution.getPlace();
    });
    google.maps.event.addListener(autocomplete_recruiting, 'place_changed', function () {
        var near_place = autocomplete_recruiting.getPlace();
        var arr = [];
        $('span.city_for_recruiting_text').each(function () {
            arr.push($(this).text())
        });
        if (arr.includes(near_place['formatted_address'].toString())){
            $('#city_relocations').val('')
        }else{
            $('#accepted_cities').append('<li class="city_for_recruiting"><span class="city_for_recruiting_text">' + near_place['formatted_address'].toString() + '</span><button style="margin-left: 15px" type="button" class="close remove_city"><span aria-hidden="true" style="color: red">×</span></button></li>')
            $('#city_relocations').val('')
        }
        check_cities()
    });
});

$('#job_found').on('hidden.bs.modal', function (e) {
  $('.confetti_wrapper').toggle()
});

$('#job_found').on('shown.bs.modal', function (e) {
  $('.confetti_wrapper').toggle()
});

function open_add_institution() {
    $('#add_institution').modal('show');
    $('#add_institution').css({'display':'block'})
}


function open_add_employers() {
    $('#add_employer').modal('show');
    $('#add_employer').css({'display':'block'})
}

function clear_errors(element) {
        element.removeClass('incorrect');
        element.prev().removeClass('incorrect_text');
        if (element.next().hasClass('val')){
            element.next().remove()
        }
}

function check_input_length(element, num) {
    if (element.val().length > num){
        element.removeClass('incorrect');
        element.prev().removeClass('incorrect_text');
        return true
    }else{
        element.addClass('incorrect');
        element.prev().addClass('incorrect_text');
        if (element.next().hasClass('val')){
        }else{
            element.after('<div class="val"><div class="row"><div class="col-sm-12 validator" id="type-l">Must be at least ' + (num + 1) + ' characters</div></div></div>')
        }
        return false
    }
}

function ensure_minimums(element) {
    var i = $('#institutions_confirm').children().length === 0;
    var e = $('#employers_confirm').children().length === 0;
    if (i || e){
        $(element).addClass('lo-tov');
        if (element.previousElementSibling !== null && $(element).has('val')){}else{
            $(element).before('<div class="val resume_parsed">You must have at least one institution and employer listed in order to proceed.</div>')
        }
        return false
    }else{
        $(element).removeClass('lo-tov');
        if (element.previousElementSibling !== null && $(element).has('val')){
            $(element.previousElementSibling).remove()
        }
        return true
    }

}

function check_industries(num) {
    if ($('li.selected').length > num || $('li.selected').length === 0){
        $('.register-industry').each(function () {
            $(this).addClass('incorrect');
        })
        $('.filter-option').addClass('incorrect_text')
        $('.industry-label').addClass('incorrect_text')
        return false
    }else{
        $('.register-industry').each(function () {
            $(this).removeClass('incorrect');
        })
        $('.filter-option').removeClass('incorrect_text')
        $('.industry-label').removeClass('incorrect_text')
        return true
    }
}

function check_cities() {
    if ($('li.city_for_recruiting').length > 3 || $('li.city_for_recruiting').length === 0){
        $('#city_relocations').addClass('incorrect');
        $('.city_relocations_label').addClass('incorrect_text')
        return false
    }else{
        $('#city_relocations').removeClass('incorrect');
        $('.city_relocations_label').removeClass('incorrect_text')
        return true
    }
}

function toggle_l() {
  $('#location_specific_true').toggle()
  $('#location_specific_false').toggle()
}

function check_date(element) {
    if (!!moment(element.val(), "MM/DD/YYYY", true).isValid()){
        element.removeClass('incorrect');
        element.prev().removeClass('incorrect_text');
        return true
    }else{
        element.addClass('incorrect');
        element.prev().addClass('incorrect_text');
        if (element.next().hasClass('val')){
        }else{
            element.after('<div class="val"><div class="row"><div class="col-sm-12 validator" id="type-l">Must be a date</div></div></div>')
        }
        return false
    }
}