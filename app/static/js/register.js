function check_length(element){
    if(element.value.length > 7){
            return true
        }else{
            return false
        }
}

function check_num(element){
    function checkStringForNumbers(input){
            let str = String(input);
            for( let i = 0; i < str.length; i++){
                if(!isNaN(str.charAt(i))){           //if the string is a number, do the following
                    return true;
                }
            }
        }
    if(checkStringForNumbers(element.value)){
        return true
    }else{
        return false
    }
}

function check_username(element) {
    if (!element.value.includes('@') && !element.value.includes(' ')){
        if(element.value.length > 0){
            return true
        }else{
            return false
        }
    }else{
        return false
    }
}

function check_email(element) {
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(element.value)) {
        return true
    } else {
        return false
    }
}

function checker_(){
        var l = check_length(document.getElementById('g_password'));
        var n = check_num(document.getElementById('g_password'));
        var u = check_username(document.getElementById('g_username'));
        var e = check_email(document.getElementById('g_email'));
        var btn = document.getElementById('g_submit');
        var name = document.getElementById('g_name').value.length > 1;

        if (l  && n && name && u && e){
                btn.removeAttribute('disabled')
        }else{
            btn.setAttribute('disabled', '')
        }
    }

function recruiter_checker_(){
        var e = check_email(document.getElementById('g_email'));
        var cn = document.getElementById('g_company').value.length > 1;
        var cw = document.getElementById('g_link').value.length > 1;
        var btn = document.getElementById('recruiter_submit');
        var name = document.getElementById('g_name').value.length > 1;
        var link = isURL($('#g_link').val());

        if (cn && e && cw && name && link){
                btn.removeAttribute('disabled')
            return true
        }else{
            btn.setAttribute('disabled', '')
            return false
        }
}

function verify_unique(){
    var username = document.getElementById('g_username');
    var email = document.getElementById('g_email');
    var content = {'u': username.value, 'e': email.value};
    var form = document.getElementById('form_r');
    var button = document.getElementById('g_submit');

    $.ajax({
        type: 'POST',
        url: "/auth/verify_unique",
        data: content,
        success: function (data) {
            if (data['e'] && data['u']){
                $(form).submit()
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
                button.setAttribute('disabled', '')
            }
        },
        error: function () {
            error_popup()
        }
    });
}

function isURL(str) {
   regexp =  /^(?:(?:https?|ftp):\/\/)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:\/\S*)?$/;
  return regexp.test(str);
}

$(document).on('change blur focus keyup keydown click', '#g_link', function () {
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

$(document).on('blur keyup change click','#form_r',  function () {
    checker_()
})

$(document).on('blur keyup change click','#recruiter_register',  function () {
    recruiter_checker_()
})

$(document).on('blur keyup change click', '.register-email', function (){
    if (this.previousElementSibling !== null && this.previousElementSibling.classList.contains('email-validator')){
        if (this.value.length === 0) {
            if (this.previousElementSibling != null){
                    $('.email-validator').remove()
                }
            $('label[for="g_email"]').removeClass('special_label_incorrect');
            $(this).removeClass('special_input_incorrect');
        }
        if (check_email(this)){
            if (this.previousElementSibling != null){
                    $('.email-validator').remove()
                }
           $('label[for="g_email"]').removeClass('special_label_incorrect');
            $(this).removeClass('special_input_incorrect');
        }
    }else{
        if (this.value.length > 0){
            if (check_email(this) === false) {
                $('label[for="g_email"]').addClass('special_label_incorrect');
                $(this).addClass('special_input_incorrect');
                $(this).before('<div class="email-validator val"><div class="row"><div class="col-sm-12 validator" id="type-e">Must be an email</div></div></div>');
            }
        }
    }
});

$(document).on('blur keyup change click', '.register-password', function () {
    if (this.previousElementSibling !== null && this.previousElementSibling.classList.contains('password-validator')){
        // if above element exists
        if (this.value.length > 0) {
            // if password is not empty
            var l = check_length(this);
            var n = check_num(this);
            if (l && n){
                // if all requirements met
                $('.password-validator').remove()
                $('label[for="g_password"]').removeClass('special_label_incorrect');
                $(this).removeClass('special_input_incorrect')
            }

        }else{
            $('.password-validator').remove()
            $('label[for="g_password"]').removeClass('special_label_incorrect');
            $(this).removeClass('special_input_incorrect');
        }

    }else {
        if (this.value.length > 0){
            var l = check_length(this);
            var n = check_num(this);
            if (l && n){}else{
                $(this).addClass('special_input_incorrect');
                $('label[for="g_password"]').addClass('special_label_incorrect');
                $(this).before('<div class="row"></div><div class="password-validator val"><div class="row"><div class="col-sm-12 validator" id="type-l">8 characters and 1 number</div></div></div>')
            }
        }
    }});

$(document).on('blur keyup change click', '.register-username', function (){
    if (this.previousElementSibling !== null && this.previousElementSibling.classList.contains('username-validator')){
        if(this.value.length === 0) {
            if (this.previousElementSibling != null){
                    $('.username-validator').remove()
                }
            $('label[for="g_username"]').removeClass('special_label_incorrect');
            $(this).removeClass('special_input_incorrect');
        }
        if (check_username(this)){
            if (this.previousElementSibling != null){
                    $('.username-validator').remove()
            }
            $('label[for="g_username"]').removeClass('special_label_incorrect');
            $(this).removeClass('special_input_incorrect');
        }
    }else{
        if (this.value.length > 0){
            if (check_username(this) === false) {
                $('label[for="g_username"]').addClass('special_label_incorrect');
                $(this).addClass('special_input_incorrect');
                $(this).before('<div class="username-validator val"><div class="row"><div class="col-sm-12 validator" id="type-u">No spaces or ampersands</div></div></div>');
            }
        }
    }
});

$(document).on('keyup', '.register-username', function (){
    if (this.classList.contains('non-unique')){
        $(this).removeClass('non-unique');
        $('#username_not_unique').remove()
        $('label[for="g_username"]').removeClass('non_unique_text');
    }
});

$(document).on('keyup', '.register-email', function (){
    if (this.classList.contains('non-unique')){
        $(this).removeClass('non-unique');
        $('#email_not_unique').remove()
        $('label[for="g_email"]').removeClass('non_unique_text');
    }
});

$(document).on('click', '#recruiter_search_test', function () {
    if(document.getElementById('profile') != null){
        custom_error_popup('You must logout to create a recruiter profile')
    }else{
        reload('/auth/partnership_inquiry_')
    }
});

$(document).on('click', '#submit_login', function (e) {
    e.preventDefault();
    if ($('#username').val().length > 2 && $('#password').val().length > 3){
        $('#login_form').submit()
    }else{
        error_popup()
    }
})

$(document).on('blur keyup change click', 'input[type=text], textarea',function () {
    if (this.previousElementSibling !== null && this.previousElementSibling.classList.contains('char-counter')){
        this.previousElementSibling.textContent = this.value.length.toString() + '/' + $(this).attr('maxlength')
        if (this.value.length == $(this).attr('maxlength')){
            this.previousElementSibling.classList.add('char-reached')
        }else{
            if (this.value.length == 0){
                this.previousElementSibling.remove()
            }else{
            this.previousElementSibling.classList.remove('char-reached')
        }}

    }else {
        if (this.hasAttribute('maxlength')  && this.value.length > 0){
        $(this).before('<p class="char-counter">' + this.value.length.toString() + '/' + $(this).attr('maxlength') + '</p>')
    }}});

function close_register() {
    $('#register_modal').modal('toggle');
}

$(document).on('click', '#recruiter_submit', function () {
 if(recruiter_checker_()){
     $('#loading_modal').modal({backdrop: 'static', keyboard: false})
     $.ajax({
         type: 'POST',
         url: '/auth/partnership_inquiry_submit',
         data: $('#recruiter_register').serialize(),
         success: function (response) {
            if(response['status'] === 'success'){
                $('#recruiter_register').find("input[type=text], textarea, input[type=email]").val("");
                custom_success_popup(response['message'])
                setTimeout(function () {
                        document.location.reload()
                }, 7000)
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

$(document).on('submit', '#login_form, #form_r', function (e) {
    e.preventDefault();
    var form = $(this);
    var url = form.attr('action')
    $('#loading_modal').modal({backdrop: 'static', keyboard: false})
    $.ajax({
           type: "POST",
           url: url,
           data: form.serialize(), // serializes the form's elements.
           success: function(data) {
               if(data['status'] === 'success'){
                   window.location = data['url']
               }else{
                   if(form.attr('id') === 'login_form'){
                       $('#loading_modal').modal('hide');
                       $('#incorrect_password').css({'display':'block'})
                       $('label[for="password"]').removeClass('blurred')
                       $('#password').val('')
                   }else{
                       custom_error_popup(data['message'])
                   }
               }
           },
            error: function () {
                error_popup()
            }
         });

})