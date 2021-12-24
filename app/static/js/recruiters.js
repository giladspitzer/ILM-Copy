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
        if (element.next().hasClass('val')){
            element.next().remove()
        }
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

function check_industry(element){
    if(element.val() === '0'){
        $('button[data-id=industry]').addClass('incorrect');
        $('.industry-label').addClass('incorrect_text');
        if (element.next().hasClass('val')){
        }else{
            element.after('<div class="val"><div class="row"><div class="col-sm-12 validator" id="type-l">Must select an industry</div></div></div>')
        }
        return false
    }else{
        $('button[data-id=industry]').removeClass('incorrect');
        $('.industry-label').removeClass('incorrect_text');
        if (element.next().hasClass('val')){
            element.next().remove()
        }
        return true
    }
}

function change_search_status(element, candidate, direction) {
        function function3(){
            var status = document.getElementById('search_status');
            if (direction == 0){
                custom_success_popup('Search settings saved. Candidates will no longer be able to reach out.')
                element.style.display = 'none';
                element.nextElementSibling.style.display = 'inline';
                status.innerText = 'False'
            }else if (direction == 1){
                custom_success_popup('Search settings saved. Candidates will now be able to reach out.')
                element.style.display = 'none';
                element.previousElementSibling.style.display = 'inline';
                status.innerText = 'True'
            }

        }
        if(confirm('Are you sure you would like to edit ' +
            'the visibility of this search?')){
            $.ajax({
                type: 'POST',
                url: '/p/change_search_visibility',
                data: { 'i': candidate, 'd': direction},
                success: function () {
                    setTimeout(function3(), 1000);
                },
                error: function () {
                    error_popup()
                }
            });
        }
    }

function drop(id, option) {
            if (option === 'message'){
                if($('#message-post_' + id).css('display') === 'block'){
                $('#message-post_' + id).css({'display':'none'});
                $('#message_indicator_' + id).addClass('glyphicon-chevron-down')
                $('#message_indicator_' + id).removeClass('glyphicon-chevron-up')
                $('#message_indicator_' + id).css({'color':'#4D80E4'})

            }else{
                $('#message-post_' + id).css({'display':'block'});
                $('#message_indicator_' + id).addClass('glyphicon-chevron-up')
                $('#message_indicator_' + id).removeClass('glyphicon-chevron-down')
                $('#message_indicator_' + id).css({'color':'orange'})
            }
                if($('#message_container_' +id).css('height') === '200px'){
                    $('#message_container_' +id).css({'height':'150px'})
                }else{
                    $('#message_container_' +id).css({'height':'200px'})
                }
            }else if (option === 'note'){
                if($('#note-post_' + id).css('display') === 'block'){
                $('#note-post_' + id).css({'display':'none'});
                $('#note_indicator_' + id).addClass('glyphicon-chevron-down')
                $('#note_indicator_' + id).removeClass('glyphicon-chevron-up')
                $('#note_indicator_' + id).css({'color':'#4D80E4'})

            }else{
                $('#note-post_' + id).css({'display':'block'});
                $('#note_indicator_' + id).addClass('glyphicon-chevron-up')
                $('#note_indicator_' + id).removeClass('glyphicon-chevron-down')
                $('#note_indicator_' + id).css({'color':'orange'})
            }
                if($('#notes_container_' +id).css('height') === '200px'){
                    $('#notes_container_' +id).css({'height':'150px'})
                }else{
                    $('#notes_container_' +id).css({'height':'200'})
                }
            }
        }

$(function() {
            $( "#candidates, #considering, #strongly, #removed" ).sortable({
               connectWith: "#candidates, #considering, #strongly",
                handle: '.handle',
            });
         });

$(document).ready(function () {
if ($.trim($("textarea").val()) != "") {
    alert($("textarea").val());
}
});

function jut_out(candidate) {
    var arrow = document.getElementById('glyph-'+ candidate);
    var side = document.getElementById('user-viewer');
    var html = document.getElementById(candidate);
    var blank_html = document.getElementById('user-viewer-safe');

    if (arrow.classList.contains('active-candidate')){
        function close() {
            arrow.classList.remove('active-candidate');
            arrow.parentElement.parentElement.children[2].innerHTML = side.innerHTML
            side.innerHTML = blank_html.innerHTML;
            side.classList = []
        }
        if ($('#notes_'+candidate).val().length > 5){
            var response = confirm("Your notes will be deleted if you leave this candidate's profile. Would you like to leave?")
            if (response){
                close()
            }
        }else{
            close()
        }
    }else{
        function open() {
            elements = document.getElementsByClassName('active-candidate');
            arr = []
            if (elements.length === 0){
                blank_html.innerHTML = side.innerHTML;
            }else{
                for (i = 0; i < elements.length; i++) {
                    arr.push(elements[i])
                    elements[i].classList.remove('active-candidate');
                }
                for (i = 0; i < arr.length; i++) {
                    arr[i].parentElement.nextElementSibling.innerHTML = side.innerHTML
                }

            }

            side.innerHTML = html.innerHTML;
            html.innerHTML = '<div></div>';
            side.classList.add('viewer');
            arrow.classList.add('active-candidate');

        }
        if ($('#general_notes').val().length > 5){
            var response = confirm("Your drafted note will be deleted if you open a candidate's profile. Would you like to proceed?")
            if (response){
                open();
                $('#main_btn').attr('disabled', '')
            }
        }else{
            open()
        }
    }

}

$(document).ready(function () {
    var autocomplete;
    autocomplete = new google.maps.places.Autocomplete((document.getElementById('city')), {
        types: ['(cities)'],
    });

    google.maps.event.addListener(autocomplete, 'place_changed', function () {
        var near_place = autocomplete.getPlace();
    });
});

$(document).on('click', '#submit_new_search_r', function () {
    var title = $('#search_title');
    var city = $('#city');
    var industry = $('#industry');
    var description = $('#search_description')
    var title_check = check_length_special(title, 0, 80, 'Title must be between 1 & 80 characters')
    var city_check = check_length_special(city, 0, 80, 'Please enter a valid city')
    var d_check = check_length_special(description, -1, 500, 'Description must be between 0 & 500 characters')
    var industry_check = check_industry(industry);
    var public_val = $('#public').is(':checked');
    var remote = $('#remote').is(':checked')
    if(remote){
        if (title_check && industry_check && d_check){
            $('#loading_modal').modal({backdrop: 'static', keyboard: false});
            var data = {'title':title.val(), 'city':city.val(), 'industry':industry.val(), 'public': public_val,
                'description':description.val(), 'remote':remote}
            $.ajax({
                type: 'POST',
                url: '/p/add_recruiter_search',
                data: data,
                success: function (response) {
                    if (response['status'] === 'success') {
                        $('#add_talent_search_modal').modal('hide')
                        $('#loading_modal').modal('hide');
                        window.location.pathname = '/p/saved_search/' + response['id'].toString()
                    } else {
                        custom_error_popup(response['message'])
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }else{
        if (title_check && industry_check && city_check && d_check){
            $('#loading_modal').modal({backdrop: 'static', keyboard: false});
            var data = {'title':title.val(), 'city':city.val(), 'industry':industry.val(), 'public': public_val,
                'description':description.val(), 'remote':remote}
            $.ajax({
                type: 'POST',
                url: '/p/add_recruiter_search',
                data: data,
                success: function (response) {
                    if (response['status'] === 'success') {
                        $('#add_talent_search_modal').modal('hide')
                        $('#loading_modal').modal('hide');
                        window.location.pathname = '/p/saved_search/' + response['id'].toString()
                    } else {
                        custom_error_popup(response['message'])
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }
})

$(document).on('click', '.inner_text', function () {

    if($(this.nextElementSibling).css('display') === 'none'){
        $(this.nextElementSibling).css({'display':'inline-block'})
    }else if ($(this.nextElementSibling).css('display') === 'inline-block'){
        $(this.nextElementSibling).css({'display':'none'})
    }
    if($(this.nextElementSibling.nextElementSibling).css('display') === 'none'){
        $(this.nextElementSibling.nextElementSibling).css({'display':'inline-block'})
    }else if ($(this.nextElementSibling.nextElementSibling).css('display') === 'inline-block'){
        $(this.nextElementSibling.nextElementSibling).css({'display':'none'})
    }

    $(this.parentElement.nextElementSibling).toggle()
    if ($(this).text().includes('+')){
        $(this).text($(this).text().replace('+', '-'))
    }else{
            $(this).text($(this).text().replace('-', '+'))
    }
    if($(this).attr('extra-id') !== null){
        $('#message_container_' + $(this).attr('extra-id').toString()).animate({ scrollTop: $('#message_container_' + $(this).attr('extra-id').toString()).prop("scrollHeight")}, 1000)
    }


})

$(document).on('click', '.candidate-card', function () {
    var id = $(this).attr('candidate-id')
    $($(this).children()[1]).before('<div class="loadingio-spinner-spinner-46etahine7c"><div class="ldio-unxkrae1eg8">\n' +
        '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '</div></div>')
    var card = $(this)
    card.addClass('loading-bg')
    var element = $($(this).children()[1])
    $.ajax({
        type: 'GET',
        url: '/p/get_candidate_info',
        data: {'a': id},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#candidate_body').html(response['html'])
                element.remove()
                $('#candidate_modal_viewer').modal({backdrop: 'static', keyboard: false})
                card.removeClass('loading-bg')
                make_moments()
                update_notification_count()
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
})

$(document).on('click', '.applicant-card', function () {
    var id = $(this).attr('applicant-id')
        $($(this).children()[1]).before('<div class="loadingio-spinner-spinner-46etahine7c"><div class="ldio-unxkrae1eg8">\n' +
        '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '</div></div>')
    var card = $(this)
    card.addClass('loading-bg')
    var element = $($(this).children()[1])
    $.ajax({
        type: 'GET',
        url: '/p/get_applicant_info',
        data: {'a': id},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#applicant_body').html(response['html'])
                element.remove()
                card.removeClass('loading-bg')
                $('#applicant_modal_viewer').modal({backdrop: 'static', keyboard: false})
                make_moments()
                update_notification_count()
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
})

// Add general search note
$(document).on('click', '#submit_search_note', function () {
    if(check_length_special($('#general_notes'), 0, 500, 'Must be between 1 and 500 characters' )){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
            type: 'POST',
            url: "/p/post_search_note",
            data: { 'q': $('#general_notes').val(), 'id': $('#general_notes').attr('search-id')},
            success: function (response) {
                if(response['status'] === 'success'){
                    if($($('#main_notes_container').children()[0]).hasClass('no-posts')){
                        $($('#main_notes_container').children()[0]).remove()
                    }
                    $('#main_notes_container').prepend(response['html'])
                    $('#general_notes').val('')
                    $('#general_notes_counter').html(parseInt($('#general_notes_counter').text()) + 1)
                    make_moments()
                    $('#loading_modal').modal('hide')
                }else{
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                error_popup()
            }
        }
        );
    }
})

$(document).on('click', '#submit_job_posting_note', function () {
    if(check_length_special($('#general_notes'), 0, 500, 'Must be between 1 and 500 characters' )){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
            type: 'POST',
            url: "/p/post_job_posting_note",
            data: { 'q': $('#general_notes').val(), 'id': $('#general_notes').attr('job-id')},
            success: function (response) {
                if(response['status'] === 'success'){
                    if($($('#main_notes_container').children()[0]).hasClass('no-posts')){
                        $($('#main_notes_container').children()[0]).remove()
                    }
                    $('#main_notes_container').prepend(response['html'])
                    $('#general_notes').val('')
                    $('#general_notes_counter').html(parseInt($('#general_notes_counter').text()) + 1)
                    make_moments()
                    $('#loading_modal').modal('hide');
                }else{
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                error_popup()
            }
        }
        );
    }
})

// Add specific candidate note
$(document).on('click', '.note-submit-candidate', function () {
    var id = $(this).attr('candidate-id')
    if(check_length_special($('#notes_' + id.toString()), 0, 500, 'Must be between 1 and 500 characters' )) {
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        var note = $('#notes_' + id.toString()).val()
        $.ajax({
            type: 'POST',
            url: '/p/post_candidate_note',
            data: {'q': note, 'a': id},
            success: function (response) {
                if(response['status'] === 'success'){
                    if($($('.notes_container_' + id.toString()).children()[0]).hasClass('no-posts')) {
                        $($('.notes_container_' + id.toString()).children()[0]).remove()
                    }
                    $('#notes_' + id.toString()).val('')
                    $('.notes_container_' + id.toString()).prepend(response['html'])
                    $('#notes_counter_' + id.toString()).text(parseInt($('#notes_counter_' + id.toString()).text()) + 1)
                    make_moments()
                    $('#loading_modal').modal('hide');
                }else{
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                error_popup()
            }

        });
    }
});

$(document).on('click', '#add_search', function () {
    $('#add_talent_search_modal').modal({backdrop: 'static', keyboard: false})
})

$(document).on('click', '.recruiter_update', function () {
    var id = $(this).attr('recruiter-id')
    var u = check_length_special($('#username_' + id), 0, 40, 'Must be between 0 & 40 characters')
    var n = check_length_special($('#name_' + id), 0, 80, 'Please enter a name')
    var t = check_length_special($('#position_title_' + id), 0, 80, 'Please enter a title')
    var email = document.getElementById('email_' + id)
    var e = check_email(email)
    var username = document.getElementById('username_' + id)
    if(u && n && t && e) {
        $('#loading_modal').modal({backdrop: 'static', keyboard: false})
        var content = {'u': username.value, 'e': email.value};
        $.ajax({
        type: 'POST',
        url: "/auth/verify_unique/" + id,
        data: content,
        success: function (data) {
            if (data['e'] && data['u']){
                var recruiter = {
                'username': $('#username_' +id).val(),
                'email': $('#email_' +id).val(),
                'experience': $('#experience_' +id).val(),
                'title': $('#position_title_' +id).val(),
                'authority': $('#authority_' +id).val(),
                'id': id,
                'name': $('#name_' +id).val()
            };
                $.ajax({
                type: 'POST',
                url: "/p/update_recruiter",
                data: recruiter,
                success: function(response) {
                    if(response['status'] === 'success'){
                        document.location.reload()
                    }else{
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
            }else{
                $('#loading_modal').modal('hide')
                if (!data['e']){
                    $('label[for="email_' + id.toString() +'"]').addClass('non_unique_text');
                    $(email).addClass('non-unique');
                    if (email.previousElementSibling !== null) {
                        if (email.previousElementSibling.id !== 'email_not_unique') {
                            $(email).before('<div class="val" id="email_not_unique"><div class="row"><div class="col-sm-12 validator" id="type-unique">Email Already in Use</div></div></div>');
                        }
                    }else{
                    $(email).before('<div class="val" id="email_not_unique"><div class="row"><div class="col-sm-12 validator" id="type-unique">Email Already in Use</div></div></div>');
                }}
                if (!data['u']){
                    $('label[for="username_' + id.toString() +'"]').addClass('non_unique_text');
                    $(username).addClass('non-unique');
                    if (username.previousElementSibling !== null) {
                        if (username.previousElementSibling.id !== 'username_not_unique') {
                            $(username).before('<div class="val" id="username_not_unique"><div class="row"><div class="col-sm-12 validator" id="type-unique">Username Already in Use</div></div></div>');
                        }
                    }else{
                        $(username).before('<div class="val" id="username_not_unique"><div class="row"><div class="col-sm-12 validator" id="type-unique">Username Already in Use</div></div></div>');
                    }
                }
            }
        },
        error: function () {
            error_popup()
        }
    });
    }
})

$(document).on('click', '.add_recruiter_btn', function () {
    var n = check_length_special($('#name_add'), 0, 40, 'Must be between 0 & 40 characters')
    var t = check_length_special($('#position_title_add'), 0, 80, 'Please enter a title')
    var email = document.getElementById('email_add')
    var e = check_email(email)
    if(n && t && e) {
        $('#loading_modal').modal({backdrop: 'static', keyboard: false})
        var content = {'u': 'giladspitzer', 'e': email.value};
        $.ajax({
            type: 'POST',
            url: "/auth/verify_unique",
            data: content,
            success: function (data) {
                if (data['e']){
                    var recruiter = {
                    'email': $('#email_add').val(),
                    'experience': $('#experience_add').val(),
                    'title': $('#position_title_add').val(),
                    'authority': $('#authority_add').val(),
                    'name': $('#name_add').val()
                };
                    $.ajax({
                        type: 'POST',
                        url: "/p/add_recruiter",
                        data: recruiter,
                        success: function(response) {
                            if(response['status']==='success'){
                                document.location.reload()
                            }else{
                                error_popup()
                            }
                        },
                        error: function () {
                            error_popup()
                        }
                    })
            }else{
                $('#loading_modal').modal('hide')
                if (!data['e']){
                    $('label[for="email_' + id.toString() +'"]').addClass('non_unique_text');
                    $(email).addClass('non-unique');
                    if (email.previousElementSibling !== null) {
                        if (email.previousElementSibling.id !== 'email_not_unique') {
                            $(email).before('<div class="val" id="email_not_unique"><div class="row"><div class="col-sm-12 validator" id="type-unique">Email Already in Use</div></div></div>');
                        }
                    }else{
                    $(email).before('<div class="val" id="email_not_unique"><div class="row"><div class="col-sm-12 validator" id="type-unique">Email Already in Use</div></div></div>');
                }}
            }
        },
        error: function () {
            error_popup()
        }
    });
    }
})

$(document).on('click', '#add_job', function () {
    $('#job_type_selection').modal({backdrop: 'static', keyboard: false})
})

$(document).on('click', '#quick_apply', function () {
    $('#job_type_selection').modal('hide')
    $('#quick_apply_modal_1').modal({backdrop: 'static', keyboard: false})
    // custom_error_popup('This feature is not yet available. Check back soon!')
})

$(document).on('click', '#external_apply', function () {
    $('#job_type_selection').modal('hide')
    $('#external_apply_modal').modal({backdrop: 'static', keyboard: false})
})

$(document).on('hidden.bs.modal', '#external_apply_modal', function () {
  $('#job_type_selection').modal({backdrop: 'static', keyboard: false})
})

$(document).on('hidden.bs.modal', '#quick_apply_modal_1', function () {
  $('#job_type_selection').modal({backdrop: 'static', keyboard: false})
})

$(document).on('hidden.bs.modal', '#quick_apply_modal_2', function () {
  $('#job_type_selection').modal({backdrop: 'static', keyboard: false})
})


$(document).on('shown.bs.modal', '#quick_apply_modal_2', function () {
  $('#job_type_selection').modal('hide')
})

$(document).on('shown.bs.modal', '#quick_apply_modal_1', function () {
  $('#job_type_selection').modal('hide')
})


$(document).on('shown.bs.modal', '#removed_candidates_modal', function () {
  $('#talent_search_edit_modal').modal('hide')
})

$(document).on('hidden.bs.modal', '#removed_candidates_modal', function () {
  $('#talent_search_edit_modal').modal({backdrop: 'static', keyboard: false})
})


$(document).on('change blur focus keyup keydown click', '#job_link', function () {
    if(!isURL($(this).val())){
        if (!$(this).next().hasClass('val')){
            $('#job_link_label').addClass('incorrect-text')
            $(this).addClass('incorrect')
            $(this).after('<div class="val"><div class="row"><div class="col-sm-12 validator" id="type-l">Must be a valid URL</div></div></div>')
        }
    }else{
        if ($(this).next().hasClass('val')){
            $('#job_link_label').removeClass('incorrect-text')
            $(this).removeClass('incorrect')
            $(this).next().remove()
        }
    }
})

// Google Maps Cities API for City of Job Saved Search
$(document).ready(function () {
var city_autocomplete_post_job_external;
    city_autocomplete_post_job_external = new google.maps.places.Autocomplete((document.getElementById('job_city_external')), {
    types: ['(cities)'],
    });

    google.maps.event.addListener(city_autocomplete_post_job_external, 'place_changed', function () {
        var near_place = city_autocomplete_post_job_external.getPlace();
        });
});


$(document).ready(function () {
var city_autocomplete_post_job_external_edit;
    city_autocomplete_post_job_external_edit = new google.maps.places.Autocomplete((document.getElementById('job_city_edit_external')), {
    types: ['(cities)'],
    });

    google.maps.event.addListener(city_autocomplete_post_job_external_edit, 'place_changed', function () {
        var near_place = city_autocomplete_post_job_external_edit.getPlace();
        });
});


$(document).ready(function () {
var city_autocomplete_post_job_quick;
    city_autocomplete_post_job_quick = new google.maps.places.Autocomplete((document.getElementById('job_city_quick')), {
    types: ['(cities)'],
    });

    google.maps.event.addListener(city_autocomplete_post_job_quick, 'place_changed', function () {
        var near_place = city_autocomplete_post_job_external_edit.getPlace();
        });
});

function check_industries_selected(element, num){
    if(element.val().length > num || element.val().length == 0){
        $('.job-industries').each(function () {
            $(this).addClass('incorrect');
        })
        $('.filter-option').addClass('incorrect_text')
        $('.industry-label').addClass('incorrect_text')
        if(!element.next().hasClass('val')){
            element.after('<div class="val"><div class="row"><div class="col-sm-12 validator" id="type-l">Must select an industry</div></div></div>')
        }
        return false
    }else{
        $('.job-industries').each(function () {
            $(this).removeClass('incorrect');
        })
        $('.filter-option').removeClass('incorrect_text')
        $('.industry-label').removeClass('incorrect_text')
        if(element.next().hasClass('val')){
            element.next().remove()
        }
        return true
    }
}

$(document).on('click', '.edit_job_toggle', function () {
    $('#external_apply_edit_modal').modal({backdrop: 'static', keyboard: false})
})

$(document).on('click', '.edit_search_toggle', function () {
    var id = $(this).attr('search-id')
    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
    $.ajax({
      type: 'GET',
      url: '/p/get_search_info',
      data: {'a':id.toString()},
      success: function (response) {
          if(response['status'] === 'success'){
                $('#search_title_edit').val(response['title'])
                $('#search_description_edit').val(response['description'])
                $('#industry_edit').selectpicker('val', response['industry'])
                if(response['l_specific'] === 0){
                    if(!$('#remote_edit').is(':checked')){
                        $('#remote_edit').click()
                    }
                }else{
                    if($('#remote_edit').is(':checked')){
                        $('#remote_edit').click()
                    }
                    $('#city_edit').val(response['city'])
                    $('#city_edit').next().addClass('blurred')
                }
                if(response['public'] === 1){
                    if(!$('#public_edit').is(':checked')){
                        $('#public_edit').click()
                    }
                }else{
                    if($('#public_edit').is(':checked')){
                        $('#public_edit').click()
                    }
                }
                $('#removed_content').html( response['removed'])
              $('#talent_search_edit_modal').modal({backdrop: 'static', keyboard: false})
              $('#loading_modal').modal('hide')
          }else{
              custom_error_popup(response['message'])
          }
      },
  })
})

$(document).on('click', '.edit_job_toggle_quick', function () {
    $('#quick_apply_modal_edit').modal({backdrop: 'static', keyboard: false})
})

$(document).on('click change blur focus ', '#job_industries', function () {
    check_industries_selected($('#job_industries'), 3)
})

$(document).on('click change blur focus ', '#job_industries_quick', function () {
    check_industries_selected($('#job_industries_quick'), 3)
})

$(document).on('click', '#submit_new_external_job', function () {
    var t = check_length_special($('#job_title'), 0, 200, 'Must be between 0 & 200 characters')
    var c = check_length_special($('#job_company_name'), 0, 200, 'Must be between 0 & 200 characters')
    var l = check_length_special($('#job_link'), 0, 400, 'Must be a link') && isURL($('#job_link').val())
    var d = check_length_special($('#job_description'), 25, 1000, 'Must be between 25 & 1000 characters')
    var i = check_industries_selected($('#job_industries'), 3)
    var city = check_length_special($('#job_city_external'), 0, 50, 'Must be a valid city')
    var remote = $('#job_remote').is(':checked');
    var data = {'title':$('#job_title').val(), 'company': $('#job_company_name').val(), 'link': $('#job_link').val(),
                        'description':$('#job_description').val(), 'industries':$('#job_industries').val(), 'city': $('#job_city_external').val(),
                        'remote':$('#job_remote').is(':checked')}
    if(t && c && l && d && i){
        if(remote){
            $('#loading_modal').modal({backdrop: 'static', keyboard: false});
            $.ajax({
                type: 'POST',
                url:'/p/post_new_job_external',
                data: data,
                success: function (response) {
                    if(response['status'] === 'success'){
                        document.location.pathname = '/p/job_posting/' + response['id'].toString()
                    }else{
                        custom_error_popup(response['message'])
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }else{
            if(city){
                $('#loading_modal').modal({backdrop: 'static', keyboard: false});
                $.ajax({
                type: 'POST',
                url:'/p/post_new_job_external',
                data: data,
                success: function (response) {
                    if(response['status'] === 'success'){
                        document.location.pathname = '/p/job_posting/' + response['id'].toString()
                    }else{
                        custom_error_popup(response['message'])
                    }
                },
                error: function () {
                    error_popup()
                }
            })
            }
        }
    }
})

$(document).on('click', '#edit_external_job', function () {
    var t = check_length_special($('#job_title_edit_external'), 0, 200, 'Must be between 0 & 200 characters')
    var c = check_length_special($('#job_company_name_edit_external'), 0, 200, 'Must be between 0 & 200 characters')
    var l = check_length_special($('#job_link_edit_external'), 0, 400, 'Must be a link') && isURL($('#job_link_edit_external').val())
    var d = check_length_special($('#job_description_edit_external'), 25, 1000, 'Must be between 25 & 1000 characters')
    var i = check_industries_selected($('#job_industries_edit_external'), 3)
    var city = check_length_special($('#job_city_edit_external'), 0, 50, 'Must be a valid city')
    var remote = $('#job_remote_edit_external').is(':checked');
    var data = {'id': $(this).attr('job-id').toString(),'title':$('#job_title_edit_external').val(), 'company': $('#job_company_name_edit_external').val(), 'link': $('#job_link_edit_external').val(),
                        'description':$('#job_description_edit_external').val(), 'industries':$('#job_industries_edit_external').val(), 'city': $('#job_city_edit_external').val(),
                        'remote':$('#job_remote_edit_external').is(':checked')}
    if(t && c && l && d && i){
        if(remote){
            $('#loading_modal').modal({backdrop: 'static', keyboard: false});
            $.ajax({
                type: 'POST',
                url:'/p/edit_job_external',
                data: data,
                success: function (response) {
                    if(response['status'] === 'success'){
                        document.location.pathname = '/p/job_posting/' + response['id'].toString()
                    }else{
                        custom_error_popup(response['message'])
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }else{
            if(city){
                $('#loading_modal').modal({backdrop: 'static', keyboard: false});
                $.ajax({
                type: 'POST',
                url:'/p/edit_job_external',
                data: data,
                success: function (response) {
                    if(response['status'] === 'success'){
                        document.location.pathname = '/p/job_posting/' + response['id'].toString()
                    }else{
                        custom_error_popup(response['message'])
                    }
                },
                error: function () {
                    error_popup()
                }
            })
            }
        }
    }
})

$(document).on('click', '#submit_quick_next', function () {
    var t = check_length_special($('#job_title_quick'), 0, 100, 'Must be between 0 & 100 characters')
    var c = check_length_special($('#job_company_name_quick'), 0, 100, 'Must be between 0 & 100 characters')
    var city = check_length_special($('#job_city_quick'), 0, 50, 'Must be a valid city')
    var remote = $('#job_remote_quick').is(':checked');
    var i = check_industries_selected($('#job_industries_quick'), 3)
    if(t && c && i){
        if(remote){
            $('#quick_apply_modal_1').modal('hide')
            $('#quick_apply_modal_2').modal({backdrop: 'static', keyboard: false})
            $('#job_type_selection').modal('hide')
        }else{
            if(city){
                $('#quick_apply_modal_1').modal('hide')
                $('#quick_apply_modal_2').modal({backdrop: 'static', keyboard: false})
            }
        }
    }

})

function check_compensation_ration(low, high){
    if(parseFloat(low) < parseFloat(high)){
        return true
    }else{
        if (!$('#compensation_high').next().hasClass('val')){
            $('#compensation_high').addClass('incorrect')
            $('#compensation_high').after('<div class="val"><div class="row"><div class="col-sm-12 validator" id="type-l">Must be more than prior field</div></div></div>')
        }
        return false
    }
}

$(document).on('click', '#submit_new_job_quick', function () {
    var t = check_length_special($('#job_title_quick'), 0, 200, 'Must be between 0 & 200 characters')
    var c = check_length_special($('#job_company_name_quick'), 0, 200, 'Must be between 0 & 200 characters')
    var city = check_length_special($('#job_city_quick'), 0, 50, 'Must be a valid city')
    var remote = $('#job_remote_quick').is(':checked');
    var i = check_industries_selected($('#job_industries_quick'), 3)
    var low = check_length_special($('#compensation_low'), 0, 50, 'Must be a valid number')
    var high = check_length_special($('#compensation_high'), 0, 50, 'Must be a valid number')
    var p = check_length_special($('#pitch'), 25, 500, 'Must be between 25 & 500 characters')
    var d = check_length_special($('#job_description_quick'), 25, 1000, 'Must be between 25 & 1000 characters')
    var high_comp = $('#compensation_high').val()
    high_comp = high_comp.replace(',', '')
    high_comp = high_comp.replace('$', '')
    var low_comp = $('#compensation_low').val()
    low_comp = low_comp.replace(',', '')
    low_comp = low_comp.replace('$', '')
    var a = check_compensation_ration(low_comp, high_comp)
    var data = {'title': $('#job_title_quick').val(), 'company':$('#job_company_name_quick').val(), 'city': $('#job_city_quick').val(),
    'remote':$('#job_remote_quick').is(':checked'), 'industries': $('#job_industries_quick').val(), 'compensation':$('#compensation_type').val(), 'low':low_comp,
    'high':high_comp, 'description': $('#job_description_quick').val(), 'pitch': $('#pitch').val(),
    'employment': $('#employment_type').val()}
    if(a && p && d && low && high){
        if(t && c && i){
        if(remote){
             $('#loading_modal').modal({backdrop: 'static', keyboard: false});
             $.ajax({
                 type: 'POST',
                 url: '/p/post_quick_job',
                 data: data,
                 success: function (response) {
                     if(response['status'] === 'success'){
                         document.location.pathname = '/p/job_posting/' + response['id'].toString()
                     }else{
                         custom_error_popup(response['message'])
                     }

                 },
                 error: function () {
                    error_popup()
                 }
             })
        }else{
            if(city){
                 $('#loading_modal').modal({backdrop: 'static', keyboard: false});
                 $.ajax({
                 type: 'POST',
                 url: '/p/post_quick_job',
                 data: data,
                 success: function (response) {
                    if(response['status'] === 'success'){
                         document.location.pathname = '/p/job_posting/' + response['id'].toString()
                     }else{
                         custom_error_popup(response['message'])
                     }
                 },
                 error: function () {
                    error_popup()
                 }
             })
            }
        }
    }
    }
})

$(document).on('click', '#submit_quick_edit', function () {
    var t = check_length_special($('#job_title_quick_edit'), 0, 200, 'Must be between 0 & 200 characters')
    var c = check_length_special($('#job_company_name_quick_edit'), 0, 200, 'Must be between 0 & 200 characters')
    var city = check_length_special($('#job_city_quick_edit'), 0, 50, 'Must be a valid city')
    var remote = $('#job_remote_quick_edit').is(':checked');
    var i = check_industries_selected($('#job_industries_quick_edit'), 3)
    var low = check_length_special($('#compensation_low_edit'), 0, 50, 'Must be a valid number')
    var high = check_length_special($('#compensation_high_edit'), 0, 50, 'Must be a valid number')
    var p = check_length_special($('#pitch_edit'), 25, 500, 'Must be between 25 & 500 characters')
    var d = check_length_special($('#job_description_quick_edit'), 25, 1000, 'Must be between 25 & 1000 characters')
    var high_comp = $('#compensation_high_edit').val()
    high_comp = high_comp.replace(',', '')
    high_comp = high_comp.replace('$', '')
    var low_comp = $('#compensation_low_edit').val()
    low_comp = low_comp.replace(',', '')
    low_comp = low_comp.replace('$', '')
    var a = check_compensation_ration(low_comp, high_comp)
    var data = {'id': $(this).attr('job-id'),'title': $('#job_title_quick_edit').val(), 'company':$('#job_company_name_quick_edit').val(), 'city': $('#job_city_quick_edit').val(),
    'remote':$('#job_remote_quick_edit').is(':checked'), 'industries': $('#job_industries_quick_edit').val(), 'compensation':$('#compensation_type_edit').val(), 'low':low_comp,
    'high':high_comp, 'description': $('#job_description_quick_edit').val(), 'pitch': $('#pitch_edit').val(),
    'employment': $('#employment_type_edit').val()}
    if(a && p && d && low && high){
        if(t && c && i){
        if(remote){
             $('#loading_modal').modal({backdrop: 'static', keyboard: false});
             $.ajax({
                 type: 'POST',
                 url: '/p/edit_quick_job',
                 data: data,
                 success: function (response) {
                     document.location.reload()
                 },
                 error: function () {
                    error_popup()
                 }
             })
        }else{
            if(city){
                 $('#loading_modal').modal({backdrop: 'static', keyboard: false});
                 $.ajax({
                 type: 'POST',
                 url: '/p/edit_quick_job',
                 data: data,
                 success: function (response) {
                    document.location.reload()
                 },
                 error: function () {
                    error_popup()
                 }
             })
            }
        }
    }
    }
})

$(document).on('click', '#back_to_quick_1', function () {
    $('#quick_apply_modal_1').modal({backdrop: 'static', keyboard: false})
    $('#quick_apply_modal_2').modal('hide')
    $('#job_type_selection').modal('hide')
})

// Jquery Dependency

$(document).on('keyup', "#compensation_low", function () {
    formatCurrency($(this));
})

$(document).on('blur', "#compensation_low", function () {
    formatCurrency($(this), "blur");
})


$(document).on('keyup', "#compensation_high", function () {
    formatCurrency($(this));
})

$(document).on('blur', "#compensation_high", function () {
    formatCurrency($(this), "blur");
})

$(document).on('keyup', "#compensation_low_edit", function () {
    formatCurrency($(this));
})

$(document).on('blur', "#compensation_low_edit", function () {
    formatCurrency($(this), "blur");
})


$(document).on('keyup', "#compensation_high_edit", function () {
    formatCurrency($(this));
})

$(document).on('blur', "#compensation_high_edit", function () {
    formatCurrency($(this), "blur");
})

$(document).ready(function () {
    $('.money_convert').each(function () {
        $(this).text('$' + formatNumber($(this).text()).toString())
    })
})


function formatNumber(n) {
  // format number 1000000 to 1,234,567
  return n.replace(/\D/g, "").replace(/\B(?=(\d{3})+(?!\d))/g, ",")
}


function formatCurrency(input, blur) {
  // appends $ to value, validates decimal side
  // and puts cursor back in right position.

  // get input value
  var input_val = input.val();

  // don't validate empty input
  if (input_val === "") { return; }

  // original length
  var original_len = input_val.length;

  // initial caret position
  var caret_pos = input.prop("selectionStart");

  // check for decimal
  if (input_val.indexOf(".") >= 0) {

    // get position of first decimal
    // this prevents multiple decimals from
    // being entered
    var decimal_pos = input_val.indexOf(".");

    // split number by decimal point
    var left_side = input_val.substring(0, decimal_pos);
    var right_side = input_val.substring(decimal_pos);

    // add commas to left side of number
    left_side = formatNumber(left_side);

    // validate right side
    right_side = formatNumber(right_side);

    // On blur make sure 2 numbers after decimal
    if (blur === "blur") {
      right_side += "00";
    }

    // Limit decimal to only 2 digits
    right_side = right_side.substring(0, 2);

    // join number by .
    input_val = "$" + left_side + "." + right_side;

  } else {
    // no decimal entered
    // add commas to number
    // remove all non-digits
    input_val = formatNumber(input_val);
    input_val = "$" + input_val;

    // final formatting
    if (blur === "blur") {
      input_val += ".00";
    }
  }

  // send updated string to input
  input.val(input_val);

  // put caret back in the right position
  var updated_len = input_val.length;
  caret_pos = updated_len - original_len + caret_pos;
  input[0].setSelectionRange(caret_pos, caret_pos);
}

$(document).on('click', '#deactivate_quick_job', function () {
    var id = $(this).attr('job-id')
    var a = confirm('Are you sure you would like to de-activate this job?')
    if(a){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
        type: 'POST',
        url: '/p/deactivate_job',
        data: {'id': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                document.location.pathname = response['url']
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
    }

})

$(document).on('click', '#deactivate_external_job', function () {
    var id = $(this).attr('job-id')
    var a = confirm('Are you sure you would like to de-activate this job?')
    if(a){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
        type: 'POST',
        url: '/p/deactivate_job',
        data: {'id': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                document.location.pathname = response['url']
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
    }

})

$(document).on('click', '#removed_candidates', function () {
    $('#removed_candidates_modal').modal({backdrop: 'static', keyboard: false})
})

$(document).on('click', '#removed_applicants', function () {
     $('#loading_modal').modal({backdrop: 'static', keyboard: false})
    var id = $(this).attr('job-id')
    $.ajax({
        type: 'GET',
        url: '/p/get_removed_applicants',
        data: {'a': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#removed_content').html( response['removed'])
                $('#loading_modal').modal('hide')
                $('#removed_applicants_modal').modal({backdrop: 'static', keyboard: false})
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }

    })
})



$(document).on('click', '#deactivate_search', function () {
    var id = $(this).attr('search-id')
    var a = confirm('Are you sure you would like to de-activate this Talent Search?')
    if(a){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
        type: 'POST',
        url: '/p/deactivate_talent_search',
        data: {'id': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                document.location.pathname = response['url']
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
    }

})

$(document).on('click', '.note-submit-applicant', function () {
    var id = $(this).attr('applicant-id')
    if(check_length_special($('#notes_' + id.toString()), 0, 500, 'Must be between 1 and 500 characters' )) {
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        var note = $('#notes_' + id.toString()).val()

        $.ajax({
            type: 'POST',
            url: '/p/post_applicant_note',
            data: {'q': note, 'a': id},
            success: function (response) {
                if(response['status'] === 'success'){
                    if($($('.notes_container_' + id.toString()).children()[0]).hasClass('no-posts')) {
                        $($('.notes_container_' + id.toString()).children()[0]).remove()
                    }
                    $('.notes_container_' + id.toString()).prepend(response['html'])
                    $('#notes_' + id.toString()).val('')
                    $('#notes_counter_' + id.toString()).text(parseInt($('#notes_counter_' + id.toString()).text()) + 1)
                    make_moments()
                    $('#loading_modal').modal('hide');
                }else{
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                error_popup()
            }

        });
    }
});

$(document).on('click', '#open_terminated_material', function () {
    $('#terminated_material').modal({backdrop: 'static', keyboard: false})
})

$(document).on('click', '#reactivate_job', function () {
    var id = $(this).attr('job-id')
    var a = confirm('Are you sure you would like to reactivate this job posting?')
    if(a){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
            type: 'POST',
            url: '/p/reactivate_job',
            data: {'id': id.toString()},
            success: function (response) {
                if(response['status'] === 'success'){
                    document.location.pathname = '/p/job_posting/' + id
                }else{
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                error_popup()
            }
        })
    }
})

$(document).on('click', '#reactivate_search', function () {
    var id = $(this).attr('search-id')
    var a = confirm('Are you sure you would like to reactivate this Talent Search?')
    if(a){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
            type: 'POST',
            url: '/p/reactivate_talent_search',
            data: {'id': id.toString()},
            success: function (response) {
                if(response['status'] === 'success'){
                    document.location.pathname = '/p/saved_search/' + id
                }else{
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                error_popup()
            }
        })
    }
})

$(document).on('click', '#delete_search', function () {
    var id = $(this).attr('search-id')
    var row = $('.terminated_search_row[search-id="' + id.toString() + '"]')
    var a = confirm('Are you sure you would like to delete this Talent Search? It will be permanently removed.')
    if(a){
        row.html('\'<div class="loadingio-spinner-spinner-5m5wfwkhl3a" style="text-align: center; margin: auto; display: block"><div class="ldio-fxcp7ev3c">\\n\' +\n' +
            '        \'<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\\n\' +\n' +
            '        \'</div></div>')
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
            type: 'POST',
            url: '/p/delete_talent_search',
            data: {'id': id.toString()},
            success: function (response) {
                if(response['status'] === 'success'){
                    row.remove()
                    custom_success_popup('Search successfully removed (permanent)')
                }else{
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                error_popup()
            }
        })
    }
})

$(document).on('click', '#delete_job', function () {
    var id = $(this).attr('job-id')
        var row = $('.terminated_job_row[job-id="' + id.toString() + '"]')
    var a = confirm('Are you sure you would like to delete this Job Posting? It will be permanently removed.')
    if(a){
        row.html('\'<div class="loadingio-spinner-spinner-5m5wfwkhl3a" style="text-align: center; margin: auto; display: block"><div class="ldio-fxcp7ev3c">\\n\' +\n' +
            '        \'<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\\n\' +\n' +
            '        \'</div></div>')
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
            type: 'POST',
            url: '/p/delete_job',
            data: {'id': id.toString()},
            success: function (response) {
                if(response['status'] === 'success'){
                    row.remove()
                    custom_success_popup('Job Posting successfully removed (permanent)')
                }else{
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                error_popup()
            }
        })
    }
})

$(document).on('click', '#remove_applicant', function () {
    var a = confirm('Are you sure you would like to remove this applicant? This action is permanent.')
    if(a){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false})
    var id = $(this).attr('applicant-id')
    $.ajax({
        type:'POST',
        url: '/p/remove_applicant',
        data: {'a': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#applicant_modal_viewer').modal('hide')
                $('.applicant-card[applicant-id="' + id.toString() + '"]').parent().remove()
                fix_orders_applicants()
                custom_success_popup('Applicant Removed')
            }
            else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
    }
})

$(document).on('click', '#remove_candidate', function () {
    var a = confirm('Are you sure you would like to remove this candidate? This action is permanent.')
    if(a){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false})
    var id = $(this).attr('candidate-id')
    $.ajax({
        type:'POST',
        url: '/p/remove_candidate',
        data: {'a': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#candidate_modal_viewer').modal('hide')
                $('.candidate-card[candidate-id="' + id.toString() + '"]').parent().remove()
                fix_orders_candidates()
                custom_success_popup('Candidate Removed')
            }
            else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
    }
})

function fix_orders_candidates(){
    var count = 1
    $('.ranking_indicator_special').each(function () {
                $(this).text('#' + count.toString())
               $('.ranking_indicator[candidate-id="' + $(this).parent().attr('candidate-id').toString() + '"]').text('#' + count.toString())
               count += 1
       })
};

function fix_orders_applicants(){
    var count = 1
    $('.ranking_indicator_special').each(function () {
                $(this).text('#' + count.toString())
               $('.ranking_indicator[applicant-id="' + $(this).parent().attr('applicant-id').toString() + '"]').text('#' + count.toString())
               count += 1
       })
};

  $( function() {
    $( "#sortable" ).sortable({
        handle: '.ranking_indicator_special',
        // items : ':not(.col-sm-12)',
        change: function(event, ui){
            $('#saving_loader').css({'display': 'inline-block'})
        },
    update: function(event, ui) {
            var count = 1
            var order = []
           $('.ranking_indicator_special').each(function () {
                $(this).text('#' + count.toString())
               $('.ranking_indicator[candidate-id="' + $(this).parent().attr('candidate-id').toString() + '"]').text('#' + count.toString())
               order.push($(this).parent().attr('candidate-id'))
               count += 1
           })
        var id = $(this).attr('search-id')

        $.ajax({
            type: 'POST',
            url: '/p/save_candidate_orders',
            data: {'orders': order, 'a': id.toString()},
            success: function(){
                            $('#saving_loader').css({'display': 'none'})
            },
            error: function () {
                custom_error_popup('Your reorders are not saving. Please try reloading the page.')
            }
        })
        }});
    $( "#sortable" ).disableSelection();
    $( "#sortable1" ).sortable({
        handle: '.ranking_indicator_special',
        // items : ':not(.col-sm-12)',
        change: function(event, ui){
            $('#saving_loader').css({'display': 'inline-block'})
        },
    update: function(event, ui) {
            var count = 1
            var order = []
           $('.ranking_indicator_special').each(function () {
                $(this).text('#' + count.toString())
               $('.ranking_indicator[applicant-id="' + $(this).parent().attr('applicant-id').toString() + '"]').text('#' + count.toString())
               order.push($(this).parent().attr('applicant-id'))
               count += 1
           })
        var id = $(this).attr('job-id')
        $.ajax({
            type: 'POST',
            url: '/p/save_applicant_orders',
            data: {'orders': order, 'a': id.toString()},
            success: function(){
                $('#saving_loader').css({'display': 'none'})
            },
            error: function () {
                custom_error_popup('Your reorders are not saving. Please try reloading the page.')
            }
        })
        }});
    $( "#sortable1" ).disableSelection();
  } );

  $(document).on('click', '#re-initiate_applicant', function () {
    var id = $(this).attr('applicant-id')
    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
    $.ajax({
        type: 'POST',
        url: '/p/re_init_applicant',
        data: {'a': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                document.location.reload()
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
})

$(document).on('click', '#re-initiate_candidate', function () {
    var id = $(this).attr('candidate-id')
    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
    $.ajax({
        type: 'POST',
        url: '/p/re_init_candidate',
        data: {'a': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                document.location.reload()
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
})

$(document).on('click', '#edit_talent_search', function () {
    var id = $(this).attr('search-id')
    var title = $('#search_title_edit');
    var city = $('#city_edit');
    var industry = $('#industry_edit');
    var description = $('#search_description_edit')
    var d_check = check_length_special(description, -1, 500, 'Description must be between 0 & 500 characters')
    var title_check = check_length_special(title, 0, 80, 'Title must be between 1 & 80 characters')
    var city_check = check_length_special(city, 0, 80, 'Please enter a valid city')
    var industry_check = check_industry(industry);
    var public_val = $('#public_edit').is(':checked');
    var remote = $('#remote_edit').is(':checked')
    if(remote){
        if (title_check && industry_check && d_check){
            $('#loading_modal').modal({backdrop: 'static', keyboard: false});
            var data = {'title':title.val(), 'city':city.val(), 'industry':industry.val(), 'public': public_val,
                'description':description.val(), 'remote':remote, 'id': id.toString()}
            $.ajax({
                type: 'POST',
                url: '/p/edit_recruiter_search',
                data: data,
                success: function (response) {
                    if (response['status'] === 'success') {
                        document.location.reload()
                    } else {
                        custom_error_popup(response['message'])
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }else{
        if (title_check && industry_check && city_check && d_check){
            $('#loading_modal').modal({backdrop: 'static', keyboard: false});
            var data = {'title':title.val(), 'city':city.val(), 'industry':industry.val(), 'public': public_val,
                'description':description.val(), 'remote':remote, 'id': id.toString()}
            $.ajax({
                type: 'POST',
                url: '/p/edit_recruiter_search',
                data: data,
                success: function (response) {
                    if (response['status'] === 'success') {
                        document.location.reload()
                    } else {
                        custom_error_popup(response['message'])
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }
})

$(document).on('hidden.bs.modal', '#candidate_modal_viewer', function () {
  $('#candidate_body').html('<div class="loadingio-spinner-spinner-ok7idc80he9"><div class="ldio-u1oevpwp8f">\n' +
      '                                                <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
      '                                                </div></div>')
})

$(document).on('hidden.bs.modal', '#applicant_modal_viewer', function () {
  $('#applicant_body').html('<div class="loadingio-spinner-spinner-ok7idc80he9"><div class="ldio-u1oevpwp8f">\n' +
      '                                                <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
      '                                                </div></div>')
})

$(document).on("change hover click blur focus", '#colleague', function() {
    if($(this).val() !== '0'){
        $('#share_btn').css({'display':'inline-block'})
    }else{
        $('#share_btn').css({'display':'none'})
    }
});

  $(document).on("change hover click blur focus", '#colleague_job', function() {
    if($(this).val() !== '0'){
        $('#share_btn_job').css({'display':'inline-block'})
    }else{
        $('#share_btn_job').css({'display':'none'})
    }
});

$(document).on('click', '#share_btn', function () {
    var r_id = $('#colleague').val()
    var s_id = $(this).attr('search_id')
    if(r_id !== '0'){
        var row = $('option.recruiter_add[value="' + r_id.toString() +'"]')
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
            type: 'POST',
            url: '/p/share_recruiter',
            data: {'search_id': s_id.toString(), 'recruiter_id': r_id.toString()},
            success: function (response) {
                if(response['status'] === 'success'){
                    $('#shared_recruiters').prepend(response['html'])
                    $('#colleague').selectpicker('val', 0)
                    $(row).remove()
                    $('#colleague').selectpicker('refresh')
                    custom_success_popup('Recruiter Added to search. They have been notified via email and ILMJTCV notification')
                }else{
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                error_popup()
            }

        })
    }
})

$(document).on('click', '#share_btn_job', function () {
    var r_id = $('#colleague_job').val()
    var j_id = $(this).attr('job_id')
    if(r_id !== '0'){
        var row = $('option.recruiter_add[value="' + r_id.toString() +'"]')
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
            type: 'POST',
            url: '/p/share_recruiter_job',
            data: {'job_id': j_id.toString(), 'recruiter_id': r_id.toString()},
            success: function (response) {
                if(response['status'] === 'success'){
                    $('#shared_recruiters').prepend(response['html'])
                    $('#colleague_job').selectpicker('val', 0)
                    $(row).remove()
                    $('#colleague_job').selectpicker('refresh')
                    custom_success_popup('Recruiter Added to search. They have been notified via email and ILMJTCV notification')
                }else{
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                error_popup()
            }

        })
    }
})