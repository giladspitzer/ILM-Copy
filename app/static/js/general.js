
$(document).on('blur', '.special_input', function () {
    if (this.value.length > 0){
        $(this.nextElementSibling).addClass('blurred')
    }else{
        $(this.nextElementSibling).removeClass('blurred')
    }
});

// $(document).on('click', '#main_body', function () {
//     $('#main_body').html('<div class="timeline-wrapper">\n' +
//         '    <div class="timeline-item">\n' +
//         '        <div class="animated-background">\n' +
//         '            <div class="background-masker header-top"></div>\n' +
//         '            <div class="background-masker header-left"></div>\n' +
//         '            <div class="background-masker header-right"></div>\n' +
//         '            <div class="background-masker header-bottom"></div>\n' +
//         '            <div class="background-masker subheader-left"></div>\n' +
//         '            <div class="background-masker subheader-right"></div>\n' +
//         '            <div class="background-masker subheader-bottom"></div>\n' +
//         '            <div class="background-masker content-top"></div>\n' +
//         '            <div class="background-masker content-first-end"></div>\n' +
//         '            <div class="background-masker content-second-line"></div>\n' +
//         '            <div class="background-masker content-second-end"></div>\n' +
//         '            <div class="background-masker content-third-line"></div>\n' +
//         '            <div class="background-masker content-third-end"></div>\n' +
//         '        </div>\n' +
//         '    </div>\n' +
//         '</div>')
//
// })

function reload(target) {
    // $('#main_body').append('<div class="timeline-wrapper">\n' +
    //     '    <div class="timeline-item">\n' +
    //     '        <div class="animated-background">\n' +
    //     '            <div class="background-masker header-top"></div>\n' +
    //     '            <div class="background-masker header-left"></div>\n' +
    //     '            <div class="background-masker header-right"></div>\n' +
    //     '            <div class="background-masker header-bottom"></div>\n' +
    //     '            <div class="background-masker subheader-left"></div>\n' +
    //     '            <div class="background-masker subheader-right"></div>\n' +
    //     '            <div class="background-masker subheader-bottom"></div>\n' +
    //     '            <div class="background-masker content-top"></div>\n' +
    //     '            <div class="background-masker content-first-end"></div>\n' +
    //     '            <div class="background-masker content-second-line"></div>\n' +
    //     '            <div class="background-masker content-second-end"></div>\n' +
    //     '            <div class="background-masker content-third-line"></div>\n' +
    //     '            <div class="background-masker content-third-end"></div>\n' +
    //     '        </div>\n' +
    //     '    </div>\n' +
    //     '</div>')
    $.ajax({
        type: 'GET',
        url: target,
        contentType: "application/json",
        success: function(data) {
            // console.log($('head').childElementCount)
            // var blank_head = document.createElement('head');
            // var head = document.createElement('head');
            // $('head').replaceWith(blank_head);
            // console.log($('head').childElementCount)
            var wrapper= document.createElement('div');
            wrapper.innerHTML= data['html'];
            // head.innerHTML = data['html'];
            // $(head).children().each(function () {
            //     if (this.nodeName === 'DIV'){
            //     }else{
            //         console.log(this);
            //         $('head').append(this)
            //     }
            // });
            window.history.pushState({}, document.title, document.location.pathname);
            window.history.replaceState({data}, data['title'], data['url']);
            document.title = data['title']
            $('.container_full').fadeOut(350, function() {
                $('.container_full').replaceWith($('.container_full', wrapper));
                $(".container_full").fadeIn(350);
            });
            document.body.scrollIntoView({behavior: 'smooth', block: 'start'});
        },
	    error: function() {
           error_popup()
        }
    });
}

function error_popup() {
    $('#loading_modal').modal('hide')
    $.fn.cornerpopup({
    variant: 9,
    header: "Error!",
    text2: 'An Error has occurred. Please try again and if the issue persists, try clearing your browser history and cache.',
    colors: "#a94442",
    });
}

function custom_error_popup(text) {
    $('#loading_modal').modal('hide');
    $.fn.cornerpopup({
    variant: 9,
    header: "Error!",
    text2: text,
    colors: "#a94442",
    });
}

function link_copied(){
    $.fn.cornerpopup({
        variant: 10,
        timeOut: 7000,
        closeBtn: 0,
        width: "150px",
        content: "<h3 style='text-align:center; color:#4D80E4'>Link Copied</h3>",
        padding: "0px",
        bgColor: '#f8f8ff6b'
});
}

function custom_success_popup(text) {
$('#loading_modal').modal('hide');
    $.fn.cornerpopup({
    variant: 9,
    header: "Success!",
    text2: text,
    colors: "#4D80E4",
        timeOut: 10000
    });
}

function update_notification_count(){
    $.ajax({
        type: 'GET',
        url: '/notification_count',
        success: function (response) {
            if(response['status'] === 'success'){
                if (response['number'].toString() === '0'){
                    $('#notification_count').remove()
                }else{
                    $('#notification_count').html(response['number'])
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
$(document).on('click', '.notifications .icon_wrap', function () {
    $(this).parent().toggleClass("active");
})

$(document).on('click', '.unread_indicator', function (e) {
    e.preventDefault()
    var element = $(this)
    var parent = $(this.parentElement)
    $.ajax({
        type: 'GET',
        url: '/read_notification/' + parent.attr('id').split('_')[1],
        success: function (response) {
            if(response['status'] === 'success'){
                element.remove()
                parent.removeClass('unread_n')
                if($('.unread_n').length === 0){
                    $('#all_notifications_read').remove()
                }
                update_notification_count()
            }else{
                error_popup()
            }
        },
        error: function () {
                error_popup()
        }
    })


})

$(document).on('click', '.notify_data', function () {
    var element = $(this).parent()
    if(!element.hasClass('unread_n')){
        window.location.pathname = element.attr('link')
    }else{
         $.ajax({
        type: 'GET',
        url: '/read_notification/' + element.attr('id').split('_')[1],
        success: function (response) {
            if (response['status'] === 'success') {
                element.removeClass('unread_n')
                if($('.unread_n').length === 0){
                    $('#all_notifications_read').remove()
                }
                document.location.pathname = element.attr('link')
            } else {
                error_popup()
            }
        },
        error: function () {
            error_popup()
        }
    })
    }
})



$(document).ready(function () {
    $('.date-picker').each(function () {
            $(this).datepicker({
                buttonImage: "static/images/gilad.png",
                buttonImageOnly: true,
                showButtonPanel: true,
            })
    })
})

 $(document).ready(function () {
    $(".selectpicker").selectpicker();
    navigator.sayswho= (function(){
    var ua= navigator.userAgent, tem,
    M= ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];
    if(/trident/i.test(M[1])){
        tem=  /\brv[ :]+(\d+)/g.exec(ua) || [];
        return 'IE '+(tem[1] || '');
    }
    if(M[1]=== 'Chrome'){
        tem= ua.match(/\b(OPR|Edge?)\/(\d+)/);
        if(tem!= null) return tem.slice(1).join(' ').replace('OPR', 'Opera').replace('Edg ', 'Edge ');
    }
    M= M[2]? [M[1], M[2]]: [navigator.appName, navigator.appVersion, '-?'];
    if((tem= ua.match(/version\/(\d+)/i))!= null) M.splice(1, 1, tem[1]);
    return M.join(' ');
})();
    var browser = navigator.sayswho.toString().split(' ')[0]
     if(browser !== 'Chrome' && browser !== 'Safari' && browser !== 'Firefox'){
         custom_error_popup('ilmjtcv.com is not optimized for your browser. You may experience discoloration and errors while interacting with our features. We recommend using Google Chrome, Safari, or Firefox.')
     }
  });

$(document).on('click', '.bootstrap-select', function () {
$(this).toggleClass("open");
})





function make_moments() {
    $('.flask-moment').each(function () {
        if($(this).attr('data-format') === 'fromNow(0)'){
            $(this).text(moment($(this).attr('data-timestamp').toString(), "YYYY-MM-DDTHH:mm:ssZ").fromNow())
        }else{
            var format = $(this).attr('data-format').split("'")[1].split("'")[0].toString()
            $(this).text(moment($(this).attr('data-timestamp').toString(), "YYYY-MM-DDTHH:mm:ssZ").format(format))
        }
        this.classList = []
        this.style.display = 'inline-block'
    })
    $('.snippet').each(function () {
        $(this).html($(this).text())
    })
    $('[data-toggle="popover"]').popover({
                trigger : 'hover'
    });

}

$(document).on('click', '#all_notifications_read', function () {
    $('#loading_modal').modal({backdrop: 'static', keyboard: false})
    var element = $(this)
    $.ajax({
        type: 'GET',
        url: '/read_notifications_all',
        success: function (response) {
            if(response['status'] === 'success'){
                $('.unread_n').each(function () {
                    $(this).removeClass('unread_n')
                })
                $('.unread_indicator').each(function () {
                    $(this).remove()
                })
                element.remove()
                 $('#loading_modal').modal('hide')
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

