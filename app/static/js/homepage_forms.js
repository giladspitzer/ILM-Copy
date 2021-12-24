function check_input(element){
    if (element.value.length === 0){
        $(element).addClass('incorrect')
        if (!$(element.nextElementSibling).hasClass('val')) {
            $(element).after('<div class="val"><div class="row"><div class="col-sm-12 validator">Please fill this field out!</div></div></div>')
        }
        return false
    }else if (element.value.length < 3 && element.value.length > 0){
        $(element).addClass('incorrect')
        if (!$(element.nextElementSibling).hasClass('val')){
            $(element).after('<div class="val"><div class="row"><div class="col-sm-12 validator">We need more info than this!!</div></div></div>')
        }
        return false
    }else{
        $(element).removeClass('incorrect')
        if ($(element.nextElementSibling).hasClass('val')){
            $(element.nextElementSibling).remove()
        }
        return true
    }
}

$(document).on('click keyup blur change focus', '#industry_test, #location_test', function () {
    if ($(this.nextElementSibling).hasClass('val')){
        $(this.nextElementSibling).remove();
        $(this).removeClass('incorrect')
    }
})
$(document).on('click', '#submit_test', function () {
    var location = document.getElementById('location_test');
    var industry = document.getElementById('industry_test');
    var i = check_input(industry);
    if (i) {
        if (document.getElementById('profile') != null) {
            document.location = '/jobs'
        } else {
            $('#default-register').css({'display': 'none'})
            $('#loading_modal').modal({backdrop: 'static', keyboard: false});
            $.ajax({
                type: 'POST',
                url: '/auth/get_register_numbers',
                data: {'i': industry.value, 'l': location.value},
                success: function (data) {
                    if(data['status'] === 'success') {
                        $('#loading_modal').modal('hide')
                        var wrapper = document.createElement('div');
                        wrapper.innerHTML = data['html'];
                        window.history.pushState({}, document.title, document.location.pathname);
                        window.history.replaceState({}, data['title'], data['url']);
                        document.title = data['title']
                        $('.container_full').fadeOut(350, function () {
                            $('.container_full').replaceWith($('.container_full', wrapper));
                            $(".container_full").fadeIn(350);
                        });
                        document.body.scrollIntoView({behavior: 'smooth', block: 'start'});
                        }},
                error: function () {
                    error_popup()
                },
            });
        }
    }
});

$(document).on('click', '#submit_short', function () {
    var email = document.getElementById('email_short')
    if (document.getElementById('profile') != null){
        document.location='/unemployment_map'
    }else{
    if (check_email(email)){
        $('#g_email').val(email.value);
        $(email).val('')
        reload('/auth/register_')
    }else{
        $(email).addClass('incorrect')
        if (!$(email.nextElementSibling).hasClass('val')) {
            $(email).after('<div class="val"><div class="row"><div class="col-sm-12 validator">Must be an email address!</div></div></div>')
        }
    }}
})

$(document).on('click', '#submit_short_recruiter', function () {
    var email = document.getElementById('email_short')
    if (document.getElementById('profile') != null){
        document.location='/unemployment_map'
    }else{
    if (check_email(email)){
        reload('/auth/partnership_inquiry_')
        $('#g_email').val(email.value);
    $(email).val('')
    }else{
        $(email).addClass('incorrect')
        if (!$(email.nextElementSibling).hasClass('val')) {
            $(email).after('<div class="val"><div class="row"><div class="col-sm-12 validator">Must be an email address!</div></div></div>')
        }
    }}
})

$(document).on('blur change keyup click', '#email_short', function () {
    $(this).removeClass('incorrect');
        if ($(this.nextElementSibling).hasClass('val')) {
                $(this.nextElementSibling).remove()
            }
});


$(document).ready(function () {
    var autocomplete;
    autocomplete = new google.maps.places.Autocomplete((document.getElementById('location_test')), {
        types: ['(cities)'],
    });

    google.maps.event.addListener(autocomplete, 'place_changed', function () {
        var near_place = autocomplete.getPlace();
    });
});

// $(document).on('click', '#recruiter_search_test', function () {
//     var industry = document.getElementById('industry_test');
//     var l = check_input(location);
//     var i = check_input(industry);
//     if (i && l) {
//         if (document.getElementById('loading_modal') === null) {
//             document.location = '/jobs'
//         } else {
//             $('#default-register').css({'display': 'none'})
//             $('#loading_modal').modal({backdrop: 'static', keyboard: false});
//             $.ajax({
//                 type: 'POST',
//                 url: '/auth/get_register_numbers',
//                 data: {'i': industry.value, 'l': location.value},
//                 success: function (data) {
//                     $('#job_num').text(data['j']);
//                     $('#recruiter_num').text(data['r']);
//                     setTimeout(function () {
//                         $('#loading_modal').modal('toggle')
//                     }, 1000);
//                     $('#results_space').css({'display': 'block'});
//                     setTimeout(function () {
//                         $('#register_modal').modal({backdrop: 'static', keyboard: false})
//                     }, 1100)
//                 },
//                 error: function () {
//                     error_popup()
//                 },
//             });
//         }
//     }
// });
function close_register() {
    $('#default-register').css({'display':'block'});
    $('#results_space').css({'display':'none'});
    $('#industry_test').val('');
    $('#industry_test').blur();
    $('#location_test').val('');
    $('#location_test').blur();
    return true
}

$(document).on('click', '.test_element', function () {
    $('li.active').each(function () {
        $(this).removeClass('active')
    })
    $(this).addClass('active')
})

$(document).on('click', '#resource_test', function () {
    $('#test_table').html('<div class="loadingio-spinner-spinner-ok7idc80he9" style="display: block; margin: auto; text-align: center"><div class="ldio-u1oevpwp8f">\n' +
        '                                    <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '                                    </div></div>')
    setTimeout(function () {
        $('#test_table').html(' <li class="col-xs-12 col-sm-6 resource resource-ui" style="cursor: pointer">\n' +
            '                                        <p class="resource_descriptor">UnEmployment Assistance</p>\n' +
            '                                        <img src="https://cdnmon.cfigroup.com/ueditor/net/upload/image/20170929/6364227796023985614405620.png" class="img-rounded resource_img">\n' +
            '                                        <div class="resource_info">\n' +
            '                                            <h5>Benefits.gov</h5>\n' +
            '                                            <p>Governmental benefits in areas such as employment/career development, financial assistance, food/nutrition, healthcare, education, etc.</p>\n' +
            '                                        </div>\n' +
            '                                </li>\n' +
            '                                    <li class="col-xs-12 col-sm-6 resource resource-ui" style="cursor: pointer">\n' +
            '                                        <p class="resource_descriptor">Virtual Networking</p>\n' +
            '                                        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcSBGdRXtgA7tAOaU4AZllIvjcUSkHxqq0d_GQ&amp;usqp=CAU" class="img-rounded resource_img">\n' +
            '                                        <div class="resource_info">\n' +
            '                                            <h5>Workforce Solutions</h5>\n' +
            '                                            <p>Hiring events and job fairs. Also an online employment database. </p>\n' +
            '                                        </div>\n' +
            '                                    </li>\n' +
            '                                    <div class="clearfix visible-md visible-lg visible-sm"></div>\n' +
            '                                    <li class="col-xs-12 col-sm-6 resource resource-ui" style="cursor: pointer">\n' +
            '                                        <p class="resource_descriptor">Food &amp; Shelter</p>\n' +
            '                                        <img src="https://www.foodpantries.org/gallery/1089_echo_mbb.png" class="img-rounded resource_img">\n' +
            '                                        <div class="resource_info">\n' +
            '                                            <h5>FoodPantries.org</h5>\n' +
            '                                            <p>Food help by state (local pantries, soup kitchens, food shelves, food banks</p>\n' +
            '                                        </div>\n' +
            '                                    </li>\n' +
            '                                    <li class="col-xs-12 col-sm-6 resource resource-ui" style="cursor: pointer">\n' +
            '                                        <p class="resource_descriptor">Skill Building</p>\n' +
            '                                        <img src="https://images.g2crowd.com/uploads/product/image/social_landscape/social_landscape_f659c30a5dd7cec9489e4aad27738b13/skillsoft.png" class="img-rounded resource_img">\n' +
            '                                        <div class="resource_info">\n' +
            '                                            <h5>Skillsoft</h5>\n' +
            '                                            <p>Resources such as webinars, podcasts, and blogs. Tips to improve skills.</p>\n' +
            '                                        </div>\n' +
            '                                    </li>\n' +
            '                                    <div class="clearfix visible-md visible-lg visible-sm"></div>\n' +
            '                                    <h3 style="margin: 5px 3px 5px 0; font-size: 22px; color: #30415d; text-align: center">And many many more...</h3>\n')
    }, 1000)
})


$(document).on('click', '#blogs_test', function () {
    $('#test_table').html('<div class="loadingio-spinner-spinner-ok7idc80he9" style="display: block; margin: auto; text-align: center"><div class="ldio-u1oevpwp8f">\n' +
        '                                    <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '                                    </div></div>')
    setTimeout(function () {
        $('#test_table').html('<li class="row blog" onclick="document.location=\'/blog/2\'">\n' +
            '                                        <div class="col-sm-4 col-xs-12">\n' +
            '                                            <div class="title" style="font-size: 24px; line-height: 30px">How to Build a Mentor Relationship</div>\n' +
            '                                            <div class="author">Amanda, Rachel</div>\n' +
            '                                        </div>\n' +
            '                                        <div class="col-sm-4 hidden-xs snippet">\n' +
            '                                            Forming a relationship with a mentor can provide you with many advantages. They can help connect...\n' +
            '                                        </div>\n' +
            '                                        <div class="col-sm-4 col-xs-12">\n' +
            '                                            <img src="/static/images/articles/mentor.jpeg" class="img">\n' +
            '                                        </div>\n' +
            '                                    </li>\n' +
            '                                    <li class="row blog" onclick="document.location=\'/blog/1\'" style="margin-top: 10px">\n' +
            '                                        <div class="col-sm-4 col-xs-12">\n' +
            '                                            <div class="title" style="font-size: 24px; line-height: 30px">10 Ways to Ace Your Interview\n' +
            '                                        </div>\n' +
            '                                            <div class="author">Amanda Jedwab</div>\n' +
            '                                        </div>\n' +
            '                                        <div class="col-sm-4 hidden-xs snippet">\n' +
            '                                            The advance preparation for a job interview is one of the most important components of how a can...\n' +
            '                                        </div>\n' +
            '                                        <div class="col-sm-4 col-xs-12">\n' +
            '                                            <img src="/static/images/articles/tips.png" class="img">\n' +
            '                                        </div>\n' +
            '                                    </li>\n' +
            '                                    <br>\n' +
            '                                    <div class="external_option_btn" onclick="document.location=\'/blogs\'" style="display: table">View All</div></ul>')
    }, 1000)
})

$(document).on('click', '#partnership_test', function () {
    $('#test_table').html('<div class="loadingio-spinner-spinner-ok7idc80he9" style="display: block; margin: auto; text-align: center"><div class="ldio-u1oevpwp8f">\n' +
        '                                    <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '                                    </div></div>')
    setTimeout(function () {
        $('#test_table').html('<li class="col-sm-6 col-xs-12 partner">\n' +
            '                                        <img class="cover_img" src="/static/images/partners/wftj_cover.png">\n' +
            '                                        <br>\n' +
            '                                        <div class="row">\n' +
            '                                            <div class="col-sm-5 col-xs-12 centered_small">\n' +
            '                                                <img class="main_img" src="/static/images/partners/wftj.png">\n' +
            '                                            </div>\n' +
            '                                            <div class="col-sm-7 col-xs-12 centered_small">\n' +
            '                                                <h4 class="name" style="font-size: 24px; line-height: 30px">Write For The Job</h4>\n' +
            '                                            </div>\n' +
            '                                        </div>\n' +
            '                                        <p class="snippet" style="font-size: 14px">WFTJ will equip you with a stand out resume, cover letter, and Linkedin profile that will leave an impression on HR professionals and recruiters.</p>\n' +
            '                                        <hr style="margin-bottom: 10px">\n' +
            '                                        <div class="learn_more" onclick="document.location=\'/auth/register\'" style="width: 90%; margin: 10px">Learn More</div>\n' +
            '                                    </li>\n' +
            '<li class="col-sm-6 col-xs-12 partner">\n' +
            '                                        <img class="cover_img" src="/static/images/partners/fn_cover.png">\n' +
            '                                        <br>\n' +
            '                                        <div class="row">\n' +
            '                                            <div class="col-sm-5 col-xs-12 centered_small">\n' +
            '                                                <img class="main_img" src="/static/images/partners/fn.png">\n' +
            '                                            </div>\n' +
            '                                            <div class="col-sm-7 col-xs-12 centered_small">\n' +
            '                                                <h4 class="name" style="font-size: 24px; line-height: 30px">The Furlough Network</h4>\n' +
            '                                            </div>\n' +
            '                                        </div>\n' +
            '                                        <p class="snippet" style="font-size: 14px">In response to the recent influx of furloughed workers, our team rushed to create this site. Let\'s get together and support each other now, as we prepare for the resurgence ahead!</p>\n' +
            '                                        <hr style="margin-bottom: 10px">\n' +
            '                                        <div class="learn_more" onclick="document.location=\'/auth/register\'" style="width: 90%; margin: 10px">Learn More</div>\n' +
            '                                    </li>\n' +
            '                                    <div class="clearfix visible-md visible-lg visible-sm"></div>\n' +
            '                                    <br>\n' +
            '                                    <h3 style="margin: 5px 3px 5px 0; font-size: 22px; color: #30415d; text-align: center">And many many more...</h3>')
    }, 1000)
})

$(document).on('click', '#sessions_test', function () {
    $('#test_table').html('<div class="loadingio-spinner-spinner-ok7idc80he9" style="display: block; margin: auto; text-align: center"><div class="ldio-u1oevpwp8f">\n' +
        '                                    <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '                                    </div></div>')
    setTimeout(function () {
        $('#test_table').html('<img src="https://d24708ad3trvus.cloudfront.net/static/images/sessions.gif" style="width: 100%; display: block; margin: 25% auto; max-width: 600px; border-radius: 20px">')
    }, 1000)
})

$(document).on('click', '#events_test', function () {
    $('#test_table').html('<div class="loadingio-spinner-spinner-ok7idc80he9" style="display: block; margin: auto; text-align: center"><div class="ldio-u1oevpwp8f">\n' +
        '                                    <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>\n' +
        '                                    </div></div>')
    setTimeout(function () {
        $('#test_table').html('<li class="col-sm-6 col-xs-12 event">\n' +
            '    <div class="row">\n' +
            '        <div class="col-sm-12 col-xs-12 centered_small">\n' +
            '            <img class="event_img img-rounded" src="https://ilmjtcv-other.s3.us-east-2.amazonaws.com/events/Examining_Thoughts_and_Flipping_Failure.jpg">\n' +
            '        </div>\n' +
            '        <div class="col-sm-12 col-xs-12 centered_small event_info">\n' +
            '            <h4 class="title">Examining Thoughts and Flipping Failure <span style="font-size: 12px;">• Webinar</span></h4>\n' +
            '                <p style="font-size: 16px"><i class="fas fa-user" aria-hidden="true"></i> Jill Griffin</p>\n' +
            '                \n' +
            '                <p class=""><i class="fas fa-calendar" aria-hidden="true"></i> <span class="" data-timestamp="2020-08-19T15:45:00Z" data-format="format(\'L\')" data-refresh="0" style="display: inline-block;"><span class="blurred_content">08/19/2020</span></span></p>\n' +
            '                <p class=""><i class="fas fa-clock" aria-hidden="true"></i> <span class="" data-timestamp="2020-08-19T15:00:00Z" data-format="format(\'LT\')" data-refresh="0" style="display: inline-block;"><span class="blurred_content">11:00 AM</span> - <span class="" data-timestamp="2020-08-19T15:45:00Z" data-format="format(\'LT\')" data-refresh="0" style="display: inline-block;"><span class="blurred_content">11:45 AM</span></span> </span></p>\n' +
            '                \n' +
            '                \n' +
            '                <p class="snippet" style="font-size: 14px">Join Jill for an interactive webinar about examining personal thoughts and flipping failures into big successes</p>\n' +
            '        </div>\n' +
            '    </div>\n' +
            '    <hr style="margin-bottom: 10px">\n' +
            '    <div class="learn_more" onclick="document.location=\'/auth/register\'">Learn More</div>\n' +
            '</li>\n' +
        '<li class="col-sm-6 col-xs-12 event">\n' +
            '    <div class="row">\n' +
            '        <div class="col-sm-12 col-xs-12 centered_small">\n' +
            '            <img class="event_img img-rounded" src="https://ilmjtcv-other.s3.us-east-2.amazonaws.com/events/Acing_the_Virtual_Interview.jpg">\n' +
            '        </div>\n' +
            '        <div class="col-sm-12 col-xs-12 centered_small event_info">\n' +
            '            <h4 class="title">Acing the Virtual Interview <span style="font-size: 12px;">• Webinar</span></h4>\n' +
            '                <p style="font-size: 16px"><i class="fas fa-user" aria-hidden="true"></i> Amy Geffen, PhD</p>\n' +
            '                \n' +
            '                <p class=""><i class="fas fa-calendar" aria-hidden="true"></i> <span class="" data-timestamp="2020-09-03T17:00:00Z" data-format="format(\'L\')" data-refresh="0" style="display: inline-block;"><span class="blurred_content">09/03/2020</span></span></p>\n' +
            '                <p class=""><i class="fas fa-clock" aria-hidden="true"></i> <span class="" data-timestamp="2020-09-03T16:00:00Z" data-format="format(\'LT\')" data-refresh="0" style="display: inline-block;"><span class="blurred_content">12:00 PM</span></span> - <span class="" data-timestamp="2020-09-03T17:00:00Z" data-format="format(\'LT\')" data-refresh="0" style="display: inline-block;"><span class="blurred_content">1:00 PM</span></span></p>\n' +
            '                \n' +
            '                \n' +
            '                <p class="snippet" style="font-size: 14px">Interviews are nerve wracking in normal times and now during COVID they add extra pressure.  Learn how to prepare for the interview through research, </p>\n' +
            '        </div>\n' +
            '    </div>\n' +
            '    <hr style="margin-bottom: 10px">\n' +
            '    <div class="learn_more" onclick="document.location=\'/auth/register\'">Learn More</div>\n' +
            '</li>')
    }, 1000)
})


