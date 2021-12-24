function check_channel_chosen(element){
    if(element.attr('forum-id').toString() === '0'){
        $('#forum-menu-dropdown-toggle').addClass('incorrect')
        return false
    }else{
        return true
    }
}

function check_length_special(element, min, max, message) {
    if(element.val().length > min && element.val().length < max){
        return true
    }else{
        if (!element.next().hasClass('val')){
            element.addClass('incorrect')
            element.after('<div class="val"><div class="row"><div class="col-sm-12 validator" id="type-l">' +  message + ' (' + element.val().length + ')' +'</div></div></div>')
        }
        return false
    }
}

function check_location(country, city, zip) {
    if (country !== '235'){
        if (city.length > 2){
            return true
        }else{
            $('#g_city').addClass('incorrect')
            return false
        }
    }else{
        if (zip.length > 4){
            return true
        }else{
            $('#g_zip').addClass('incorrect')
            return false
        }
    }
}

function verify_unique_values(){
    var username = document.getElementById('g_username');
    var email = document.getElementById('g_email');
    var content = {'u': username.value, 'e': email.value};

    $.ajax({
        type: 'POST',
        url: "/auth/verify_unique",
        data: content,
        success: function (data) {
            if (data['e'] && data['u']){
                let i = true
            }else{
                if (!data['e']){
                    $('label[for="g_email"]').addClass('non_unique_text');
                    $(email).addClass('non-unique');
                    if (email.previousElementSibling !== null) {
                        if (email.previousElementSibling.id !== 'email_not_unique') {
                            $(email).before('<div class="val" id="email_not_unique"><div class="row"><div class="col-sm-12 validator" id="type-unique">Email Already in Use</div></div></div>');
                        }
                    }else{
                    $(email).before('<div class="val" id="email_not_unique"><div class="row"><div class="col-sm-12 validator" id="type-unique">Email Already in Use</div></div></div>');
                }}
                if (!data['u']){
                    $('label[for="g_username"]').addClass('non_unique_text');
                    $(username).addClass('non-unique');
                    if (username.previousElementSibling !== null) {
                        if (username.previousElementSibling.id !== 'username_not_unique') {
                            $(username).before('<div class="val" id="username_not_unique"><div class="row"><div class="col-sm-12 validator" id="type-unique">Username Already in Use</div></div></div>');
                        }
                    }else{
                        $(username).before('<div class="val" id="username_not_unique"><div class="row"><div class="col-sm-12 validator" id="type-unique">Username Already in Use</div></div></div>');
                    }
                }
                let i = false
            }
        },
        error: function () {
            error_popup()

        }
    });
}


// Toggle post modal on forum, chat pages
$(document).on('click', '#post_btn', function () {
    $('#post_modal').modal({backdrop: 'static', keyboard: false});
})

// Toggle comment modal on post page
$(document).on('click', '.post-editor-container', function () {
    $('#comment_modal').modal({backdrop: 'static', keyboard: false});
})

// Toggle comment modal on post page
$(document).on('click', '.open_comment', function () {
    $('#comment_modal').modal({backdrop: 'static', keyboard: false});
})

// Change forum-id selector for posting from chat
$(document).on('click', '.forum-dropdown-option', function () {
    $('#post-destination-forum-title').text($(this).text())
    $('.post_submit_btn').attr({'forum-id': $(this).attr('forum-id')})
   $('#forum-menu-dropdown-toggle').click()
})

// Toggle Delete Post Modal
$(document).on('click', '.post-delete', function () {
    $('#delete_modal').modal({backdrop: 'static', keyboard: false})
    $('#delete_post_official').attr('post-id', $(this).attr('post-id'))

})

// Clear Delete Post Modal
$(document).on('hidden.bs.modal', '#delete_modal', function () {
  $('#delete_post_official').attr('post-id', 0)
})

// Toggle Edit Post Modal
$(document).on('click', '.post-edit', function () {
    var id = $(this).attr('post-id')
    $('#edit_post_modal').modal({backdrop: 'static', keyboard: false})
    $('#forum-menu-dropdown-toggle_edit').text($('#forum_title_' + id.toString()).text())
    $('#post_subject_edit').val($('.post_' + id.toString()).children()[0].innerText)
    $('#post_post_edit').val($('.post_' + id.toString()).children()[1].innerText)
    $('#edit_post_official').attr('post-id', $(this).attr('post-id'))
    $('.edit_post_submit_btn').attr('post-id', id)
})

// Clear Edit Post Modal
$(document).on('hidden.bs.modal', '#edit_post_modal', function () {
  $('.edit_post_submit_btn').attr('post-id', 0)
    $('#forum-menu-dropdown-toggle_edit').text('Select a forum')
    $('#post_subject_edit').val('');
    $('#post_post_edit').val('');
})

// Toggle Flag Post Modal
$(document).on('click', '.post-flag', function () {
    $('#flag_modal').modal({backdrop: 'static', keyboard: false})
    if($(this).hasClass('comment-option')){
        $('#flag_post_official').attr('type', 1)
    }else if(($(this).hasClass('post-option'))){
        $('#flag_post_official').attr('type', 0)
    }
    $('#flag_post_official').attr('post-id', $(this).attr('post-id'))

})

// Clear Flag Post Modal
$(document).on('hidden.bs.modal', '#flag_modal', function () {
  $('#flag_post_official').attr('post-id', 0)
    $('#flag_post_comment').val('')
})

// Like/Unlike Post
$(document).on('click', '.likes_indicator', function () {
    var post_id = $(this).attr('post-id')
    var like_count = $('#likes_count_'+ post_id.toString())
    if($(this).hasClass('liked')){
        like_count.text(parseInt(like_count.text()) - 1)
        like_count.parent().removeClass('liked')
        $.ajax({
            type: 'POST',
            url: '/unlike_post',
            data: {'post_id': post_id.toString()},
            error: function () {
                like_count.html((parseInt(like_count.text()) + 1).toString)
                like_count.parent().addClass('liked')
                error_popup()
            }
        })
    }else{
        like_count.text(parseInt(like_count.text()) + 1)
        like_count.parent().addClass('liked')
        $.ajax({
            type: 'POST',
            url: '/like_post',
            data: {'post_id': post_id.toString()},
            error: function () {
                like_count.text(parseInt(like_count.text()) - 1)
                like_count.parent().removeClass('liked')
                error_popup()
            }
        })
    }
});

// Copying Post URL
$(document).on('click', '.post-copy', function () {
    var dummy = document.createElement('input'),
    text = document.location.host + '/post/' + $(this).attr('post-id').toString()
    document.body.appendChild(dummy);
    dummy.value = text;
    dummy.select();
    document.execCommand('copy');
    document.body.removeChild(dummy);
    link_copied('Link Copied')
})

$(document).on('click', '.copy_link', function () {
    var dummy = $('<input id="copy_holder">').val(document.location.href).appendTo('body').select();
    dummy.focus();
    document.execCommand('copy');
    $('#copy_holder').remove()
    link_copied('Link Copied')
})

// Deleting a post
$(document).on('click', '#delete_post_official', function () {
    $('#delete_modal').modal('hide')
    if(document.location.pathname.includes('/post')){
        var post = $('.main-post-area');
        new_html = '            <div class="deleted" style="overflow-y: auto; max-height: 70vh; margin: 0">\n' +
            '            <div class="col-sm-12">\n' +
            '                <div class="no-comments">This post has been deleted. <br> :( <br><br> You are now being redirected.</div>\n' +
            '            </div>\n' +
            '        </div>\n'
        post.replaceWith(new_html)
    }else{
        var post = $('#post_full_' + $(this).attr('post-id').toString())
    }
    var id = $(this).attr('post-id').toString()
    post.css({'display':'none'})
    $.ajax({
        type: 'POST',
        url: '/delete_post',
        data: {'post_id': id},
        success: function () {
            post.remove()
            if(document.location.pathname.includes('/post')){
                document.location.pathname = '/chat_new'
            }else{
                if($('.posts-table-col').children().length === 0){
                    $('.posts-table-col').prepend("<div class='no-comments'>No posts yet. <br>Your's can be the first!!!</div>")
                }
            }
        },
        error: function () {
            error_popup()
            post.css({'display':'block'})
        }
    })
    custom_success_popup('Post Deleted')

})

// Submitting flagged post case
$(document).on('click', '#flag_post_official', function () {
    var post_id = $(this).attr('post-id')
    var type = $(this).attr('type')
    if(check_length_special($('#flag_post_comment'), 0, 400, 'Must be between 0 & 400 characters')){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
            type: 'POST',
            url: '/flag_post',
            data: {'post_id':post_id.toString(), 'explanation': $('#flag_post_comment').val(), 'report_type': type},
            success: function(response){
                $('#loading_modal').modal('hide');
                $('#flag_modal').modal('hide')
                if(response['status'] === 'success'){
                    custom_success_popup('Post reported. Our community managers will look into your' +
                        ' report and decide how best to proceed.')
                }else{
                    custom_error_popup(response['message'])
                }
            },
            error: function (response) {
                error_popup()
            }
        })
    }
})

// Clearing text fields of any errors
$(document).on('keyup keydown focus blur', 'input[type=text], textarea, input[type=number]', function () {
    $(this).removeClass('incorrect');
    $(this).next().removeClass('incorrect_text');
    if ($(this).next().hasClass('val')){
        $(this).next().remove()
    }
})

// Submitting a comment from post page
$(document).on('click', '.comment_submit_btn', function () {
    var post_id = $(this).attr('post-id')
    if(check_length_special($('#post_post'), 0, 1800, 'Must be between 1 and 1800 characters')){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
            type: 'POST',
            url: '/add_comment',
            data: {'post_id': post_id, 'body': $('#post_post').val()},
            success: function(response) {
                if(response['status'] === 'success'){
                    $('#post_post').val('')
                    $('#comments_area').prepend(response['html'])
                    $('#comment_modal').modal('hide')
                    $('#loading_modal').modal('hide');
                    $('.no-comments').remove()
                    $('#comments_count_' + post_id).text(parseInt($('#comments_count_' + post_id).text()) + 1)
                    custom_success_popup('Post successfully posted!')
                    make_moments()
                }else{
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                error_popup()
            }
        })
    }
});

// Clearing forum selector of any errors
$(document).on('change focus click blur', '#forum-menu-dropdown-toggle', function () {
    if($(this).hasClass('incorrect')){
        $(this).removeClass('incorrect')
    }
})

// Submitting a new post from Forum, Chat
$(document).on('click', '.post_submit_btn', function () {
    var subject_check = check_length_special($('#post_subject'), 0, 180, 'Must be between 1 and 180 characters')
    var post_check = check_length_special($('#post_post'), 0, 1800, 'Must be between 1 and 1800 characters')
    var forum_id = $(this).attr('forum-id')
    var channel_check = check_channel_chosen($('.post_submit_btn'))
    if(document.location.pathname.includes('/chat')){
        var type = 0
    }else if(document.location.pathname.includes('/forum')){
        var type = 1
    }
    if(subject_check && post_check && channel_check){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
            type: 'POST',
            url: '/add_post',
            data: {'forum_id': forum_id, 'body': $('#post_post').val(), 'subject': $('#post_subject').val(), 'type':type},
            success: function(response) {
                if(response['status'] === 'success'){
                    $('#post-destination-forum-title').text('Select a forum')
                    $('#post_subject').val('')
                    $('#post_post').val('')
                    $('.posts-table-col').prepend(response['html'])
                    $('#post_modal').modal('hide')
                    $('#loading_modal').modal('hide');
                    custom_success_popup('Post successfully posted!')
                    $('.no-comments').remove()
                    make_moments()
                }else{
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                error_popup()
            }
        })
    }
});

// Submit edit to a post
$(document).on('click', '.edit_post_submit_btn', function () {
    var subject_check = check_length_special($('#post_subject_edit'), 0, 180, 'Must be between 1 and 180 characters')
    var post_check = check_length_special($('#post_post_edit'), 0, 1800, 'Must be between 1 and 1800 characters')
    var post_id = $(this).attr('post-id')
    if(subject_check && post_check){
        var title = $('#post_subject_edit').val()
        var body =  $('#post_post_edit').val()
        $($('.post_' + post_id.toString()).children()[0]).text(title)
        $($('.post_' + post_id.toString()).children()[1]).text(body)
        $('#edit_post_modal').modal('hide')
        $.ajax({
            type: 'POST',
            url: '/edit_post',
            data: {'post_id': post_id, 'body': body, 'subject':title},
            error: function () {
                error_popup()
                window.location.reload()
            }
        })
    }
})

// Toggle comment modal on post page
$(document).on('click', '.comment-edit', function () {
    $('#edit_comment_modal').modal({backdrop: 'static', keyboard: false});
    $('.edit_comment_submit_btn').attr('comment-id', $(this).attr('comment-id'))
    var body = $('#comment_full_' + $(this).attr('comment-id').toString()).text()
    $('#comment_text_edit').val(body)
    $('.comment-delete').attr('comment-id', $(this).attr('comment-id') )
    $('.comment-delete').attr('post-id', $(this).attr('post-id') )
})

// Clear Edit Comment Modal
$(document).on('hidden.bs.modal', '#edit_comment_modal', function () {
  $('#edit_comment_submit_btn').attr('comment-id', 0)
    $('#comment_text_edit').val('')
    $('.comment-delete').attr('comment-id', 0 )
    $('.comment-delete').attr('post-id', 0 )
})

// Delete Comment
$(document).on('click', '.comment-delete', function () {
    var id = $(this).attr('comment-id').toString()
    var post_id = $(this).attr('post-id').toString()
    var post = $('#comment_' + id.toString())
    post.css({'display':'none'})
    $('#edit_comment_modal').modal('hide')
    $.ajax({
        type: 'POST',
        url: '/delete_comment',
        data: {'comment_id': id},
        success: function () {
            post.remove()
            if($('#comments_area').children().length === 0){
                $('#comments_area').prepend("<div class='no-comments'>No posts yet. <br>Your's can be the first!!!</div>")
            }
            $('#comments_count_' + post_id).text(parseInt($('#comments_count_' + post_id).text()) - 1)

        },
        error: function () {
            error_popup()
            post.css({'display':'block'})
        }
    })
    custom_success_popup('Comment Deleted')

})

// Submit edit to a comment
$(document).on('click', '.edit_comment_submit_btn', function () {
    var post_check = check_length_special($('#comment_text_edit'), 0, 1800, 'Must be between 1 and 1800 characters')
    var comment_id = $(this).attr('comment-id')
    if(post_check){
        var body =  $('#comment_text_edit').val()
        $('#comment_full_' + comment_id.toString()).text(body)
        $('#edit_comment_modal').modal('hide')
        $.ajax({
            type: 'POST',
            url: '/edit_comment',
            data: {'comment_id': comment_id, 'body': body},
            error: function () {
                error_popup()
                window.location.reload()
            }
        })
    }
})

// Downvote comment
$(document).on('click', '.downvote', function () {
    var id = $(this).attr('id').split('_')[1];
    var num = parseInt($('#vote_count_' + id.toString()).text())
    if($('#upvote_' + id.toString()).hasClass('upvoted')){
        $('#upvote_' + id.toString()).removeClass('upvoted')
         $('#vote_count_' + id.toString()).text(num - 2)
        $(this).addClass('downvoted')
    }else{
        if($(this).hasClass('downvoted')){
        $('#vote_count_' + id.toString()).text(num + 1)
        $(this).removeClass('downvoted')
    }else{
        $('#vote_count_' + id.toString()).text(num - 1)
        $(this).addClass('downvoted')
    }
    }
        $.ajax({
        type: 'POST',
        url: '/downvote_comment',
        data: {'comment_id': id},
        error: function () {
            error_popup()
            window.location.reload()
        }
    })
})

// Upvote comment
$(document).on('click', '.upvote', function () {
    var id = $(this).attr('id').split('_')[1];
    var num = parseInt($('#vote_count_' + id.toString()).text())
    if($('#downvote_' + id.toString()).hasClass('downvoted')){
        $('#downvote_' + id.toString()).removeClass('downvoted')
         $('#vote_count_' + id.toString()).text(num + 2)
        $(this).addClass('upvoted')
    }else {
        if ($(this).hasClass('upvoted')) {
            $('#vote_count_' + id.toString()).text(num - 1)
            $(this).removeClass('upvoted')
        } else {
            $('#vote_count_' + id.toString()).text(num + 1)
            $(this).addClass('upvoted')
        }
    }
    $.ajax({
        type: 'POST',
        url: '/upvote_comment',
        data: {'comment_id': id},
        error: function () {
            error_popup()
            window.location.reload()
        }
    })
})

// Open more forums modal
$(document).on('click', '#more_forums', function () {
    $('#suggested_content').html('\'<div class="loadingio-spinner-spinner-5m5wfwkhl3a" style="text-align: center; margin: auto; display: block"><div class="ldio-fxcp7ev3c">\\n\' +\n' +
            '        \'<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\\n\' +\n' +
            '        \'</div></div>')
    $('#more_forums_modal').modal({backdrop: 'static', keyboard: false})
    $.ajax({
        type: 'GET',
        url: '/get_suggested',
        success: function (response) {
            if(response['status'] === 'success'){
                $('#suggested_content').html(response['html'])
                make_moments()
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
})

// Open more forums modal
$(document).on('click', '#deactivated_searches_toggle', function () {
    $('#deactivated_content').html('\'<div class="loadingio-spinner-spinner-5m5wfwkhl3a" style="text-align: center; margin: auto; display: block"><div class="ldio-fxcp7ev3c">\\n\' +\n' +
            '        \'<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\\n\' +\n' +
            '        \'</div></div>')
    $('#deactivated_searches_modal').modal({backdrop: 'static', keyboard: false})
    $.ajax({
        type: 'GET',
        url: '/get_deactivated',
        success: function (response) {
            if(response['status'] === 'success'){
                $('#deactivated_content').html(response['html'])
                make_moments()
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
})

$(document).on('click', '.join_forum', function () {
    var id = $(this).attr('forum-id').toString()
    var element = $(this)
    element.removeClass('join_forum')
    element.addClass('leave_forum')
    element.text('- Unfollow')
    $('#forums-divider').after('<a href="/forum/' + id +'" id="forum_selector_' + id + '">' + $(element.prev()).html() + '</a>')
    $.ajax({
            type: 'POST',
            url: '/join_forum',
            data: {'forum_id': id},
            success: function (response) {
                if(response['status'] === 'success'){
                    custom_success_popup('Forum Joined')
                }else{
                    element.addClass('join_forum')
                element.removeClass('leave_forum')
                element.text('+ Follow')
                $('#forum_selector_' + id).remove()
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                element.addClass('join_forum')
                element.removeClass('leave_forum')
                element.text('+ Follow')
                $('#forum_selector_' + id).remove()
                error_popup()
            }
        })
})

$(document).on('click', '.leave_forum', function () {
    var id = $(this).attr('forum-id').toString()
    var element = $(this)
    element.addClass('join_forum')
    element.removeClass('leave_forum')
    element.text('+ Follow')
    $('#forum_selector_' + id).remove()
    $.ajax({
            type: 'POST',
            url: '/leave_forum',
            data: {'forum_id': id},
            success: function (response) {
                if(response['status'] === 'success'){
                    custom_success_popup('Forum Unfollowed')
                }else{
                    element.removeClass('join_forum')
                element.addClass('leave_forum')
                element.text('- Unfollow')
                $('#forums').after('<a href="/forum/' + id +'" id="forum_selector_' + id + '">' + $(element.prev()).html() + '</a>')
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                element.removeClass('join_forum')
                element.addClass('leave_forum')
                element.text('- Unfollow')
                $('#forums').after('<a href="/forum/' + id +'" id="forum_selector_' + id + '">' + $(element.prev()).html() + '</a>')
                error_popup()
            }
        })
})

// Add or Remove forum
$(document).on('click', '.suggested_forum_action', function () {
    var id = $(this).attr('forum-id').toString()
    var element = $(this)
    if(element.hasClass('join')){
        element.removeClass('join')
        element.addClass('leave')
        element.text('X')
        console.log($('#forums-divider'))
        $('#forums-divider').after('<a href="/forum/' + id +'" id="forum_selector_' + id + '">' + $(element.parent().prev().children()[0]).html() + '</a>')
        $.ajax({
            type: 'POST',
            url: '/join_forum',
            data: {'forum_id': id},
            success: function () {
                custom_success_popup('Forum Joined')
                if(document.location.pathname.includes('/chat')){
                    document.location.reload()
                }else if(document.location.pathname.includes('/forum/' + id)){
                    document.location.reload()
                }
            },
            error: function () {
                element.removeClass('leave')
                element.addClass('join')
                element.text('+')
                $('#forum_selector_' + id).remove()
            }
        })
    }else{
        element.removeClass('leave')
        element.addClass('join')
        element.text('+')
        $('#forum_selector_' + id).css({'display':'none'})
        $.ajax({
            type: 'POST',
            url: '/leave_forum',
            data: {'forum_id': id},
            success: function () {
                custom_success_popup('Forum Unfollowed')
                $('#forum_selector_' + id).remove()
                if(document.location.pathname.includes('/chat')){
                    document.location.reload()
                }else if(document.location.pathname.includes('/forum/' + id)){
                    document.location.reload()
                }
            },
            error: function () {
                element.removeClass('join')
                element.addClass('leave')
                element.text('X')
                $('#forum_selector_' + id).css({'display':'block'})
            }
        })
    }
})

// Open Sidebar on mobile
$(document).on('click', '.sidenav-opener', function () {
    if($('.sidenav').css('width') === '0px'){
        $('.sidenav').animate({ width: '22rem'}, 150);
        $('.sidenav').css({'display':'block'})
        $('#toggler').removeClass('fa-toggle-on')
        $('#toggler').addClass('fa-toggle-off')
    }else{
        $('.sidenav').animate({ width: '0px'}, 150);
        $('.sidenav').css({'display':'none'})
        $('#toggler').addClass('fa-toggle-on')
        $('#toggler').removeClass('fa-toggle-off')
    }
})

// Upload Img detection for profile
$(document).on('change', '#img_upload', function () {
    var filePath = this.value;
    var allowedExtensions =
            /(\.jpg|\.jpeg|\.png|\.gif)$/i;
    if (!allowedExtensions.exec(filePath)) {
        alert('Invalid file type');
        filePath.value = '';
    } else {
        $('#submit_img_upload').click()
    }
});

// Toggle Edit Profile Modal
$(document).on('click', '.edit_profile_toggle', function () {
    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
    $.ajax({
        type: 'GET',
        url: '/get_location',
        success: function (response) {
            $('#country').selectpicker('val', response['country'])
            if(response['country'] === 235){
                 $('#city_div').val(response['zip'])
                $('#city_div').css({'display':'none'});
                $('#city_div').val('');
                $('#zip_div').css({'display':'block'})
            }else{
                $('#city_div').val(response['city'])
                $('#city_div').css({'display':'block'});
                 $('#zip_div').val('');
                $('#zip_div').css({'display':'none'})
            }
        },
        error: function () {
            error_popup()
        }
    })
    $('#loading_modal').modal('hide');
    $('#edit_social_profile_modal').modal({backdrop: 'static', keyboard: false});
})

// Submit Edit profile
$(document).on('click', '#edit_profile_submit', function () {
    var username = check_username(document.getElementById('g_username'));
    var email = check_email(document.getElementById('g_email'));
    var name = $('#g_name').val().length > 0;
    var locations = check_location($('#country').val(), $('#g_city').val(), $('#g_zip').val())
    var bio = check_length_special($('#user_bio'), -1, 140, 'Bio must be between 0 & 140 characters')
    if(username && email && name && locations && bio){
        var username = document.getElementById('g_username');
        var email = document.getElementById('g_email');
        var content = {'u': username.value, 'e': email.value};
        $.ajax({
            type: 'POST',
            url: "/auth/verify_unique",
            data: content,
            success: function (data) {
                if (data['e'] && data['u']){
                    $('#loading_modal').modal({backdrop: 'static', keyboard: false})
                    $('#edit_profile_form').submit()
                }else{
                    if (!data['e']){
                        $('label[for="g_email"]').addClass('non_unique_text');
                        $(email).addClass('non-unique');
                        if (email.previousElementSibling !== null) {
                            if (email.previousElementSibling.id !== 'email_not_unique') {
                                $(email).before('<div class="val" id="email_not_unique"><div class="row"><div class="col-sm-12 validator" id="type-unique">Email Already in Use</div></div></div>');
                            }
                        }else{
                        $(email).before('<div class="val" id="email_not_unique"><div class="row"><div class="col-sm-12 validator" id="type-unique">Email Already in Use</div></div></div>');
                    }}
                    if (!data['u']){
                        $('label[for="g_username"]').addClass('non_unique_text');
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
});

// Change zip/city on country change
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

// delete user protocol
$(document).on('click', '#delete_user', function () {
    var r = confirm('Are you sure you would like to permanently delete your account and all of your accompanying data?')
    if(r){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
            type: 'POST',
            url: '/auth/delete_account',
            success: function (response) {
                $('#edit_social_profile_modal').modal('hide')
                if(response['status'] === 'success'){
                    custom_success_popup(response['message'])
                }else{
                    error_popup()
                }
            },
            error: function () {
                error_popup()
            }
        })
    }
})


function load_more_comments(element) {
    let div = $(element).get(0);
    let cont = $('#comments_area')
    if(div.scrollTop + div.clientHeight >= div.scrollHeight) {
        if(cont.children().last().attr('id') !== 'loading_spinner_more' && cont.children().last().attr('id') !== 'no-more-comments') {
            cont.append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/get_comments',
                data: {
                    'post_id': $(div).attr('post-id'),
                    'order': $(div).attr('ordering'),
                    'set': $(div).attr('data-set')
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        $('#loading_spinner_more').remove()
                        cont.append(response['html'])
                        $(div).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }
}


function load_more_candidates(element) {
    let cont = $(element).get(0)
    let div = $(element)
    if(cont.scrollTop + cont.clientHeight >= cont.scrollHeight) {
        if(div.children().last().attr('id') !== 'loading_spinner_more' && div.children().last().attr('id') !== 'no-more-candidates') {
            div.append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/p/load_more_candidates',
                data: {
                    'search_id': $(div).attr('search-id'),
                    'order': $(div).attr('ordering'),
                    'set': $(div).attr('data-set')
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        div.children().last().remove()
                        div.append(response['html'])
                        $(div).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }
}

function load_more_applicants(element) {
    let cont = $(element).get(0)
    let div = $(element)
    if(cont.scrollTop + cont.clientHeight >= cont.scrollHeight) {
        if(div.children().last().attr('id') !== 'loading_spinner_more' && div.children().last().attr('id') !== 'no-more-applicants') {
            div.append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/p/load_more_applicants',
                data: {
                    'job_id': $(div).attr('job-id'),
                    'order': $(div).attr('ordering'),
                    'set': $(div).attr('data-set')
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        div.children().last().remove()
                        div.append(response['html'])
                        $(div).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }
}


function load_more_posts(element) {
    let div = $(element).get(0);
    if(div.scrollTop + div.clientHeight >= div.scrollHeight) {
        if($(element).children().last().attr('id') !== 'loading_spinner_more' && $(element).children().last().attr('id') !== 'no-more-posts') {
            $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/load_more_posts',
                data: {
                    'forum_id': $(element).attr('forum-id'),
                    'order': $(element).attr('ordering'),
                    'set': $(element).attr('data-set'),
                    'style_type': $(element).attr('style-type')
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        $(element).children().last().remove()
                        $(element).append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }
}

function load_more_blogs(element) {
    let div = $(element).get(0);
    if(div.scrollTop + div.clientHeight >= div.scrollHeight) {
        if($(element).children().last().attr('id') !== 'loading_spinner_more' && $(element).children().last().attr('id') !== 'no-more-posts') {
            if($(element).children().last().attr('id') !== 'temp_row'){
                $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            }
            $.ajax({
                type: 'GET',
                url: '/load_more_blogs',
                data: {
                    'set': $(element).attr('data-set'),
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        $(element).children().last().remove()
                        $(element).append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }
}


function load_more_messages(element) {
    let div = $(element).get(0);
    if(div.scrollTop === 0) {
        if($(element).children().first().attr('id') !== 'loading_spinner_more' && $(element).children().first().attr('id') !== 'no-more-messages') {
            $(element).prepend('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/load_more_messages',
                data: {
                    'board_id': $(element).attr('board-id'),
                    'set': $(element).attr('data-set'),
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        $(element).children().first().remove()
                        $(element).prepend(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        $(div).animate({ scrollTop: $(div).prop('scrollHeight') / parseInt($(element).attr('data-set'))}, 200)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }
}

function load_more_appointment_notes(element) {
    let div = $(element).get(0);
    if(div.scrollTop === 0) {
        if($(element).children().first().attr('id') !== 'loading_spinner_more' && $(element).children().first().attr('id') !== 'no-more-notes') {
            $(element).prepend('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/load_more_appointment_notes',
                data: {
                    'id': $(element).attr('app-id'),
                    'set': $(element).attr('data-set'),
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        $(element).children().first().remove()
                        $(element).prepend(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        $('#participant_notes').animate({ scrollTop: $('#participant_notes').prop('scrollHeight') / parseInt($(element).attr('data-set'))}, 400)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }
}

function load_more_news_articles(element) {
    let div = $(element).get(0);
    console.log(div.scrollTop, div.clientHeight, div.scrollHeight)
    if(div.scrollTop + div.clientHeight >= div.scrollHeight - 5) {
        if($(element).children().last().attr('id') !== 'loading_spinner_more' && $(element).children().last().attr('id') !== 'no-more-news') {
            $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/get_news_articles',
                data: {
                    'set': $(element).attr('data-set'),
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        $(element).children().last().remove()
                        $(element).append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }
}

function load_more_boards(element) {
    let div = $(element).get(0);
    if(div.scrollTop + div.clientHeight >= div.scrollHeight) {
        if($(element).children().last().attr('id') !== 'loading_spinner_more' && $(element).children().last().attr('id') !== 'no-more-boards') {
            $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/load_more_boards',
                data: {
                    'set': $(element).attr('data-set'),
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        $(element).children().last().remove()
                        $(element).append(response['html'])
                        div.scrollTop = div.scrollTop - 100
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }
}


function refresh_jobs() {
    element = document.getElementById('jobs_table')
    if($(element).children().last().attr('id') !== 'loading_spinner_more'){
            $(element).children().remove()
            $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/load_more_jobs',
                data: {
                    'search_id': $(element).attr('search-id'),
                    'order': $(element).attr('ordering'),
                    'set': $(element).attr('data-set')
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        $(element).children().remove()
                        $(element).append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
}}

function refresh_posts() {
    var element = document.getElementById('posts-table-col')
    if($(element).children().last().attr('id') !== 'loading_spinner_more'){
            $(element).children().remove()
            $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/load_more_posts',
                data: {
                    'forum_id': $(element).attr('forum-id'),
                    'order': $(element).attr('ordering'),
                    'set': $(element).attr('data-set'),
                    'style_type': $(element).attr('style-type')
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        $(element).children().remove()
                        $(element).append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
}}

function refresh_comments() {
    var element = document.getElementById('post_full_container')
    var div = document.getElementById('comments_area')
    if($(div).children().last().attr('id') !== 'loading_spinner_more'){
            $(div).children().remove()
            $(div).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/get_comments',
                data: {
                    'post_id': $(element).attr('post-id'),
                    'order': $(element).attr('ordering'),
                    'set': $(element).attr('data-set')
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        $('#loading_spinner_more').remove()
                        $(div).append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
}


function load_more_job_listings(element) {
    let div = $(element).get(0);
    if(div.scrollTop + div.clientHeight >= div.scrollHeight) {
        if($(element).children().last().attr('id') !== 'loading_spinner_more' && $(element).children().last().attr('id') !== 'no-more-jobs') {
            $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/load_more_jobs',
                data: {
                    'search_id': $(element).attr('search-id'),
                    'order': $(element).attr('ordering'),
                    'set': $(element).attr('data-set')
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        $(element).children().last().remove()
                        $(element).append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }
}

$(document).on('click', '#submit_job_search_note', function () {
    var id = $(this).attr('search-id')
    if(check_length_special($('#general_notes'), 0, 500, 'Must be between 1 & 500 characters')){
         $('#loading_modal').modal({backdrop: 'static', keyboard: false})
        $.ajax({
            type: 'POST',
            url: "/post_job_search_note",
            data: { 'q': $('#general_notes').val(), 'search_id': id},
            success: function (response) {
                if(response['status'] === 'success'){
                    if($($('#main_notes').children()[0]).hasClass('no-posts')){
                        $($('#main_notes').children()[0]).remove()
                    }
                    var note_div = $('#main_notes')
                    note_div.prepend(response['html'])
                    $('#general_notes').val('')
                    $('#general_notes_counter').text(parseInt($('#general_notes_counter').text()) + 1)
                    make_moments()
                     $('#loading_modal').modal('hide')
                }else{
                    custom_error_popup(response['message'])
                }

            },
            error: function () {
                error_popup()
            }
        });
    }
})

$(document).on('click', '#new_job_search', function () {
    if($('.job_search_menu_item').length === 3){
        custom_error_popup('You have reached the maximum number of job searches permitted per user. If you are seriously interested in creating more job searches with this account, please reach out to support@ilmjtcv.com')
    }else{
        $('#new_job_search_modal').modal({backdrop: 'static', keyboard: false})
    }
})

function check_industries_jobs(num) {
    if ($('li.selected').length > num || $('li.selected').length === 0){
        $('.searches-industry').each(function () {
            $(this).addClass('incorrect');
        })
        $('.filter-option').addClass('incorrect_text')
        $('.industry-label').addClass('incorrect_text')
        return false
    }else{
        $('.searches-industry').each(function () {
            $(this).removeClass('incorrect');
        })
        $('.filter-option').removeClass('incorrect_text')
        $('.industry-label').removeClass('incorrect_text')
        return true
    }
}

function mark_read(element, option, time) {
                if(element.hasClass('mark-read')){
                    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
                }
                var rows = $('#message_t_' + option).children('tbody')
                for (var i = 0; i < rows.children().length; i++) {
                    if (rows.children()[i].classList.contains('unread')){
                        rows.children()[i].firstElementChild.classList.replace('unread', 'read')
                        rows.children()[i].classList.replace('unread', 'read')
                    }
                }
                $('.' + option.toString() + '_fire_special').remove()
                $('.' + option.toString() + '_fire').css({'color': 'rgba(129, 129, 129, 0.4)'})
                $('.' + option.toString() + '_fire').data({'content': 'Messaged'})
                make_moments()
                update_notification_count()
                if(element.hasClass('mark-read')){
                    element.remove()
                }
                if (option > 0){
                    $.ajax({
                    type: 'POST',
                    url: '/p/update_message_activity',
                    data: {'t': time, 'c': option},
                    success: function () {
                        if(element.hasClass('mark-read')){
                    custom_success_popup('Messages marked as read')
                            make_moments()
                update_notification_count()
                }
                    },
                    error: function () {
                        error_popup()
                    }
                });
            }}

function mark_read_applicant(element) {
                var option  = $(element).attr('applicant-id')
                if(element.hasClass('mark-read')){
                    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
                }
                var rows = $('#message_t_' + option).children('tbody')
                for (var i = 0; i < rows.children().length; i++) {
                    if (rows.children()[i].classList.contains('unread')){
                        rows.children()[i].firstElementChild.classList.replace('unread', 'read')
                        rows.children()[i].classList.replace('unread', 'read')
                    }
                }
                $('.' + option.toString() + '_fire_special').remove()
                $('.' + option.toString() + '_fire').css({'color': 'rgba(129, 129, 129, 0.4)'})
                $('.' + option.toString() + '_fire').data({'content': 'Messaged'})
                make_moments()
                update_notification_count()
                if(element.hasClass('mark-read')){
                    element.remove()
                }
                if (option > 0){
                    $.ajax({
                    type: 'POST',
                    url: '/p/update_message_activity_applicant',
                    data: {'a': option},
                    success: function () {
                        if(element.hasClass('mark-read')){
                    custom_success_popup('Messages marked as read')
                            make_moments()
                update_notification_count()
                }
                    },
                    error: function () {
                        error_popup()
                    }
                });
            }}

function send_candidate_message_new(element, timestamp) {
    var id = element.attr('candidate-id')
    if (check_length_special($('#message_' + id.toString()), 0, 140, 'Must be between 1 and 140 characters')) {
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
            type: 'POST',
            url: '/p/send_candidate_message',
            data: {'q': $('#message_' + id.toString()).val(), 'a': id, 't': timestamp},
            success: function (response) {
                if (response['status'] === 'success') {
                    if($('#candidate_badges_' + id.toString()).find('i.fab').length === 0){
                        $('#candidate_badges_' + id.toString()).prepend('<i class="fab fa-facebook-messenger ' + id.toString() + '_fire" style="width: 25px; float:right;text-align: right; color: rgba(129, 129, 129, 0.4); margin-right: 5px; display: block; font-size: 25px; position:relative;" data-toggle="popover" data-placement="left" data-content="Messaged"></i>')
                        update_notification_count()
                    }
                    custom_success_popup('Message Sent')
                    $('#message_container_' + id.toString()).html(response['html'])
                    $('#message_container_' + id.toString()).attr('data-set', '1')
                    $('#message_container_' + id.toString()).animate({ scrollTop: $('#message_container_' + id.toString()).prop("scrollHeight")}, 1000)
                    $('#message_' + id.toString()).val('')
                    $('#messages_counter_' + id.toString()).text(parseInt($('#messages_counter_' + id.toString()).text()) + 1)
                    mark_read($('#loading_modal'), id, timestamp)
                    make_moments()
                } else {
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                error_popup()
            }
        });
    }
}

function send_applicant_message_new(element) {
    var id = element.attr('applicant-id')
    if (check_length_special($('#message_' + id.toString()), 0, 140, 'Must be between 1 and 140 characters')) {
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
            type: 'POST',
            url: '/p/send_applicant_message',
            data: {'q': $('#message_' + id.toString()).val(), 'a': id},
            success: function (response) {
                if (response['status'] === 'success') {
                    if($('#applicant_badges_' + id.toString()).find('i.fab').length === 0){
                        $('#applicant_badges_' + id.toString()).prepend('<i class="fab fa-facebook-messenger ' + id.toString() + '_fire" style="width: 25px; float:right;text-align: right; color: rgba(129, 129, 129, 0.4); margin-right: 5px; display: block; font-size: 25px; position:relative;" data-toggle="popover" data-placement="left" data-content="Messaged"></i>')
                        update_notification_count()
                    }
                    custom_success_popup('Message Sent')
                    $('#message_container_' + id.toString()).html(response['html'])
                    $('#message_container_' + id.toString()).attr('data-set', '1')
                    $('#message_container_' + id.toString()).animate({ scrollTop: $('#message_container_' + id.toString()).prop("scrollHeight")}, 1000)
                    $('#message_' + id.toString()).val('')
                    $('#messages_counter_' + id.toString()).text(parseInt($('#messages_counter_' + id.toString()).text()) + 1)
                    make_moments()
                    mark_read_applicant($('#loading_modal'), id)
                } else {
                    custom_error_popup(response['message'])
                }
            },
            error: function () {
                error_popup()
            }
        });
    }
}

$(document).on('blur', '.searches-industry', function () {
check_industries_jobs(2)
});

//
$(document).on('click', '#submit_new_job_search', function () {
var title = check_length_special($('#search_title'), 0, 80, 'Must be between 0 and 80 characters')
var city = check_length_special($('#search_city'), 0, 80, 'Must be a valid city')
var industries = check_industries_jobs(2)
var data = {'t': $('#search_title').val(), 'd':$('#search_description').val(), 'industries': $('#search_industries').val(),
'l':$('#search_l_specific').is(':checked'), 'c':$('#search_city').val(), 'p':$('#search_proximity').val()};
if($('#search_l_specific').is(':checked')){
if(title && city && industries){
 $('#loading_modal').modal({backdrop: 'static', keyboard: false});
 $.ajax({
type: 'POST',
url: '/add_job_search',
data: data,
success: function (response) {
 if(response['status'] === 'success'){
     document.location = '/job_search/' + response['id']
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
if(title && industries){
 $('#loading_modal').modal({backdrop: 'static', keyboard: false});
 $.ajax({
type: 'POST',
url: '/add_job_search',
data: data,
success: function (response) {
 if(response['status'] === 'success'){
     document.location = '/job_search/' + response['id']
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

})

// Location Specific Checkbox toggle of Saved Job Search
$(document).on('change click', '#jobs_checkbox', function () {
if ($('#search_l_specific').is(':checked')){
$('#l_specific_true').css({'display':'block'})
}else{
$('#l_specific_true').css({'display':'none'});
$('#city').val('')
}
})

$(document).on('change click', '#jobs_checkbox_edit', function () {
if ($('#search_l_specific_edit').is(':checked')){
$('#l_specific_true_edit').css({'display':'block'})
}else{
$('#l_specific_true_edit').css({'display':'none'});
$('#city_edit').val('')
}
})

// Google Maps Cities API for City of Job Saved Search
$(document).ready(function () {
    var city_autocomplete_jobs;
    city_autocomplete_jobs = new google.maps.places.Autocomplete((document.getElementById('search_city')), {
        types: ['(cities)'],
    })
});

$(document).ready(function () {
var city_autocomplete_jobs_edit;
city_autocomplete_jobs_edit = new google.maps.places.Autocomplete((document.getElementById('search_city_edit')), {
types: ['(cities)'],
});

google.maps.event.addListener(city_autocomplete_jobs_edit, 'place_changed', function () {
var near_place = city_autocomplete_jobs_edit.getPlace();
});
});

$(document).on('hidden.bs.modal', '#custom_message', function () {
    $('#submit_custom_message').attr('job-id', '')
    $('#custom_message_job').val('')

})
// CLose job specific Modal
$(document).on('hidden.bs.modal', '#job_modal', function () {
$('#job_title').text('')
$('#job_order').html('')
$('#job_company').text('')
$('#job_location').text('')
$('#job_description').text('')
$('#job_found').text('')
$('#submit_job_note').attr('job-id', 0)
$('#job_apply_btn').attr('job-id', 0)
    $('#quick_apply_btn').attr('job-id', 0)
$('#remove_quick_apply_btn').attr('job-id', 0)
$('#note_loading').css({'display': 'block'})
$('#job_listing_note_row').css({'display': 'none'})
$('#job_badges_window').text('')
$('#job_badges_window').attr('option', 0)
    $('#ilm-exclusive-main').css({'display':'none'})
            $('#job_quick_apply_main').css({'display':'none'})
    $('#job_applied_main').css({'display':'none'})
    $('#job_viewed_main').css({'display':'none'})
    $('#job_apply_btn').css({'display':'block'})
        $('#quick_apply_btn').css({'display':'none'})
    $('#quick_apply_btn').html('Quick Apply! <i class="fas fa-bolt"></i>')
    $('#remove_quick_apply_btn').css({'display':'none'})
    $('#remove_quick_apply_btn').html('Withdraw Application :(')
    $('#job_info_quick').css({'display': 'none'})
    $('#job_employment').text('')
    $('#job_compensation').text('')
    $('#job_pitch').text('')

});


$(document).on('click', '.jobs-card', function () {
    $('#job_modal').modal({backdrop: 'static', keyboard: false})
    var id = $(this).attr('job-id').toString()
    var completed = $(this).attr('completed').toString()
    var ilm = $(this).attr('ilm').toString()
    var quick = $(this).attr('quick').toString()
    var element = $(this)
    $('#job_title').text($('#title_' + id).text())
    $('#job_order').html($('#order_' + id).html())
    $('#job_company').text($('#company_' + id).text())
    $('#job_location').text($('#location_' + id).text())
    $('#job_description').text($('#snippet_' + id).text())
    $('#job_found').text($('#found_' + id).text())
    $('#submit_job_note').attr('job-id', id)
    $('#job_apply_btn').attr('job-id', id)
    $('#quick_apply_btn').attr('job-id', id)
    $('#remove_quick_apply_btn').attr('job-id', id)
    if(completed === '0'){
        $('#job_badges_window').css({'display':'inline-block'})
        $('#job_badges_window').text('Remove job listing from feed')
        $('#job_badges_window').attr('option', -1)
    }else if(completed === '1'){
        if(quick === '0'){
            $('#job_badges_window').css({'display':'inline-block'})
        $('#job_badges_window').text('Mark job as applied')
        $('#job_badges_window').attr('option', 2)
        }
        $('#job_viewed_main').css({'display':'inline-block'})
    }else if(completed == '2'){
        $('#job_badges_window').css({'display':'none'})
        $('#job_applied_main').css({'display':'inline-block'})
    }
    if(ilm === '1'){
        $('#ilm-exclusive-main').css({'display':'inline-block'})
    }
    if(quick === '1'){
            $('#job_badges_window').css({'display':'none'})
            $('#job_quick_apply_main').css({'display':'inline-block'})
            $('#job_apply_btn').css({'display':'none'})
            $('#job_info_quick').css({'display': 'block'})
            $('#job_employment').text($('#employment_' + id).text())
            $('#job_compensation').text($('#compensation_' + id).text())
            $('#job_pitch').html('<b>Why work at ' + $('#company_' + id).text().toString() + '?</b> -- ' + $('#pitch_' + id).text())
        if(completed === '2'){
                    $('#job_badges_window').css({'display':'none'})

            $('#remove_quick_apply_btn').css({'display':'block'})
        }else if(completed === '0'){
        $('#quick_apply_btn').css({'display':'block'})
            $.ajax({
                type: 'POST',
                url: '/mark_quick_job_viewed',
                data: {'id': id},
                success: function (response) {
                if(response['status'] === 'success'){
                    $('#job_viewed_main').css({'display':'inline-block'})
                    element.attr('completed', 1)
                    $($('#badges_' + id).children()[0]).append('<li>\n' +
                        '                        <i class="fas fa-binoculars" data-toggle="popover" data-placement="bottom" data-content="You have viewed this job application" style="color: #efe84db5;" aria-hidden="true" data-original-title="" title=""></i>\n' +
                        '                    </li>')
                }else{
                    error_popup()
                }
                },
                error: function () {
                error_popup()
                }
                })
        }else if(completed === '1'){
            $('#quick_apply_btn').css({'display':'block'})
        }
    }
        $.ajax({
        type: 'GET',
        url: '/get_job_listing_data',
        data: {'id': id},
        success: function (response) {
        if(response['status'] === 'success'){
            $('#job_notes_counter').text(response['note_count'])
            $('#job_notes_container').html(response['html'])
            $('#note_loading').css({'display': 'none'})
            $('#job_listing_note_row').css({'display': 'block'})
            make_moments()
        }
        },
        error: function () {
        error_popup()
        }
        })
});

$(document).on('click', '#submit_job_note', function () {
if(check_length_special($('#job_notes_pad'), 0, 500, 'Must be between 1 & 500 characters')){
var id = $(this).attr('job-id')
    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
$.ajax({
type: 'POST',
url: '/post_job_note',
data: {'q': $('#job_notes_pad').val(), 'a': id},
success: function (response) {
if(response['status'] === 'success'){
    if($($('#job_notes_container').children()[0]).hasClass('no-posts')){
            $($('#job_notes_container').children()[0]).remove()
    }
    var note_div = $('#job_notes_container')
    note_div.prepend(response['html']);
    $('#job_notes_pad').val('')
   $('#job_notes_counter').text(parseInt($('#job_notes_counter').text()) + 1)
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

})

$(document).on('click', '#job_apply_btn', function () {
var id = $(this).attr('job-id').toString()
window.open('/open_job_application/' + id,  '_blank')
setTimeout(function () {
        $('#job_modal').modal('hide')
                    $('.job-dropdown-item').each(function () {
                    if($(this).hasClass('active')){
                        $(this).removeClass('active')
                    }
                    })
                    $('.job-dropdown-item[ordering=' + '1' +']').addClass('active')
                    $('#jobs_table').attr('ordering', 1)
                    $('#jobs_table').attr('data-set', 0)
                    $('#job_filtering').html('Viewed' + ' <span class="caret"></span>')
                    refresh_jobs()
}, 2000)
})

$(document).on('click', '.job-dropdown-item', function () {
$('.job-dropdown-item').each(function () {
if($(this).hasClass('active')){
$(this).removeClass('active')
}
})
$(this).addClass('active')
$('#jobs_table').attr('ordering', $(this).attr('ordering'))
$('#jobs_table').attr('data-set', 0)
$('#job_filtering').html($(this).text() + ' <span class="caret"></span>')
refresh_jobs()
})

$(document).on('click', '#job_badges_window', function () {
var option = $(this).attr('option').toString()
var id = $('#job_apply_btn').attr('job-id').toString()
if(option === '-1'){
var v = confirm('Are you sure you would like to remove this job listing from your feed? It will be permenantly gone.')
}else if(option === '2'){
var v = confirm('Are you sure you would like to mark this job as applied?')
}
if(v){

$.ajax({
type:'POST',
url:'/edit_job_activity',
data: {'id':id, 'option': option},
success: function (response) {
    if(response['status'] === 'success'){
        if(option === '-1'){
            $('#job_modal').modal('hide')
            $('div.jobs-card[job-id="' + id +'"]').remove()
            $('#jobs_counter').text(parseInt($('#jobs_counter').text()) - 1)
        }else{
            $('#job_modal').modal('hide')
            $('.job-dropdown-item').each(function () {
            if($(this).hasClass('active')){
                $(this).removeClass('active')
            }
            })
            $('.job-dropdown-item[ordering=' + '2' +']').addClass('active')
            $('#jobs_table').attr('ordering', 2)
            $('#jobs_table').attr('data-set', 0)
            $('#job_filtering').html('Applied' + ' <span class="caret"></span>')
            refresh_jobs()
        }
    }else{
        error_popup()
    }
},
error: function () {
    error_popup()
}
})
}
})

function isURL(str) {
   regexp =  /^(?:(?:https?|ftp):\/\/)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:\/\S*)?$/;
  return regexp.test(str);
}

$(document).on('click', '#submit_custom_message', function () {
    if(check_length_special($('#custom_message_job'), -1, 500, 'Must be less than 500 characters')){
        var element = $(this)
    var id = element.attr('job-id')
    var btn = $('#quick_apply_btn[job-id="' + id + '"]')
    $('#custom_message').modal('toggle');
    btn.html('<div class="loadingio-spinner-spinner-5m5wfwkhl3a"><div class="ldio-fxcp7ev3c">\n' +
        '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '</div></div>')
    $.ajax({
            type: 'POST',
            url: '/submit_quick_apply',
            data: {'id': id, 'custom_message': $('#custom_message_job').val()},
            success: function (response) {
                if(response['status'] === 'success'){
                    $('#job_modal').modal('hide')
                    $('.job-dropdown-item').each(function () {
                    if($(this).hasClass('active')){
                        $(this).removeClass('active')
                    }
                    })
                    $('.job-dropdown-item[ordering=' + '2' +']').addClass('active')
                    $('#jobs_table').attr('ordering', 2)
                    $('#jobs_table').attr('data-set', 0)
                    $('#job_filtering').html('Applied' + ' <span class="caret"></span>')
                    refresh_jobs()
                    custom_success_popup(response['message'])
                }else{
                    custom_error_popup(response['message'])
                    setTimeout(function () {
                            document.location.pathname = response['url']
                    }, 5000)
                }
            }
        })
    }
})

$(document).on('click', '#quick_apply_btn', function () {
        var element = $(this)
        var id = element.attr('job-id')
        $('#submit_custom_message').attr('job-id', id)
        $('#custom_message').modal({keyboard: false});
})

$(document).on('click', '#remove_quick_apply_btn', function () {
    var element = $(this)
    var id = element.attr('job-id')
    element.html('<div class="loadingio-spinner-spinner-5m5wfwkhl3a"><div class="ldio-fxcp7ev3c">\n' +
        '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '</div></div>')
        $.ajax({
            type: 'POST',
            url: '/remove_quick_apply',
            data: {'id': id},
            success: function (response) {
                if(response['status'] === 'success'){
                    $('#job_modal').modal('hide')
                    $('.job-dropdown-item').each(function () {
                    if($(this).hasClass('active')){
                        $(this).removeClass('active')
                    }
                    })
                    $('.job-dropdown-item[ordering=' + '2' +']').addClass('active')
                    $('#jobs_table').attr('ordering', 1)
                    $('#jobs_table').attr('data-set', 0)
                    $('#job_filtering').html('Applied' + ' <span class="caret"></span>')
                    refresh_jobs()
                    custom_success_popup(response['message'])
                }
            }

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

$(document).ready(function () {
    $('.money_convert').each(function () {
        $(this).text('$' + formatNumber($(this).text()).toString())
    })
})

$(document).on('submit', '#img_upload_form', function (e) {
    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
    var formData = new FormData(this);
    var url = $(this).attr('action')
    e.preventDefault()
    $.ajax({
        type: 'POST',
        url: url,
        data: formData,
        contentType: false,
        processData: false,
        cache: false,
        success: function (response) {
            if(response['status'] === 'success'){
                document.location.reload(true)
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
})

$(document).on('click', '.delete_personal_img', function () {
    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
    $.ajax({
        type: 'GET',
        url: '/delete_profile_images',
        success: function (response) {
            if(response['status'] === 'success'){
                document.location.reload(true)
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
})

  var overlay= document.getElementById('overlay');

$(document).on('click', '#overlay', function () {
   $(this).css({'display':'none'})
    var video=document.getElementById("explainer");
    video.muted = !video.muted;
    if($('#explainer').get(0).paused){
        $('#explainer').get(0).play()
    }
})

function set_muted(element) {
    if($(element).prop('volume') === 0){
        $('#overlay').css({'display':'block'})
    }else{
        $('#overlay').css({'display':'none'})
    }
}

function getSearchParams(k){
     var p={};
     location.search.replace(/[?&]+([^=&]+)=([^&]*)/gi,function(s,k,v){p[k]=v})
     return k?p[k]:p;
}


$(document).on('click', '.comment-filtering-item', function () {
    $('.comment-filtering-item').each(function () {
    if($(this).hasClass('active')){
    $(this).removeClass('active')
    }
    })
    $(this).addClass('active')
    $('#post_full_container').attr('ordering', $(this).attr('ordering'))
    $('#post_full_container').attr('data-set', 0)
    $('#post_filtering_btn').html( $(this).text() + ' <span class="caret"></span>')
    refresh_comments()
})

$(document).on('click', '.post-filtering-item', function () {
    $('.post-filtering-item').each(function () {
    if($(this).hasClass('active')){
    $(this).removeClass('active')
    }
    })
    $(this).addClass('active')
    $('#posts-table-col').attr('ordering', $(this).attr('ordering'))
    $('#posts-table-col').attr('data-set', 0)
    $('#post_filtering_btn').html( '<span class="caret"></span> ' + $(this).text() )
    refresh_posts()
})

$(document).on('click', '.main_navbar_tab', function () {
    var element = this
    $('.open').each(function () {
        if(element !== this){
            $(this).removeClass('open')
        }
    })
    $('.fa-caret-right').each(function () {
        if(element !== this){
            $(this).removeClass('fa-caret-right')
            $(this).addClass('fa-caret-down')
        }
    })
    if($(this).hasClass('open')){
        $(this).removeClass('open')
        $($(this).children()[0]).removeClass('fa-caret-right')
        $($(this).children()[0]).addClass('fa-caret-down')
    }else{
        $(this).addClass('open')
        $($(this).children()[0]).addClass('fa-caret-right')
        $($(this).children()[0]).removeClass('fa-caret-down')    }
 $('.main_navbar_tab').each(function () {
     if($(this).hasClass('open')){
         $(this).next().css({'display': 'block'})
     }else{
         $(this).next().css({'display': 'none'})
     }
 })
})

$(document).on('hidden.bs.modal', '#edit_note_modal', function () {
    $('#note_job_delete').attr('note-id', '')
    $('#note_job_delete').attr('note-type', '')
    $('#note_text_edit').val('')
    $('#edit_job_note_submit').attr('note-id', '')
    $('#edit_job_note_submit').attr('note-type', '')
})

$(document).on('click', '.job-ss-note-edit', function () {
    var id = $(this).attr('job-note-id')
    $('#note_job_delete').attr('note-id', id.toString())
    $('#note_job_delete').attr('note-type', 0)
    $('#note_text_edit').val($('.note_text[job-note-id="' + id.toString() + '"]').text())
    $('#edit_job_note_submit').attr('note-id', id.toString())
    $('#edit_job_note_submit').attr('note-type', 0)
    $('#edit_note_modal').modal({backdrop: 'static', keyboard: false})
})

$(document).on('click', '.job-listing-note-edit', function () {
    var id = $(this).attr('listing-note-id')
    $('#note_job_delete').attr('note-id', id.toString())
    $('#note_job_delete').attr('note-type', 1)
    $('#note_text_edit').val($('.note_text[listing-note-id="' + id.toString() + '"]').text())
    $('#edit_job_note_submit').attr('note-id', id.toString())
    $('#edit_job_note_submit').attr('note-type', 1)
    $('#edit_note_modal').modal({backdrop: 'static', keyboard: false})
})

$(document).on('click', '#edit_job_note_submit', function () {
    if(check_length_special($('#note_text_edit'), 0, 500, 'Must be between 0 & 500 characters')){
        var id = $(this).attr('note-id')
    var text = $('#note_text_edit').val()
    var url = ''
    if($(this).attr('note-type').toString() === '0'){
        url = '/edit_job_ss_note'
        var element =  $('.note_text[job-note-id="' + id.toString() + '"]')
    }else if($(this).attr('note-type').toString() === '1'){
        url = '/edit_job_listing_note'
        var element =  $('.note_text[listing-note-id="' + id.toString() + '"]')
    }
   element.text(text)
    $('#edit_note_modal').modal('hide')
    $.ajax({
        type: 'POST',
        url: url,
        data: {'a': id, 'q': text},
        success: function(response){
            if(response['status'] !== 'success'){
                custom_error_popup('Your changes could not be saved. Please reload the page and try again.')
            }
        },
        error: function () {
            custom_error_popup('Your changes could not be saved. Please reload the page and try again.')
        }
    })
    }
})

$(document).on('click', '#note_job_delete', function () {
    var a = confirm('Are you sure you would like to delete this note? It will be permanently unavailable.')
    if(a){
        var id = $(this).attr('note-id')
        var url = ''
        if($(this).attr('note-type').toString() === '0'){
            url = '/del_job_ss_note'
            var element =  $('.note[job-note-id="' + id.toString() + '"]')
            $('#general_notes_counter').text(parseInt($('#general_notes_counter').text()) - 1)
        }else if($(this).attr('note-type').toString() === '1'){
            url = '/del_job_listing_note'
            var element =  $('.note[listing-note-id="' + id.toString() + '"]')
           $('#job_notes_counter').text(parseInt($('#job_notes_counter').text()) - 1)
        }
        element.css({'display':'none'})
        $('#edit_note_modal').modal('hide')
        $.ajax({
            type: 'POST',
            url: url,
            data: {'a': id},
            success: function (response) {
                if (response['status'] === 'success') {
                    if(element.parent().children().length === 1){
                        element.parent().append('<h5 class="no-posts">Your notes will appear here</h5>')
                    }
                    element.remove()
                }else{
                    element.css({'display':'block'})
                    custom_error_popup('Your changes could not be saved. Please reload the page and try again.')
                }
            },
            error: function () {
                element.css({'display':'block'})
                custom_error_popup('Your changes could not be saved. Please reload the page and try again.')
            }
        })
    }
})


$(document).on('click', '.candidate-note-edit', function () {
    var id = $(this).attr('candidate-note-id')
    $('#note_search_delete').attr('note-id', id.toString())
    $('#note_search_delete').attr('note-type', 1)
    $('#note_text_edit').val($('.note_text[candidate-note-id="' + id.toString() + '"]').text())
    $('#edit_search_note_submit').attr('note-id', id.toString())
    $('#edit_search_note_submit').attr('note-type', 1)
    $('#edit_note_modal').modal({backdrop: 'static', keyboard: false})
})


$(document).on('click', '.ss-note-edit', function () {
    var id = $(this).attr('ss-note-id')
    $('#note_search_delete').attr('note-id', id.toString())
    $('#note_search_delete').attr('note-type', 0)
    $('#note_text_edit').val($('.note_text[ss-note-id="' + id.toString() + '"]').text())
    $('#edit_search_note_submit').attr('note-id', id.toString())
    $('#edit_search_note_submit').attr('note-type', 0)
    $('#edit_note_modal').modal({backdrop: 'static', keyboard: false})
})


$(document).on('click', '#edit_search_note_submit', function () {
    if(check_length_special($('#note_text_edit'), 0, 500, 'Must be between 0 & 500 characters')){
        var id = $(this).attr('note-id')
    var text = $('#note_text_edit').val()
    var url = ''
    if($(this).attr('note-type').toString() === '0'){
        url = '/p/edit_ss_note'
        var element =  $('.note_text[ss-note-id="' + id.toString() + '"]')
    }else if($(this).attr('note-type').toString() === '1'){
        url = '/p/edit_candidate_note'
        var element =  $('.note_text[candidate-note-id="' + id.toString() + '"]')
    }
    element.text(text)
    $('#edit_note_modal').modal('hide')
    $.ajax({
        type: 'POST',
        url: url,
        data: {'a': id, 'q': text},
        success: function(response){
            if(response['status'] !== 'success'){
                custom_error_popup('Your changes could not be saved. Please reload the page and try again.')
            }
        },
        error: function () {
            custom_error_popup('Your changes could not be saved. Please reload the page and try again.')
        }
    })
    }
})


$(document).on('click', '#note_search_delete', function () {
    var a = confirm('Are you sure you would like to delete this note? It will be permanently unavailable.')
    if(a){
        var id = $(this).attr('note-id')
        var url = ''
        if($(this).attr('note-type').toString() === '0'){
            url = '/p/del_ss_note'
            var element =  $('.note[ss-note-id="' + id.toString() + '"]')
            $('#general_notes_counter').html(parseInt($('#general_notes_counter').text()) - 1)
        }else if($(this).attr('note-type').toString() === '1'){
            url = '/p/del_candidate_note'
            var element =  $('.note[candidate-note-id="' + id.toString() + '"]')
            $('#notes_counter_' + id.toString()).text(parseInt($('#notes_counter_' + id.toString()).text()) - 1)
        }
        element.css({'display':'none'})
        $('#edit_note_modal').modal('hide')
        $.ajax({
            type: 'POST',
            url: url,
            data: {'a': id},
            success: function (response) {
                if (response['status'] === 'success') {
                    if(element.parent().children().length === 1){
                        element.parent().append('<h5 class="no-posts">Recruiter notes will appear here</h5>')
                    }
                    element.remove()
                }else{
                    element.css({'display':'block'})
                    custom_error_popup('Your changes could not be saved. Please reload the page and try again.')
                }
            },
            error: function () {
                element.css({'display':'block'})
                custom_error_popup('Your changes could not be saved. Please reload the page and try again.')
            }
        })
    }
})


$(document).on('click', '.applicant-note-edit', function () {
    var id = $(this).attr('applicant-note-id')
    $('#note_posting_delete').attr('note-id', id.toString())
    $('#note_posting_delete').attr('note-type', 1)
    $('#note_text_edit').val($('.note_text[applicant-note-id="' + id.toString() + '"]').text())
    $('#edit_posting_note_submit').attr('note-id', id.toString())
    $('#edit_posting_note_submit').attr('note-type', 1)
    $('#edit_note_modal').modal({backdrop: 'static', keyboard: false})
})


$(document).on('click', '.posting-note-edit', function () {
    var id = $(this).attr('posting-note-id')
    $('#note_posting_delete').attr('note-id', id.toString())
    $('#note_posting_delete').attr('note-type', 0)
    $('#note_text_edit').val($('.note_text[posting-note-id="' + id.toString() + '"]').text())
    $('#edit_posting_note_submit').attr('note-id', id.toString())
    $('#edit_posting_note_submit').attr('note-type', 0)
    $('#edit_note_modal').modal({backdrop: 'static', keyboard: false})
})

$(document).on('click', '#edit_posting_note_submit', function () {
    if(check_length_special($('#note_text_edit'), 0, 500, 'Must be between 0 & 500 characters')){
        var id = $(this).attr('note-id')
    var text = $('#note_text_edit').val()
    var url = ''
    if($(this).attr('note-type').toString() === '0'){
        url = '/p/edit_job_note'
        var element =  $('.note_text[posting-note-id="' + id.toString() + '"]')
    }else if($(this).attr('note-type').toString() === '1'){
        url = '/p/edit_applicant_note'
        var element =  $('.note_text[applicant-note-id="' + id.toString() + '"]')
    }
    element.text(text)
    $('#edit_note_modal').modal('hide')
    $.ajax({
        type: 'POST',
        url: url,
        data: {'a': id, 'q': text},
        success: function(response){
            if(response['status'] !== 'success'){
                custom_error_popup('Your changes could not be saved. Please reload the page and try again.')
            }
        },
        error: function () {
            custom_error_popup('Your changes could not be saved. Please reload the page and try again.')
        }
    })
    }
})


$(document).on('click', '#note_posting_delete', function () {
    var a = confirm('Are you sure you would like to delete this note? It will be permanently unavailable.')
    if(a){
        console.log($(this).attr('note-type'))
        var id = $(this).attr('note-id')
        var url = ''
        if($(this).attr('note-type').toString() === '0'){
            url = '/p/del_job_note'
            var element =  $('.note[posting-note-id="' + id.toString() + '"]')
            $('#general_notes_counter').html(parseInt($('#general_notes_counter').text()) - 1)
        }else if($(this).attr('note-type').toString() === '1'){
            url = '/p/del_applicant_note'
            var element =  $('.note[applicant-note-id="' + id.toString() + '"]')
            $('#notes_counter_' + id.toString()).text(parseInt($('#notes_counter_' + id.toString()).text()) - 1)
        }
        element.css({'display':'none'})
        $('#edit_note_modal').modal('hide')
        $.ajax({
            type: 'POST',
            url: url,
            data: {'a': id},
            success: function (response) {
                if (response['status'] === 'success') {
                    if(element.parent().children().length === 1){
                        element.parent().append('<h5 class="no-posts">Recruiter notes will appear here</h5>')
                    }
                    element.remove()
                }else{
                    element.css({'display':'block'})
                    custom_error_popup('Your changes could not be saved. Please reload the page and try again.')
                }
            },
            error: function () {
                element.css({'display':'block'})
                custom_error_popup('Your changes could not be saved. Please reload the page and try again.')
            }
        })
    }
})

function refresh_candidates(){
    element = document.getElementById('sortable')
    if($(element).children().last().attr('id') !== 'loading_spinner_more'){
            $(element).children().remove()
            $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/p/load_more_candidates',
                data: {
                    'search_id': $(element).attr('search-id'),
                    'order': $(element).attr('ordering'),
                    'set': $(element).attr('data-set')
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        if($(element).attr('ordering') === '0'){
                            $('#sortable').sortable("enable")
                        }else{
                            $('#sortable').sortable("disable")
                        }

                        $(element).children().remove()
                        $(element).append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
}}

function refresh_applicants(){
    element = document.getElementById('sortable1')
    if($(element).children().last().attr('id') !== 'loading_spinner_more'){
            $(element).children().remove()
            $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/p/load_more_applicants',
                data: {
                    'job_id': $(element).attr('job-id'),
                    'order': $(element).attr('ordering'),
                    'set': $(element).attr('data-set')
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        if($(element).attr('ordering') === '0'){
                            $('#sortable1').sortable("enable")
                        }else{
                            $('#sortable1').sortable("disable")
                        }

                        $(element).children().remove()
                        $(element).append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
}}


$(document).on('click', '.candidate-dropdown-item', function () {
$('.candidate-dropdown-item').each(function () {
if($(this).hasClass('active')){
$(this).removeClass('active')
}
})
$(this).addClass('active')
$('#sortable').attr('ordering', $(this).attr('ordering'))
$('#sortable').attr('data-set', 0)
$('#candidate_filtering').html($(this).text() + ' <span class="caret"></span>')
refresh_candidates()
})

$(document).on('click', '.applicant-dropdown-item', function () {
$('.applicant-dropdown-item').each(function () {
if($(this).hasClass('active')){
$(this).removeClass('active')
}
})
$(this).addClass('active')
$('#sortable1').attr('ordering', $(this).attr('ordering'))
$('#sortable1').attr('data-set', 0)
$('#applicant_filtering').html($(this).text() + ' <span class="caret"></span>')
refresh_applicants()
})

$(document).on('click', '#edit_job_search_toggle', function () {
    $('#edit_job_search_modal').modal({backdrop: 'static', keyboard: false});
})

// window.addEventListener('DOMContentLoaded', () => {
//
// 	const observer = new IntersectionObserver(entries => {
// 		entries.forEach(entry => {
// 			const id = entry.target.getAttribute('id');
// 			if (entry.intersectionRatio > 0) {
// 				document.querySelector(`nav li a[href="#${id}"]`).parentElement.classList.add('active');
// 			} else {
// 				document.querySelector(`nav li a[href="#${id}"]`).parentElement.classList.remove('active');
// 			}
// 		});
// 	});
//
// 	// Track all sections that have an `id` applied
// 	document.querySelectorAll('section[id]').forEach((section) => {
// 		observer.observe(section);
// 	});
//
// });


$(document).on('click', '#edit_job_search_submit', function () {
    var id = $(this).attr('search-id')
    var title = check_length_special($('#search_title_edit'), 0, 80, 'Must be between 0 and 80 characters')
    var city = check_length_special($('#search_city_edit'), 0, 80, 'Must be a valid city')
    var industries = check_industries_jobs(2)
    var data = {'t': $('#search_title_edit').val(), 'd':$('#search_description_edit').val(), 'industries': $('#search_industries_edit').val(),
                'l':$('#search_l_specific_edit').is(':checked'), 'c':$('#search_city_edit').val(), 'p':$('#search_proximity_edit').val(), 'id': id.toString()}
    if($('#search_l_specific_edit').is(':checked')){
        if(title && city && industries){
            $('#loading_modal').modal({backdrop: 'static', keyboard: false});
            $.ajax({
                type: 'POST',
                url: '/edit_job_search',
                data: data,
                success: function (response) {
                     if(response['status'] === 'success'){
                         document.location = '/job_search/' + response['id']
                     }else{
                         custom_error_popup(response['message'])
                     }
                },
                error: function () {
                    error_popup()
                }
            });
        } }
    else{
        if(title && industries){
            $('#loading_modal').modal({backdrop: 'static', keyboard: false});
            $.ajax({
                type: 'POST',
                url: '/edit_job_search',
                data: data,
                success: function (response) {
                 if(response['status'] === 'success'){
                     document.location = '/job_search/' + response['id']
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

})

$(document).on('click', '#deactivate_job_search', function () {
    var id = $(this).attr('search-id')
    var a = confirm('Are you sure you would like to de-activate this Job Search? You will no longer receive updates about it.')
    if(a){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
        type: 'POST',
        url: '/deactivate_job_search',
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


$(document).on('click', '#delete_job_search', function () {
    var id = $(this).attr('search-id')
    var row = $('.terminated_search_row[search-id="' + id.toString() + '"]')
    var a = confirm('Are you sure you would like to delete this Job Search? It will be permanently removed.')
    if(a){
        row.html('\'<div class="loadingio-spinner-spinner-5m5wfwkhl3a" style="text-align: center; margin: auto; display: block"><div class="ldio-fxcp7ev3c">\\n\' +\n' +
            '        \'<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\\n\' +\n' +
            '        \'</div></div>')
        $.ajax({
            type: 'POST',
            url: '/delete_job_search',
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

$(document).on('click', '#reactivate_job_search', function () {
    var id = $(this).attr('search-id')
    var a = confirm('Are you sure you would like to reactivate this Job Search?')
    if(a){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $('#loading_text').text('This may take a minute...')
        $('#deactivated_searches_modal').modal('hide')
        $.ajax({
            type: 'POST',
            url: '/reactivate_job_search',
            data: {'id': id.toString()},
            success: function (response) {
                if(response['status'] === 'success'){
                    document.location.pathname = '/job_search/' + id
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

$(document).on('keypress change keydown keyup', '#send_message_text', function () {
    if($(this).val().length > 0){
        $('#submit_msg').removeClass('disabled');
        $('#submit_msg').removeAttr('disabled');
    }else{
        $('#submit_msg').addClass('disabled');
        $('#submit_msg').attr('disabled', 'disabled');
    }
})

$(document).on('click', '#submit_msg', function () {
    var id = $(this).attr('board-id')
    var element = $(this)
    var m = $('#send_message_text')
    if(check_length_special(m, 0, 140, 'Message must be between 0 & 140 characters')){
        $(this).before('<div class="loadingio-spinner-spinner-8kccqdvo9i"><div class="ldio-tnvxe4xu369">\n' +
            '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
            '</div></div>')
        $.ajax({
            type: 'POST',
            url: '/send_message',
            data: {'a': id, 'q': m.val()},
            success: function (response) {
                if(response['status'] === 'success'){
                    element.prev().remove()
                    element.blur()
                    element.attr('disabled')
                    element.addClass('disabled')
                    m.val('')
                    $('#messages_container').html(response['html'])
                    $('#message_boards_col').html(response['html_boards'])
                    $('#message_boards_col').attr('data-set', '1')
                    $('#message_boards_col').animate({ scrollTop: 0}, 500);
                    $('#messages_container').attr('data-set', '1')
                    $("#messages_container").animate({ scrollTop: $('#messages_container').prop("scrollHeight")}, 500);
                    make_moments()
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

$(document).on('click', '#new_message_toggle', function () {
    $('#new_message_modal').modal({backdrop: 'static', keyboard: false})
})

// $(document).on('change keyup keydown keypress', '.select2-search__field', function () {
//     var q = $(this).val()
//     $.ajax({
//         type: 'GET',
//         url: '/get_user_options',
//         success: function (response) {
//             if(response['status'] === 'success'){
//                 console.log(response['options'])
//             }else{
//                 custom_error_popup(response['message'])
//             }
//         }
//     })
// })

$(document).on('hidden.bs.modal', '#edit_area_category', function () {
    $('#save_options_btn').attr('option', '0')
    $('#save_options_btn').text('Save')
    $('#edit_area_label').text('')
    $('#options_area').html('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
        '                                        <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '                                        </div></div></div></div></div>')
})

$(document).on('click', '#hobbies_edit', function () {
    $('#edit_area_label').text('Hobbies')
    $('#edit_area_category').modal({backdrop: 'static', keyboard: false})
    $.ajax({
        type: 'GET',
        url: '/get_profile_info_options/1',
        success: function (response) {
            if(response['status'] === 'success'){
                $('#options_area').html(response['html'])
                $('#save_options_btn').attr('option', '1')
            }else{
                custom_error_popup(response['message'])
                $('#edit_area_category').modal('hide')

            }
        },
        error: function () {
            error_popup()
            $('#edit_area_category').modal('hide')
        }
    })
})

$(document).on('click', '#skills_edit', function () {
    $('#edit_area_label').text('Skills')
    $('#edit_area_category').modal({backdrop: 'static', keyboard: false})
    $.ajax({
        type: 'GET',
        url: '/get_profile_info_options/2',
        success: function (response) {
            if(response['status'] === 'success'){
                $('#options_area').html(response['html'])
                $('#save_options_btn').attr('option', '2')
            }else{
                custom_error_popup(response['message'])
                $('#edit_area_category').modal('hide')

            }
        },
        error: function () {
            error_popup()
            $('#edit_area_category').modal('hide')
        }
    })
})

$(document).on('click', '#interests_edit', function () {
    $('#edit_area_label').text('Interests')
    $('#edit_area_category').modal({backdrop: 'static', keyboard: false})
    $.ajax({
        type: 'GET',
        url: '/get_profile_info_options/3',
        success: function (response) {
            if(response['status'] === 'success'){
                $('#options_area').html(response['html'])
                $('#save_options_btn').attr('option', '3')

            }else{
                custom_error_popup(response['message'])
                $('#edit_area_category').modal('hide')

            }
        },
        error: function () {
            error_popup()
            $('#edit_area_category').modal('hide')
        }
    })
})

$(document).on('click', '#values_edit', function () {
    $('#edit_area_category').modal({backdrop: 'static', keyboard: false})
    $('#edit_area_label').text('Values')
    $.ajax({
        type: 'GET',
        url: '/get_profile_info_options/4',
        success: function (response) {
            if(response['status'] === 'success'){
                $('#options_area').html(response['html'])
                $('#save_options_btn').attr('option', '4')
            }else{
                custom_error_popup(response['message'])
                $('#edit_area_category').modal('hide')
            }
        },
        error: function () {
            error_popup()
            $('#edit_area_category').modal('hide')
        }
    })
})

$(document).on('click', '.profile_option', function () {
    if($(this).hasClass('option_selected')){
        $(this).removeClass('option_selected')
    }else{
        if($('.option_selected').length >=5){
            $($('.option_selected')[4]).removeClass('option_selected')
        }
        $(this).addClass('option_selected')
    }
})

$(document).on('click', '#save_options_btn', function () {
    if(parseInt($(this).attr('option')) > 0){
        $(this).html('<div class="loadingio-spinner-spinner-j1ldxzuzgi"><div class="ldio-1d16qs58ad6">\n' +
        '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '</div></div>')
    var values = []
    for (i = 0; i < $('.option_selected').length; i++){
        values.push($($('.option_selected')[i]).attr('id'))
    }
    var id = $(this).attr('option')
    $.ajax({
        type: 'POST',
        url: '/update_profile_info_options',
        data: {'values': values, 'type': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#edit_area_category').modal('hide')
                $('.area_options[type-id="' + id.toString() +'"]').html(response['html'])
            }else{
                custom_error_popup(response['message'])
                $('#edit_area_category').modal('hide')
            }
        },
        error: function () {
            error_popup()
            $('#edit_area_category').modal('hide')
        }
    })
    }

})

$(document).on('click', '#notifications_toggle', function () {
    $('#notifications_modal').modal({backdrop: 'static', keyboard: false})
})

$(document).on('hidden.bs.modal', '#existing_convos', function () {
    $('#existing_convos_content').html('')
    $('#new_convo').attr('recipient-id', '0')
    $('#conversations_with').text('')
})

$(document).on('click', '#new_convo', function () {
    var id = $(this).attr('recipient-id')
    $('#recipient_name').text($('#conversations_with').text())
    $('#send_message_btn').attr('recipient-id', id.toString())
    $('#existing_convos').modal('hide');
    $('#new_message_modal').modal({backdrop: 'static', keyboard: false});
})

$(document).on('click', '#connect_with_btn', function () {
    var element = $(this)
    var current_text = element.html()
    element.html('<div class="loadingio-spinner-spinner-j1ldxzuzgi"><div class="ldio-1d16qs58ad6">\n' +
        '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '</div></div>')
    var id = $(this).attr('recipient-id')
    $.ajax({
        type: 'GET',
        url: '/get_existing_convos',
        data: {'r_id': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                if(response['html'].length === 0){
                    element.html(current_text)
                    $('#recipient_name').text(response['name'])
                    $('#send_message_btn').attr('recipient-id', id.toString())
                    $('#new_message_modal').modal({backdrop: 'static', keyboard: false});
                }else{
                    element.html(current_text)
                    $('#conversations_with').text(response['name'])
                    $('#new_convo').attr('recipient-id', id.toString())
                    $('#existing_convos_content').html(response['html'])
                    $('#existing_convos').modal({backdrop: 'static', keyboard: false});
                }
                make_moments()
            }else{
                custom_error_popup(response['message'])
                element.html(current_text)
            }
        },
        error: function () {
            error_popup()
            element.html(current_text)
        }
    })
})

$(document).on('click', '#send_message_btn', function () {
    var id = $(this).attr('recipient-id')
    var element = $(this)
    var current_text = element.html()
    if(check_length_special($('#message_subject'), 0, 140, 'Must be between 0 & 140 characters') &&
    check_length_special($('#message_body'), 0, 140, 'Must be between 0 & 140 characters')){
        element.html('<div class="loadingio-spinner-spinner-j1ldxzuzgi"><div class="ldio-1d16qs58ad6">\n' +
        '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '</div></div>')
        var s = $('#message_subject').val()
        var q = $('#message_body').val()
        $.ajax({
            type: 'POST',
            url: '/start_new_convo',
            data: {'r_id': id.toString(), 'q': q, 's': s},
            success: function (response) {
                if(response['status'] === 'success'){
                    document.location.pathname = '/message/' + response['id']
                }else{
                    custom_error_popup(response['message'])
                    element.html(current_text)
                }
            },
            error: function () {
                error_popup()
                element.html(current_text)
            }
        })
    }
})

function load_more_similar_users(element) {
    let div = $(element).get(0);
    var existing = []
    for (var i=0; i<$('.card_thx').length; i++){
        if(!existing.includes($($('.card_thx')[i]).attr('id'))){
            existing.push($($('.card_thx')[i]).attr('id'))
        }
    }
    if(div.scrollTop + div.clientHeight >= div.scrollHeight) {
        if($(element).children().last().attr('id') !== 'loading_spinner_more' && $(element).children().last().attr('id') !== 'no-results') {
            $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/get_similar_people',
                data: {
                    'set': $(element).attr('data-set'),
                    'existing': existing
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        $(element).children().last().remove()
                        $(element).append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }
}

function load_more_resources(element) {
    let div = $(element).get(0);
    if(div.scrollTop + div.clientHeight >= div.scrollHeight) {
        if($(element).children().last().attr('id') !== 'loading_spinner_more' && $(element).children().last().attr('id') !== 'no-results') {
            if($(element).children().last().attr('id') !== 'temp_row') {
                $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                    '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                    '</div></div></div> </div> ')
            }
            $.ajax({
                type: 'GET',
                url: '/get_resources',
                data: {
                    'set': $(element).attr('data-set'),
                    'ordering': $(element).attr('ordering')
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        $(element).children().last().remove()
                        $(element).append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }
}

function refresh_resources(){
    var element = $('#resources_table')
    $.ajax({
        type: 'GET',
        url: '/get_resources',
        data: {
            'set': $(element).attr('data-set'),
            'ordering': $(element).attr('ordering')
        },
        success: function (response) {
            if (response['status'] === 'success') {
                $(element).html(response['html'])
                $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                make_moments()
                window.history.pushState({}, document.title, document.location.pathname);
                window.history.replaceState(null, '', response['url']);
            } else {
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
}


$(document).on('click', '.resource_option', function () {
    $('.resource_option').each(function () {
        if($(this).hasClass('selected_resource')){
            $(this).removeClass('selected_resource')
        }
    })

    $(this).addClass('selected_resource')
    $('#resources_table').html('                            <div class="row" id="temp_row" style="animation: fadein 2s">\n' +
        '                        <h4 style="text-transform: uppercase; color: #818181ab; text-align: center">We are finding you resources for this category... give us one second!</h4>\n' +
        '                        <div class="loadingio-spinner-spinner-ok7idc80he9" style="display: block; margin: auto; text-align: center"><div class="ldio-u1oevpwp8f">\n' +
        '                        <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '                        </div></div>\n' +
        '            </div>\n')
    $('#resources_table').attr('ordering', $(this).attr('ordering'))
    $('#resources_table').attr('data-set', 0)
    refresh_resources()
})

$(document).on('click', '.event_option', function () {
    $('.event_option').each(function () {
        if($(this).hasClass('selected_event')){
            $(this).removeClass('selected_event')
        }
    })

    $(this).addClass('selected_event')
    $('#events_table').attr('ordering', $(this).attr('ordering'))
    $('#events_table').attr('data-set', 0)
    refresh_events()
})

$(document).on('click', '.external_link', function () {
        $('#external_link_btn').attr('url', $(this).attr('link'))
        $('#external_link_modal').modal('show')
})

$(document).on('click', '#external_link_btn', function () {
    $('#external_link_modal').modal('hide')
    window.open($(this).attr('url'), '_blank')
})


$(document).on('hidden.bs.modal', '#external_link_modal', function () {
    $('#external_link_btn').attr('url', '')

})

function blog_progress(element){
    var winScroll = element.scrollTop;
    var height = element.scrollHeight - element.clientHeight;
    var scrolled = (winScroll / height) * 100;
    $('#progress').css({'width': scrolled.toString() + '%'})
    if(scrolled >= 20){
        $('#back_to_blogs').css({'display': 'block'})
        $('#article_title').addClass('smaller_article', 1000)
        $('#article_title').removeClass('regular_article')

    }else{
        $('#back_to_blogs').css({'display': 'none'})
        $('#article_title').addClass('regular_article')
        $('#article_title').removeClass('smaller_article', 1000)
    }
}

$(document).on('click', '.share_btn', function () {
    $('#share_modal').modal('show')
})

$(document).on('shown.bs.modal', '#share_modal', function () {
    $('#social_icons_temp').clone().appendTo('#social_icons')
})

$(document).on('click', '.linkedin_share', function () {
    // console.log(document.location.host, document.location.hostname)
    // var link = 'https://www.linkedin.com/sharing/share-offsite/'
    // var obj = { url: 'https://ilmjtcv.com' , xdOrigin: document.location.host, xdChannel: 'a9fc6155-2bec-4f3f-8f6e-7b8010a740a7',
    // xd_origin_host: document.location.host};
    // var url = link + $.param(obj);
    // window.open(url, '_blank')
    $('.IN-2bc0215c-7188-4274-b598-1969e06d4d7c-1G9ISYhSF8XoOmdcl0yKDu')[0].click()
})

$(document).on('click', '.fb_share', function () {
    var link = 'https://www.facebook.com/sharer/sharer.php?'
    var obj = { kid_directed_site: 0 , sdk: 'joey', u: document.location.href, display: 'popup',
    ref: 'plugin', src:'share_btn'};
    var url = link + $.param(obj);
    window.open(url, '_blank')
})

$(document).on('click', '.twitter_share', function () {
    var link = 'https://twitter.com/intent/tweet?'
    var obj = { original_referer: document.location.href , ref_src: 'twsrc%5Etfw', text: document.title, tw_p: 'tweetbutton',
    url: document.location.href};
    var url = link + $.param(obj);
    window.open(url, '_blank')
})

function load_more_partners(element) {
    let div = $(element).get(0);
    if(div.scrollTop + div.clientHeight >= div.scrollHeight) {
        if($(element).children().last().attr('id') !== 'loading_spinner_more' && $(element).children().last().attr('id') !== 'no-more-posts') {
            if($(element).children().last().attr('id') !== 'temp_row'){
                $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            }
            $.ajax({
                type: 'GET',
                url: '/load_more_partners',
                data: {
                    'set': $(element).attr('data-set'),
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        $(element).children().last().remove()
                        $(element).append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                        var partner = getSearchParams('partner')
                        if(partner != null){
                            $.ajax({
                                type: 'GET',
                                url: '/get_partner_modal',
                                data: {'id': partner},
                                success: function (response) {
                                    if(response['status'] === 'success'){
                                        $('#partner_area').html(response['html'])
                                        $('#partner_modal').modal({backdrop: 'static', keyboard: false})
                                        $('#partner_modal').attr('partner-id', partner.toString())
                                    }else{
                                        custom_error_popup(response['message'])
                                        $('#partner_modal').modal('hide')
                                        window.history.pushState({}, document.title, document.location.pathname);
                                        window.history.replaceState({}, document.title,document.location.pathname.split('?')[0]);
                                    }
                                },
                                error: function () {
                                    error_popup()
                                    $('#partner_modal').modal('hide')
                                        window.history.pushState({}, document.title, document.location.pathname);
                                        window.history.replaceState({}, document.title,document.location.pathname.split('?')[0]);
                                }
                            })
                            window.history.pushState({}, document.title, document.location.pathname);
                            window.history.replaceState({}, document.title,document.location.pathname + '?partner=' + partner.toString());
                        }
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }
}

$(document).on('hidden.bs.modal', '#partner_modal', function () {
    $('#partner_area').html('')
    $(this).attr('partner-id', '0')
    window.history.pushState({}, document.title, document.location.pathname);
    window.history.replaceState({}, document.title,document.location.pathname.split('?')[0]);
})

$(document).on('hidden.bs.modal', '#event_modal', function () {
    $('#event_area').html('')
    $(this).attr('event-id', '0')
    window.history.pushState({}, document.title, document.location.pathname);
    window.history.replaceState({}, document.title,document.location.pathname.split('?')[0]);
})



$(document).on('click', '.event', function () {
    if(this.hasAttribute('event-id')){
        var id = $(this).attr('event-id')
        $('.learn_more[event-id="' + id.toString() + '"]').html('<div class="loadingio-spinner-spinner-5m5wfwkhl3a"><div class="ldio-fxcp7ev3c">\n' +
        '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '</div></div>')
        $.ajax({
        type: 'GET',
        url: '/get_event_modal',
        data: {'id': id},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#event_area').html(response['html'])
                $('#event_modal').modal({backdrop: 'static', keyboard: false})
                $('#event_modal').attr('event-id', id.toString())
                $('.learn_more[event-id="' + id.toString() + '"]').html('Learn More')
                make_moments()
                window.history.pushState({}, document.title, document.location.pathname);
                window.history.replaceState({}, document.title,document.location.pathname + '?event=' + id.toString());
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

$(document).on('click', '.event_preview', function () {
    if(this.hasAttribute('event-id')){
        var id = $(this).attr('event-id')
        $('#loading_modal').modal({backdrop: 'static', keyboard: false})
        $.ajax({
        type: 'GET',
        url: '/get_event_modal',
        data: {'id': id},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#event_area').html(response['html'])
                $('#event_modal').attr('event-id', id.toString())
                $('#loading_modal').modal('hide')
                make_moments()
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


$(document).on('click', '.partner', function () {
    if(this.hasAttribute('partner-id')){
         var id = $(this).attr('partner-id')
    $('.learn_more[partner-id="' + id.toString() + '"]').html('<div class="loadingio-spinner-spinner-5m5wfwkhl3a"><div class="ldio-fxcp7ev3c">\n' +
        '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '</div></div>')
    $.ajax({
        type: 'GET',
        url: '/get_partner_modal',
        data: {'id': id},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#partner_area').html(response['html'])
                $('#partner_modal').modal({backdrop: 'static', keyboard: false})
                $('#partner_modal').attr('partner-id', id.toString())
                $('.learn_more[partner-id="' + id.toString() + '"]').html('Learn More')
                window.history.pushState({}, document.title, document.location.pathname);
                window.history.replaceState({}, document.title,document.location.pathname + '?partner=' + id.toString());
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

$(document).on('click', '.visit_btn', function () {
    var id = $(this).attr('partner-id')
    window.open('/open_partner/' + id.toString(), '_blank')
})

function load_more_events(element) {
    let div = $(element).get(0);
    if(div.scrollTop + div.clientHeight >= div.scrollHeight) {
        if($(element).children().last().attr('id') !== 'loading_spinner_more' && $(element).children().last().attr('id') !== 'no-more-posts') {
            if($(element).children().last().attr('id') !== 'temp_row'){
                $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            }
            $.ajax({
                type: 'GET',
                url: '/load_more_events',
                data: {
                    'set': $(element).attr('data-set'),
                    'ordering': $(element).attr('ordering')
                },
                success: function (response) {
                    if (response['status'] === 'success') {
                        $(element).children().last().remove()
                        $(element).append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
                    } else {
                        error_popup()
                    }
                },
                error: function () {
                    error_popup()
                }
            })
        }
    }
}


function refresh_events(){
    var element = $('#events_table')
    if($(element.children().first()).attr('id') !=='temp_row'){
        element.html('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
    }
    $.ajax({
        type: 'GET',
        url: '/load_more_events',
        data: {
            'set': $(element).attr('data-set'),
            'ordering': $(element).attr('ordering')
        },
        success: function (response) {
            if (response['status'] === 'success') {
                $(element).html(response['html'])
                $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                make_moments()
                // if(!document.location.href.includes('/admin')){
                //     window.history.pushState({}, document.title, document.location.pathname);
                //     window.history.replaceState(null, '', response['url']);
                // }
                var event = getSearchParams('event')
                console.log(event)
                if(event != null){
                    $.ajax({
                        type: 'GET',
                        url: '/get_event_modal',
                        data: {'id': event},
                        success: function (response) {
                            if(response['status'] === 'success'){
                                $('#event_area').html(response['html'])
                                $('#event_modal').modal({backdrop: 'static', keyboard: false})
                                $('#event_modal').attr('event-id', event.toString())
                                make_moments()
                            }else{
                                custom_error_popup(response['message'])
                                $('#event_modal').modal('hide')
                                window.history.pushState({}, document.title, document.location.pathname);
                                window.history.replaceState({}, document.title,document.location.pathname.split('?')[0]);
                            }
                        },
                        error: function () {
                            error_popup()
                            $('#event_modal').modal('hide')
                            window.history.pushState({}, document.title, document.location.pathname);
                            window.history.replaceState({}, document.title,document.location.pathname.split('?')[0]);
                        }
                    })
                    window.history.pushState({}, document.title, document.location.pathname);
                    window.history.replaceState({}, document.title,document.location.pathname + '?event=' + event.toString());
                }
            } else {
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
}


$(document).on('click', '#submit_speaker', function () {
    var name = check_length_special($('#speaker_name'), 0, 200, 'Must be between 0 & 200 characters')
    var title = check_length_special($('#speaker_title'), 0, 200, 'Must be between 0 & 200 characters')
    var bio = check_length_special($('#speaker_bio'), 0, 2500, 'Must be between 0 & 5000 characters')
    var email = check_email($('#speaker_email')[0])
    var linkedin = isURL($('#speaker_linkedin').val())
    var img = $('#img_upload_speaker').val().length > 0
    var fd = new FormData($('#add_speaker_form')[0]);
    var files = $('#img_upload_speaker')[0].files[0];
    fd.append('file',files);
    // fd.append('n', $('#speaker_name').val())
    // var data = {'t': $('#speaker_title').val(), 'b': $('#speaker_bio').val(), 'e': $('#speaker_email').val(), 'l': $('#speaker_linkedin').val(), 'img': $('#img_upload_speaker')[0].files[0]}
    // fd.append('form', data)
    if(name && bio && email && linkedin && img && title){
         $('#loading_modal').modal({backdrop: 'static', keyboard: false})
        $.ajax({
            type: 'POST',
            url: '/admin/add_speaker',
            processData: false,
            contentType: false,
            data: fd,
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
    }
})

$(document).on('click', '#submit_news', function () {
    var title = check_length_special($('#news_title'), 0, 200, 'Must be between 0 & 200 characters')
    var description = check_length_special($('#news_description'), 0, 200, 'Must be between 0 & 200 characters')
    var link = isURL($('#news_link').val())
    var img = $('#news_img').val().length > 0
    var fd = new FormData($('#news_form')[0]);
    var files = $('#news_img')[0].files[0];
    fd.append('file',files);
    // fd.append('n', $('#speaker_name').val())
    // var data = {'t': $('#speaker_title').val(), 'b': $('#speaker_bio').val(), 'e': $('#speaker_email').val(), 'l': $('#speaker_linkedin').val(), 'img': $('#img_upload_speaker')[0].files[0]}
    // fd.append('form', data)
    if(description && link && img && title){
         $('#loading_modal').modal({backdrop: 'static', keyboard: false})
        $.ajax({
            type: 'POST',
            url: '/admin/add_news',
            processData: false,
            contentType: false,
            data: fd,
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
    }
})


$(document).on('click', '#submit_news_edit', function () {
    var title = check_length_special($('#news_title_edit'), 0, 200, 'Must be between 0 & 200 characters')
    var description = check_length_special($('#news_description_edit'), 0, 200, 'Must be between 0 & 200 characters')
    var link = isURL($('#news_link_edit').val())
    var fd = new FormData($('#news_form_edit')[0]);
    if($('#news_img')[0].files.length > 0){
        var files = $('#news_img')[0].files[0];
        fd.append('file',files);
    }
    if(description && link && title){
         $('#loading_modal').modal({backdrop: 'static', keyboard: false})
        $.ajax({
            type: 'POST',
            url: '/admin/edit_news',
            processData: false,
            contentType: false,
            data: fd,
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
    }
})


$(document).on('click', '.edit_speaker', function () {
    var id = $(this).attr('speaker-id')
    $.ajax({
        type: 'GET',
        url: '/admin/get_speaker_edit_modal',
        data: {'id': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#edit_speaker_form').html(response['html'])
                $('#edit_speaker_modal').modal('show')
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
})

$(document).on('click', '.edit_news', function () {
    var id = $(this).attr('news-id')
    $.ajax({
        type: 'GET',
        url: '/admin/get_news_edit_modal',
        data: {'id': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#news_form_edit').html(response['html'])
                $('#edit_news_story').modal('show')
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
})


$(document).on('click', '#edit_speaker', function () {
    var name = check_length_special($('#speaker_name_edit'), 0, 200, 'Must be between 0 & 200 characters')
    var title = check_length_special($('#speaker_title_edit'), 0, 200, 'Must be between 0 & 200 characters')
    var bio = check_length_special($('#speaker_bio_edit'), 0, 2500, 'Must be between 0 & 5000 characters')
    var email = check_email($('#speaker_email_edit')[0])
    var linkedin = isURL($('#speaker_linkedin_edit').val())
    var fd = new FormData($('#edit_speaker_form')[0]);
    var files = $('#img_upload_speaker_edit')[0].files[0];
    fd.append('file',files);
    if(name && bio && email && linkedin && title){
         $('#loading_modal').modal({backdrop: 'static', keyboard: false})
        $.ajax({
            type: 'POST',
            url: '/admin/edit_speaker',
            processData: false,
            contentType: false,
            data: fd,
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
    }
})

$(document).on('click', '#submit_event', function () {
    var title = check_length_special($('#event_title'), 0, 200, 'Must be between 0 & 200 characters')
    var description = check_length_special($('#event_description'), 0, 5000, 'Must be between 0 & 5000 characters')
    var link = isURL($('#event_link').val())
    var start = $('#start').val().length > 0
    var end = $('#end').val().length > 0
    var img = $('#img_upload_event').val().length > 0
    var speakers = $('#event_speakers').val().length > 0
    console.log(title, description, link, start, end, img, speakers)
    if(title && description && link && start && end && img && speakers){
        var fd = new FormData($('#add_event_form')[0]);
        var files = $('#img_upload_event')[0].files[0];
        fd.append('file',files);
        $('#loading_modal').modal({backdrop: 'static', keyboard: false})
        $.ajax({
            type: 'POST',
            url: '/admin/create_event',
            processData: false,
            contentType: false,
            data: fd,
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

    }


})

$(document).on('click', '#edit_event', function () {
    var a = confirm('Editing the start or end time will result in an update email being sent to everybody who has rsvped. Would you like to proceed?')
    if(a) {
        var title = check_length_special($('#event_title_edit'), 0, 200, 'Must be between 0 & 200 characters')
        var description = check_length_special($('#event_description_edit'), 0, 5000, 'Must be between 0 & 5000 characters')
        var link = isURL($('#event_link_edit').val())
        var start = $('#start').val().length > 0
        var end = $('#end').val().length > 0
        var speakers = $('#event_speakers_edit').val().length > 0
        if (title && description && link && start && end && speakers) {
            var fd = new FormData($('#edit_event_form')[0]);
            var files = $('#img_upload_event_edit')[0].files[0];
            fd.append('file', files);
            $('#loading_modal').modal({backdrop: 'static', keyboard: false})
            $.ajax({
                type: 'POST',
                url: '/admin/edit_event',
                processData: false,
                contentType: false,
                data: fd,
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


$(document).on('click', '.rsvp_btn', function () {
    if(this.hasAttribute('event-id')){
        var id = $(this).attr('event-id')
        if ($(this).hasClass('rsvped')){
            $(this).removeClass('rsvped')
            $(this).html('RSVP')
        }else{
            $(this).addClass('rsvped')
            $(this).html('Attending <i class="fas fa-check-circle" aria-hidden="true"></i>')
            custom_success_popup('You will receive the webinar link via email before this event begins.')
        }
    $.ajax({
        type: 'POST',
        url: '/rsvp_event',
        data: {'e_id': id.toString()},
        success: function(response){
            if(response['status'] !== 'success'){
                error_popup()
            }
        },
        error: function () {
            error_popup()
        }
    })
    }
})

$(document).on('click', '.watch_btn', function () {
    if(this.hasAttribute('event-id')){
        var id = $(this).attr('event-id')
        window.open('/watch_event/' + id.toString(), '_blank')
    }
})

$(document).on('click', '#add_email', function () {
            $('#add_email_modal').modal({backdrop: 'static', keyboard: false});
})

$(document).on('click', '#submit_email', function () {
    var subject = check_length_special($('#email_subject'), 0, 100, 'Must be between 0 & 100 characters')
    var header = check_length_special($('#email_header'), 0, 100, 'Must be between 0 & 100 characters')
    var button_text = check_length_special($('#button_text'), 0, 100, 'Must be between 0 & 100 characters')
    var prefix = check_length_special($('#email_prefix'), 0, 30, 'Must be between 0 & 30 characters')
    var button_link = isURL($('#button_link').val())
    var message = tinyMCE.editors['email_message'].getContent().length > 0 && tinyMCE.editors['email_message'].getContent().length < 1000000
    console.log('clicked')
    console.log(tinyMCE.editors['email_message'].getContent().length)
    console.log(subject, header, button_link, button_text, message, prefix)
    if(subject && header && button_link && button_text && message && prefix){
        console.log('success')
        $.ajax({
            type: 'POST',
            data: {'subject': $('#email_subject').val(), 'prefix': $('#email_prefix').val(),'header': $('#email_header').val(), 'button_text': $('#button_text').val(),
            'button_link': $('#button_link').val(), 'message': tinyMCE.editors['email_message'].getContent(), 'audience': $('#audience').val()},
            url: '/admin/add_email',
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
    }
})

function load_more_upcoming(element) {
    let div = $(element).get(0);
    if(div.scrollTop + div.clientHeight >= div.scrollHeight - 5) {
        if($(element).children().last().attr('id') !== 'loading_spinner_more' && $(element).children().last().attr('id') !== 'no-more-upcoming') {
            $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/get_upcoming_appointments',
                data: {
                    'offset': moment().utcOffset(),
                    'set': $(element).attr('data-set'),
                },
                success: function (response) {
                    console.log(response)
                    if(response['status'] === 'success'){
                        $(element).children().last().remove()
                        $('#upcoming_appointments').append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
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

function load_more_past(element) {
    let div = $(element).get(0);
    if(div.scrollTop + div.clientHeight >= div.scrollHeight) {
        if($(element).children().last().attr('id') !== 'loading_spinner_more' && $(element).children().last().attr('id') !== 'no-more-past') {
            $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/get_past_appointments',
                data: {
                    'offset': moment().utcOffset(),
                    'set': $(element).attr('data-set'),
                },
                success: function (response) {
                    if(response['status'] === 'success'){
                        $(element).children().last().remove()
                        $('#past_appointments').append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
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

function load_more_upcoming_mentee(element) {
    let div = $(element).get(0);
    if(div.scrollTop + div.clientHeight >= div.scrollHeight - 5) {
        if($(element).children().last().attr('id') !== 'loading_spinner_more' && $(element).children().last().attr('id') !== 'no-more-upcoming') {
            $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/get_upcoming_appointments_mentee',
                data: {
                    'offset': moment().utcOffset(),
                    'set': $(element).attr('data-set'),
                },
                success: function (response) {
                    if(response['status'] === 'success'){
                        $(element).children().last().remove()
                        $('#upcoming_appointments').append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
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

function load_more_past_mentee(element) {
    let div = $(element).get(0);
    if(div.scrollTop + div.clientHeight >= div.scrollHeight) {
        if($(element).children().last().attr('id') !== 'loading_spinner_more' && $(element).children().last().attr('id') !== 'no-more-past') {
            $(element).append('<div class="row" id="loading_spinner_more"><div class="col-sm-12" style="margin: auto; text-align: center; display: block"><div class="loadingio-spinner-spinner-lmswu5gqlpl"><div class="ldio-ysqxvp0pznb">\n' +
                '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
                '</div></div></div> </div> ')
            $.ajax({
                type: 'GET',
                url: '/get_past_appointments_mentee',
                data: {
                    'offset': moment().utcOffset(),
                    'set': $(element).attr('data-set'),
                },
                success: function (response) {
                    if(response['status'] === 'success'){
                        $(element).children().last().remove()
                        $('#past_appointments').append(response['html'])
                        $(element).attr('data-set', parseInt($(element).attr('data-set')) + 1)
                        make_moments()
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

function check_params() {
    let appointment = getSearchParams('appointment')
    let join = getSearchParams('join_appointment')
    if (appointment != null) {
        if ($('.edit[app-id="' + appointment + '"]').length === 1) {
            $('.edit[app-id="' + appointment + '"]').click()
        } else {
            open_appointment_mentor(appointment)
        }
    }
    if (join != null){
        open_join_appointment(join)
    }
}

function refresh_mentor_appointments(){
    var upcoming = $('#upcoming_appointments')
    $.ajax({
                type: 'GET',
                url: '/get_upcoming_appointments',
                data: {
                    'offset': moment().utcOffset(),
                    'set': $(upcoming).attr('data-set'),
                },
                success: function (response) {
                    if(response['status'] === 'success'){
                        $('#upcoming_appointments').html(response['html'])
                        $(upcoming).attr('data-set', parseInt($(upcoming).attr('data-set')) + 1)
                        make_moments()
                    }else{
                        custom_error_popup(response['message'])
                    }
                },
                error: function () {
                    error_popup()
                }
    })
    var past = $('#past_appointments')
    $.ajax({
                type: 'GET',
                url: '/get_past_appointments',
                data: {
                    'offset': moment().utcOffset(),
                    'set': $(past).attr('data-set'),
                },
                success: function (response) {
                    if(response['status'] === 'success'){
                        $('#past_appointments').html(response['html'])
                        $(past).attr('data-set', parseInt($(past).attr('data-set')) + 1)
                        make_moments()
                    }else{
                        custom_error_popup(response['message'])
                    }
                },
                error: function () {
                    error_popup()
                }
    })
    setTimeout(function () {
        check_params()
    }, 1200)

}

function refresh_mentee_appointments(){
    var upcoming = $('#upcoming_appointments')
    $.ajax({
                type: 'GET',
                url: '/get_upcoming_appointments_mentee',
                data: {
                    'offset': moment().utcOffset(),
                    'set': $(upcoming).attr('data-set'),
                },
                success: function (response) {
                    if(response['status'] === 'success'){
                        $('#upcoming_appointments').html(response['html'])
                        $(upcoming).attr('data-set', parseInt($(upcoming).attr('data-set')) + 1)
                        make_moments()
                    }else{
                        custom_error_popup(response['message'])
                    }
                },
                error: function () {
                    error_popup()
                }
    })
    var past = $('#past_appointments')
    $.ajax({
                type: 'GET',
                url: '/get_past_appointments_mentee',
                data: {
                    'offset': moment().utcOffset(),
                    'set': $(past).attr('data-set'),
                },
                success: function (response) {
                    if(response['status'] === 'success'){
                        $('#past_appointments').html(response['html'])
                        $(past).attr('data-set', parseInt($(past).attr('data-set')) + 1)
                        make_moments()
                    }else{
                        custom_error_popup(response['message'])
                    }
                },
                error: function () {
                    error_popup()
                }
    })
    setTimeout(function () {
        check_params()
    }, 1200)

}


$(document).on('click', '#add_availability', function () {
    $('#availability_modal').modal({backdrop: 'static', keyboard: false})
})

$(document).on('click', '#add_availability_btn', function () {
    console.log(parseInt($('#num_slots').text()))
    if(parseInt($('#num_slots').text()) > 0 && $('#slot_date').val() !== ''){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false})
        var data = {'date': $('#slot_date').val(), 'start': $("#time_start").data("DateTimePicker").date().format('HH:mm'), 'end': $("#time_end").data("DateTimePicker").date().format('HH:mm'), 'offset': $("#time_start").data("DateTimePicker").date().utcOffset()}
        $.ajax({
            type: 'POST',
            url: '/add_available_times',
            data: data,
            success: function (response) {
                if(response['status'] === 'success'){
                    document.location.reload()
                }else{
                    $('#loading_modal').modal('hide')
                    $('#error_box').text(response['message'])
                }
            },
            error: function () {
                error_popup()
            }
        })
    }else{
        $('#error_box').text('You must enter at least one 30 min. time slot on a specific date')
    }
})

$(document).on('hidden.bs.modal', '#edit_app_modal', function () {
    $('#edit_session_content').html('<div class="row">\n' +
        '                                <div class="col-sm-12">\n' +
        '                                    <div class="loadingio-spinner-spinner-ok7idc80he9" style="display: block; margin: auto; text-align: center"><div class="ldio-u1oevpwp8f">\n' +
        '                                    <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '                                    </div></div>\n' +
        '                                </div>\n' +
        '                            </div>')
    $('#edit_session_content').attr('app-id', '0')
    window.history.pushState({}, document.title, document.location.pathname);
    window.history.replaceState({}, document.title,document.location.pathname.split('?')[0]);
})

function open_appointment_mentor(id){
    $('#edit_app_modal').modal({backdrop: 'static', keyboard: false})
    $('#edit_session_content').attr('app-id', id)
    $.ajax({
        type: 'GET',
        url: '/get_edit_upcoming_modal',
        data: {'id': id},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#edit_session_content').html(response['html'])
                 $('#participant_notes').animate({ scrollTop: $('#participant_notes').prop('scrollHeight')}, 1000)
                make_moments()
            }else{
                $('#edit_app_modal').modal('hide')
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            $('#edit_app_modal').modal('hide')
            error_popup()
        }
    })
    window.history.pushState({}, document.title, document.location.pathname);
    window.history.replaceState({}, document.title,document.location.pathname + '?appointment=' + id.toString());
}

function open_join_appointment(id){
    $('#join_session_modal').modal({backdrop: 'static', keyboard: false})
    $('#session_info').html('<div class="row">\n' +
        '                                <div class="col-sm-12">\n' +
        '                                    <div class="loadingio-spinner-spinner-ok7idc80he9" style="display: block; margin: auto; text-align: center; height: 100px; width: 100px"><div class="ldio-u1oevpwp8f" style="transform: translateZ(0) scale(0.5); transform-origin: -80px -50px;">\n' +
        '                                    <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '                                    </div></div>\n' +
        '                                </div>\n' +
        '                            </div>')
    $.ajax({
        type: 'GET',
        url: '/get_join_modal',
        data: {'id': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#session_info').html(response['html'])
            }else{
                $('#join_session_modal').modal('hide')
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
    window.history.pushState({}, document.title, document.location.pathname);
    window.history.replaceState({}, document.title,document.location.pathname + '?join_appointment=' + id.toString());
}

$(document).on('click', '.upcoming .edit', function () {
    var id = $(this).attr('app-id')
    $('#edit_app_modal').modal({backdrop: 'static', keyboard: false})
    $('#edit_session_content').attr('app-id', id)
    $.ajax({
        type: 'GET',
        url: '/get_edit_upcoming_modal',
        data: {'id': id},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#edit_session_content').html(response['html'])
                 $('#participant_notes').animate({ scrollTop: $('#participant_notes').prop('scrollHeight')}, 1000)
                make_moments()
            }else{
                $('#edit_app_modal').modal('hide')
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            $('#edit_app_modal').modal('hide')
            error_popup()
        }
    })
    window.history.pushState({}, document.title, document.location.pathname);
    window.history.replaceState({}, document.title,document.location.pathname + '?appointment=' + id.toString());
})

$(document).on('keyup keydown keypress', '#add_participant_note', function () {
    if($(this).val().length > 0){
        $('#submit_note').removeAttr('disabled')
    }else{
        $('#submit_note').attr('disabled', '')
    }
})

$(document).on('keyup keydown keypress', '#add_participant_message', function () {
    if($(this).val().length > 0){
        $('#submit_message').removeAttr('disabled')
    }else{
        $('#submit_message').attr('disabled', '')
    }
})

$(document).on('click', '#submit_note', function () {
    var id = $(this).attr('app-id')
    if(check_length_special($('#add_participant_note'), 0,  1000, 'Note must be between 0 & 1000 characters.')){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false})
        $.ajax({
            type: 'POST',
            url: '/post_participant_note',
            data: {'id': id, 'q': $('#add_participant_note').val()},
            success: function (response) {
                if(response['status'] === 'success'){
                    $('#participant_notes').html(response['html'])
                    $('#participant_notes').attr('data-set', 1)
                     $('#participant_notes').animate({ scrollTop: $('#participant_notes').prop('scrollHeight')}, 1000)
                    make_moments()
                    $('#loading_modal').modal('hide')
                    $('#add_participant_note').val('')
                    $('#submit_note').attr('disabled', '')
                    $('#total_notes').text(parseInt($('#total_notes').text()) + 1)
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

$(document).on('click', '.participant_option', function () {
    $('.participant_option.activated').each(function () {
        $(this).removeClass('activated')
    })
    $(this).addClass('activated')
})

$(document).on('click', '#message_toggle_participant', function () {
    var id = $(this).attr('app-id')
    $('#participant_extra_area').html('<div class="row">\n' +
        '                                <div class="col-sm-12">\n' +
        '                                    <div class="loadingio-spinner-spinner-ok7idc80he9" style="display: block; margin: auto; text-align: center; height: 100px; width: 100px"><div class="ldio-u1oevpwp8f" style="transform: translateZ(0) scale(0.5); transform-origin: -80px -50px;">\n' +
        '                                    <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '                                    </div></div>\n' +
        '                                </div>\n' +
        '                            </div>')
    $.ajax({
        type: 'GET',
        url: '/get_participant_messages',
        data: {'id': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#participant_extra_area').html(response['html'])
                make_moments()
                 $('#participant_messages').animate({ scrollTop: $('#participant_messages').prop('scrollHeight')}, 1000)
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
})

$(document).on('click', '#personal_notes_toggle', function () {
    var id = $(this).attr('app-id')
    $('#participant_extra_area').html('<div class="row">\n' +
        '                                <div class="col-sm-12">\n' +
        '                                    <div class="loadingio-spinner-spinner-ok7idc80he9" style="display: block; margin: auto; text-align: center; height: 100px; width: 100px"><div class="ldio-u1oevpwp8f" style="transform: translateZ(0) scale(0.5); transform-origin: -80px -50px;">\n' +
        '                                    <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '                                    </div></div>\n' +
        '                                </div>\n' +
        '                            </div>')
    $.ajax({
        type: 'GET',
        url: '/get_participant_notes',
        data: {'id': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#participant_extra_area').html(response['html'])
                make_moments()
                 $('#participant_notes').animate({ scrollTop: $('#participant_notes').prop('scrollHeight')}, 1000)
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
})

$(document).on('click', '#submit_message', function () {
    var id = $(this).attr('board-id')
    var element = $(this)
    var m = $('#add_participant_message')
    if(check_length_special(m, 0, 140, 'Message must be between 0 & 140 characters')){
        $(this).before('<div class="loadingio-spinner-spinner-8kccqdvo9i" style="transform: scale(0.9); margin: 8px !important;"><div class="ldio-tnvxe4xu369">\n' +
            '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
            '</div></div>')
        $.ajax({
            type: 'POST',
            url: '/send_message',
            data: {'a': id, 'q': m.val()},
            success: function (response) {
                if(response['status'] === 'success'){
                    element.prev().remove()
                    element.attr('disabled', '')
                    m.val('')
                    $('#participant_messages').html(response['html'])
                    $('#participant_messages').attr('data-set', 1)
                    $("#participant_messages").animate({ scrollTop: $('#participant_messages').prop("scrollHeight")}, 500);
                    $('#total_messages').text(parseInt($('#total_messages').text()) + 1)
                    make_moments()
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

function cancel_appointment(id){
     $('#loading_modal').modal({backdrop: 'static', keyboard: false})
    $.ajax({
        type: 'POST',
        url: '/cancel_appointment',
        data: {'id': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                custom_success_popup('Appointment successfully cancelled')
                $('#edit_app_modal').modal('hide')
                $('.appointment[app-id="' + id.toString() +'"]').remove()
                if($('#upcoming_appointments').children().length === 0){
                    $('#upcoming_appointments').html('<div class="row" id="no-more-upcoming"><div class="col-sm-12 no-more-indicator">NO UPCOMING APPOINTMENTS</div><div class="filler"></div><div class="filler"></div></div>')
                }
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }

    })
}


$(document).on('click', '#cancel_app', function () {
    var id = $(this).attr('app-id')
    if($(this).attr('booked') === 'true'){
        var a = confirm('Are you sure you would like to cancel this appointment? This action is permanent. Both you and the client will receive confirmation of the cancellation.')
        if(a){
            cancel_appointment(id)
        }
    }else{
        cancel_appointment(id)
    }
})

$(document).on('click', '#confirm_mentor_info', function () {
    var zoom_link = isURL($('#appointment_zoom_link').val())
    if(!zoom_link){
        if (!$('#appointment_zoom_link').next().hasClass('val')){
            $('#appointment_zoom_link').addClass('incorrect')
            $('#appointment_zoom_link').after('<div class="val"><div class="row"><div class="col-sm-12 validator" id="type-l">' + 'Must be a valid Zoom link' +'</div></div></div>')
        }
    }
    var linked_in_link = isURL($('#linked_in_link').val())
    var bio = check_length_special($('#mentor_bio'), 100, 400, 'Must be between 100 & 400 characters')
    if(!linked_in_link){
        if (!$('#linked_in_link').next().hasClass('val')){
            $('#linked_in_link').addClass('incorrect')
            $('#linked_in_link').after('<div class="val"><div class="row"><div class="col-sm-12 validator" id="type-l">' + 'Must be a valid LinkedIn link' +'</div></div></div>')
        }
    }
    if($('#zoom_password_check').is(':checked')){
        var password = check_length_special($('#appointment_zoom_password'), 0, 1000, 'Password must be between 0 & 1000 characters')
        var data = {'password': $('#appointment_zoom_password').val(), 'link': $('#appointment_zoom_link').val(), 'bio': $('#mentor_bio').val(), 'linkedin': $('#linked_in_link').val()}
    }else{
        var password = true
        var data = {'password': '', 'link': $('#appointment_zoom_link').val(), 'bio': $('#mentor_bio').val(), 'linkedin': $('#linked_in_link').val()}
    }
    if(password && zoom_link && linked_in_link && bio){
         $('#loading_modal').modal({backdrop: 'static', keyboard: false})
        $.ajax({
            type: 'POST',
            url: '/update_mentor_info',
            data: data,
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
    }
})

$(document).on('click', '#change_zoom_info', function () {
    $('#edit_app_modal').modal('hide')
    $('#edit_zoom_info').modal('show')
})

$(document).on('click', '#delete_event', function () {
    var id = $(this).attr('event-id')
    var a = confirm('Are you sure you would like to delete this event? This action is permanent.')
    if(a){
        $.ajax({
            type: 'POST',
            url: '/admin/delete_event',
            data: {'id': id.toString()},
            success: function (response) {
                if(response['status'] === 'success'){
                    document.location = '/admin/events'
                }else{
                    custom_success_popup(response['message'])
                }
            },
            error: function () {
                error_popup()
            }

        })
    }
})

$(document).on('click', '#delete_news', function () {
    var id = $(this).attr('news-id')
    var a = confirm('Are you sure you would like to delete this news article. This action is permanent and the whole team will be notified?')
    if(a){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false});
        $.ajax({
            type: 'POST',
            url: '/admin/delete_news',
            data: {'id': id.toString()},
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
    }
})

$(document).on('click', '#booking_btn', function () {
    var time = $('#mentee_datepicker').val()
    refresh_slots(time)
    $('#booking_modal').modal({backdrop: 'static', keyboard: false})
})

$(document).on('click', '.available_slots li', function () {
    refresh_mentors(this)
})

$(document).on('hidden.bs.modal', '#mentor_options', function () {
    $('.available_slots li.selected').each(function () {
        $(this).removeClass('selected')
    })
    var time = $('#mentee_datepicker').val()
    refresh_slots(time)
})

$(document).on('click', '.confirm_session_btn', function () {
    var id = $(this).attr('app-id')
    $(this).html('<div class="loadingio-spinner-spinner-j1ldxzuzgi"><div class="ldio-1d16qs58ad6">\n' +
        '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '</div></div>')
    $.ajax({
        type: 'POST',
        url: '/register_appointment',
        data: {'id': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                custom_success_popup('Appointment Confirmed')
                $('#mentor_options').modal('hide')
                $('#booking_modal').modal('hide')
                $('#past_appointments').attr('data-set', 0)
                $('#upcoming_appointments').attr('data-set', 0)
                refresh_mentee_appointments()
            }else{
                custom_error_popup(response['message'])
                refresh_mentors($('.available_slots li.selected'))
                $('#mentor_options').modal('hide')

            }
        },
        error: function () {
                error_popup()
                $('#mentor_options').modal('hide')
                refresh_mentors($('.available_slots li.selected'))
        }
    })
})

$(document).on('click', '#join_session', function () {
    var id = $(this).attr('app-id')
    $('#join_session_modal').modal({backdrop: 'static', keyboard: false})
    $('#session_info').html('<div class="row">\n' +
        '                                <div class="col-sm-12">\n' +
        '                                    <div class="loadingio-spinner-spinner-ok7idc80he9" style="display: block; margin: auto; text-align: center; height: 100px; width: 100px"><div class="ldio-u1oevpwp8f" style="transform: translateZ(0) scale(0.5); transform-origin: -80px -50px;">\n' +
        '                                    <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '                                    </div></div>\n' +
        '                                </div>\n' +
        '                            </div>')
    $.ajax({
        type: 'GET',
        url: '/get_join_modal',
        data: {'id': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#session_info').html(response['html'])
                make_moments()
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
    window.history.pushState({}, document.title, document.location.pathname);
    window.history.replaceState({}, document.title,document.location.pathname + '?join_appointment=' + id.toString());
})

$(document).on('click', '#rating_btn', function () {
    var id = $(this).attr('app-id')
    $('#rate_session').modal({backdrop: 'static', keyboard: false})
    $('#rating_session_info').html('<div class="row">\n' +
        '                                <div class="col-sm-12">\n' +
        '                                    <div class="loadingio-spinner-spinner-ok7idc80he9" style="display: block; margin: auto; text-align: center; height: 100px; width: 100px"><div class="ldio-u1oevpwp8f" style="transform: translateZ(0) scale(0.5); transform-origin: -80px -50px;">\n' +
        '                                    <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '                                    </div></div>\n' +
        '                                </div>\n' +
        '                            </div>')
    $.ajax({
        type: 'GET',
        url: '/get_rating_modal',
        data: {'id': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#rating_session_info').html(response['html'])
                make_moments()
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }
    })
})

$(document).on('click', '.star', function () {
    var placement = parseInt($(this).attr('placement'))
    var above = []
    var above_full = []
    var below = []
    var element = this
    $('.star').each(function () {
        if (parseInt($(this).attr('placement')) > placement) {
            above.push(this)
            if ($(this)[0].className !== 'far fa-star star') {
                above_full.push(this)
            }
        } else if(parseInt($(this).attr('placement')) < placement) {
            below.push(this)
        }
    })
    if(above_full.length > 0){
        for (i = 0; i < above_full.length; i++){
            $(above_full[i])[0].className = 'far fa-star star'
        }
    }else{
        if($(element)[0].className === 'fas fa-star star'){
             $(element)[0].className = 'fas fa-star-half-alt star'
        }else{
            $(element)[0].className = 'fas fa-star star'
        }

    }
    for (i = 0; i < below.length; i++) {
        if($(below[i])[0].className !== 'fas fa-star star'){
            $(below[i])[0].className = 'fas fa-star star'
        }
    }
    var total = 0
    $('.star').each(function () {
       if($(this)[0].className === 'fas fa-star-half-alt star'){
           total += 0.5
       }else if($(this)[0].className === 'fas fa-star star'){
           total += 1
       }
    })
    $('#number_rating').text(total)
})

$(document).on('click', '#save_rating', function () {
    var score = $('#number_rating').text()
    var id = $(this).attr('app-id')
    $(this).html('<div class="loadingio-spinner-spinner-j1ldxzuzgi"><div class="ldio-1d16qs58ad6">\n' +
        '<div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '</div></div>')
    $.ajax({
        type: 'POST',
        url: '/post_appointment_rating',
        data: {'rating': score, 'id': id.toString()},
        success: function (response) {
            if(response['status'] === 'success'){
                $('#rate_session').modal('hide')
                custom_success_popup('Session Rating Saved')
                $('#past_appointments').attr('data-set', 0)
                $('#upcoming_appointments').attr('data-set', 0)
                refresh_mentee_appointments()
            }else{
                custom_error_popup(response['message'])
                $('#rate_session').modal('hide')
            }
        },
        error: function () {
            error_popup()
            $('#rate_session').modal('hide')
        }
    })
})

$(document).on('click', '#confirm_mentee_info', function () {
    var passed = false
    if($('#linked_in_link').val().length > 0){
        if(isURL($('#linked_in_link').val())){
            passed = true
        }else{
            var element = $('#linked_in_link')
            if (!element.next().hasClass('val')){
                element.addClass('incorrect')
                element.after('<div class="val"><div class="row"><div class="col-sm-12 validator" id="type-l">' + 'Must be a valid LinkedIn URL' +'</div></div></div>')
            }
        }
    }else{
        passed = true
    }
    var fd = new FormData($('#mentee_info_form')[0]);
    var files = $('#resume')[0].files[0];
    fd.append('file',files);
    if(passed){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false})
        $.ajax({
            type: 'POST',
            url: '/add_mentee_info',
            processData: false,
            contentType: false,
            data: fd,
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
})

$(document).on('change', '#resume', function () {
        var file = document.getElementById('resume');
        var filePath = file.value;
        var allowedExtensions =
            /(\.pdf)$/i;
         if (!allowedExtensions.exec(filePath)) {
                custom_error_popup('We are only accepting resumes in the form of .pdf at this time. You may use this website to convert your resume to a PDF: https://smallpdf.com/pdf-converter.');
                file.value = '';
                $('#submit_resume').attr('disabled', '')
                $('#edit_resume_submit').attr('disabled', '')
            }else {
                $('#submit_resume').removeAttr('disabled');
                $('#edit_resume_submit').removeAttr('disabled');
            }
});

$(document).on('click', '#confirm_mentor_application', function () {
    var bio = check_length_special($('#mentor_bio'), 20, 400, 'Must be between 20 & 400 characters')
    var why = check_length_special($('#why'), 20, 400, 'Must be between 20 & 400 characters')
    var linked_in = isURL($('#linked_in_link').val())
    if(!linked_in){
        var element = $('#linked_in_link')
            if (!element.next().hasClass('val')){
                element.addClass('incorrect')
                element.after('<div class="val"><div class="row"><div class="col-sm-12 validator" id="type-l">' + 'Must be a valid LinkedIn URL' +'</div></div></div>')
            }
    }
    var zoom_link = isURL($('#appointment_zoom_link').val())
    if(!zoom_link){
        var element = $('#appointment_zoom_link')
            if (!element.next().hasClass('val')){
                element.addClass('incorrect')
                element.after('<div class="val"><div class="row"><div class="col-sm-12 validator" id="type-l">' + 'Must be a valid Zoom URL' +'</div></div></div>')
            }
    }
    var zoom_password = false
    if($('#zoom_password_check').is(':checked')){
        if(check_length_special($('#appointment_zoom_password'), 0, 50, 'Must be a valid Zoom password.')){
            zoom_password = true
        }else{
            zoom_password = false
        }
    }else{
        zoom_password = true
    }
    if(bio && why && zoom_link && zoom_password && linked_in){
        $('#loading_modal').modal({backdrop: 'static', keyboard: false})
        $.ajax(
            {
                type: 'POST',
                url: '/apply_mentor',
                data:{'linked_in_link': $('#linked_in_link').val(), 'bio': $('#mentor_bio').val(),
                'zoom_password': $('#appointment_zoom_password').val(), 'zoom_link': $('#appointment_zoom_link').val(),
                'why': $('#why').val()},
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
            }
        )

    }

})

$(document).on('click', '.approve_mentor', function () {
    var id = $(this).attr('mentor-id')
    $('#loading_modal').modal({backdrop: 'static', keyboard: false})
    $.ajax({
        type: 'POST',
        url: '/admin/confirm_mentor',
        data: {'id': id.toString()},
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

$(document).on('click', '.reject_mentor', function () {
    var id = $(this).attr('mentor-id')
    $('#loading_modal').modal({backdrop: 'static', keyboard: false})
    $.ajax({
        type: 'POST',
        url: '/admin/reject_mentor',
        data: {'id': id.toString()},
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


$(document).on('hidden.bs.modal', '#join_session_modal', function () {
    window.history.pushState({}, document.title, document.location.pathname);
    window.history.replaceState({}, document.title,document.location.pathname.split('?')[0]);
})

$(document).on('click', '.edit_email', function () {
    var id = $(this).attr('email-id')
    $('#loading_modal').modal({backdrop: 'static', keyboard: false})
    $.ajax({
        type: 'GET',
        url: '/admin/get_edit_email',
        data: {'id': id.toString()},
        success: function (response) {
            console.log(response)
            if(response['status'] === 'success'){
                $('#loading_modal').modal('hide')
                $('#edit_email_form').html(response['html'])
                $('#audience_edit').selectpicker()
                $('#audience_edit').selectpicker('val', response['audience'])
                tinymce.init({
        selector: 'textarea#email_message_edit',
        plugins: 'lists',
         toolbar: 'bold italic underline | numblist bullist|fontsizeselect formatselect | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist | forecolor backcolor removeformat',
         toolbar_sticky: true,
        menubar: '',
    })
                make_moments()
                $('#edit_email_modal').modal({backdrop: 'static', keyboard: false})
            }else{
                custom_error_popup(response['message'])
            }
        },
        error: function () {
            error_popup()
        }

    })


})

$(document).on('click', '#edit_email_submit', function () {
    var id = $(this).attr('email-id')
    var subject = check_length_special($('#email_subject_edit'), 0, 100, 'Must be between 0 & 100 characters')
    var header = check_length_special($('#email_header_edit'), 0, 100, 'Must be between 0 & 100 characters')
    var button_text = check_length_special($('#button_text_edit'), 0, 100, 'Must be between 0 & 100 characters')
    var prefix = check_length_special($('#email_prefix_edit'), 0, 30, 'Must be between 0 & 30 characters')
    var button_link = isURL($('#button_link_edit').val())
    var message = tinyMCE.editors['email_message_edit'].getContent().length > 0 && tinyMCE.editors['email_message_edit'].getContent().length < 1000000
    if(subject && header && button_link && button_text && message && prefix){
        $.ajax({
            type: 'POST',
            data: {'id': id.toString(),'subject': $('#email_subject_edit').val(), 'prefix': $('#email_prefix_edit').val(),'header': $('#email_header_edit').val(), 'button_text': $('#button_text_edit').val(),
            'button_link': $('#button_link_edit').val(), 'message': tinyMCE.editors['email_message_edit'].getContent(), 'audience': $('#audience_edit').val()},
            url: '/admin/edit_email',
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
    }
})

$(document).on('click', '.delete_email', function () {
    var id = $(this).attr('email-id')
    $.ajax({
            type: 'POST',
            data: {'id': id.toString()},
            url: '/admin/delete_email',
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