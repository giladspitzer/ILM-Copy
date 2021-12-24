function check_username(element) {
    if (!element.value.includes('@') && !element.value.includes(' ')){
        return true
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


function check_location(country, city, zip) {
    if (country.value !== '235'){
        if (city.value.length > 2){
            return true
        }else{
            return false
        }
    }else{
        if (zip.value.length > 4){
            return true
        }else{
            return false
        }
    }
}


function verify_unique_values(){
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


function checker_(){
        var u = check_username(document.getElementById('g_username'));
        var e = check_email(document.getElementById('g_email'));
        var btn = document.getElementById('g_submit');
        var name = document.getElementById('g_name').value.length > 1;
        var location = check_location(document.getElementById('country'), document.getElementById('g_city'), document.getElementById('g_zip'))

        if ($form.serialize() !== origForm && name && u && e && location){
            btn.removeAttribute('disabled')
        }else{
            btn.setAttribute('disabled', '')
        }

    }

// function verify_unique(){
//     var username = document.getElementById('g_username');
//     var email = document.getElementById('g_email');
//     var content = {'u': username.value, 'e': email.value};
//     var form = document.getElementById('form_r');
//     var button = document.getElementById('g_submit');
//     $.ajax({
//         url: "/auth/verify_unique",
//         data: content,
//         success: function (data) {
//             if (data['e'] && data['u']){
//             $(form).submit()
//             }else{
//                 if (!data['e']){
//                     if (email.previousElementSibling.classList.contains('char-counter')){
//                         $(email.previousElementSibling.previousElementSibling).addClass('non_unique_text');
//                     }else{
//                         $(email.previousElementSibling).addClass('non_unique_text');
//                     }
//                     $(email).addClass('non-unique');
//                     if (email.nextElementSibling !== null) {
//                         if (email.nextElementSibling.id !== 'email_not_unique') {
//                             $(email).after('<div class="val" id="email_not_unique"><div class="row"><div class="col-sm-12 validator" id="type-unique">Email Already in Use</div></div></div>');
//                         }
//                     }else{
//                     $(email).after('<div class="val" id="email_not_unique"><div class="row"><div class="col-sm-12 validator" id="type-unique">Email Already in Use</div></div></div>');
//                 }}
//                 if (!data['u']){
//                     if (username.previousElementSibling.classList.contains('char-counter')){
//                         $(username.previousElementSibling.previousElementSibling).addClass('non_unique_text');
//                     }else{
//                         $(username.previousElementSibling).addClass('non_unique_text');
//                     }
//                     $(username).addClass('non-unique');
//                     if (username.nextElementSibling !== null) {
//                         if (username.nextElementSibling.id !== 'username_not_unique') {
//                             $(username).after('<div class="val" id="username_not_unique"><div class="row"><div class="col-sm-12 validator" id="type-unique">Username Already in Use</div></div></div>');
//                         }
//                     }else{
//                         $(username).after('<div class="val" id="username_not_unique"><div class="row"><div class="col-sm-12 validator" id="type-unique">Username Already in Use</div></div></div>');
//                     }
//                 }
//
//                 button.setAttribute('disabled', '')
//             }
//             },
//         error: function () {
//             error_popup()
//         }
//     })
//
// }

var $form = $('#form_r'),
origForm = $form.serialize();

$(document).on('blur keyup change click','#form_r',  function () {
    checker_()
})


$(document).on('blur keyup change click', '.register-username', function (){
    if (this.nextElementSibling !== null && this.nextElementSibling.classList.contains('username-validator')){
        if (this.value.length === 0) {
            if (this.nextElementSibling != null){
                    this.nextElementSibling.remove();
                }
            if (this.previousElementSibling.classList.contains('char-counter')){
                    $(this.previousElementSibling.previousElementSibling).removeClass('incorrect_text');
            }else{
                $(this.previousElementSibling).removeClass('incorrect_text');
            }
            $(this).removeClass('incorrect');
        }
        if (check_username(this)){
            if (this.nextElementSibling != null){
                    this.nextElementSibling.remove();
                }
            if (this.previousElementSibling.classList.contains('char-counter')){
                    $(this.previousElementSibling.previousElementSibling).removeClass('incorrect_text');
            }else{
                $(this.previousElementSibling).removeClass('incorrect_text');
            }
            $(this).removeClass('incorrect');
        }
    }else{
        if (this.value.length > 0){
            if (check_username(this) === false) {
                if (this.previousElementSibling.classList.contains('char-counter')){
                    $(this.previousElementSibling.previousElementSibling).addClass('incorrect_text');
                }else{
                    $(this.previousElementSibling).addClass('incorrect_text');
                }
                $(this).addClass('incorrect');
                $(this).after('<div class="username-validator val"><div class="row"><div class="col-sm-12 validator" id="type-u">No spaces or ampersands</div></div></div>');
            }
        }
    }
});

$(document).on('keyup', '.register-username', function (){
    if (this.classList.contains('non-unique')){
        $(this).removeClass('non-unique');
        $('#username_not_unique').remove()
        if (this.previousElementSibling.classList.contains('char-counter')){
            $(this.previousElementSibling.previousElementSibling).removeClass('non_unique_text');
        }else{
            $(this.previousElementSibling).removeClass('non_unique_text');
         }

    }
});

$(document).on('keyup', '.register-email', function (){
    if (this.classList.contains('non-unique')){
        $(this).removeClass('non-unique');
        $('#email_not_unique').remove()
        if (this.previousElementSibling.classList.contains('char-counter')){
            $(this.previousElementSibling.previousElementSibling).removeClass('non_unique_text');
        }else{
            $(this.previousElementSibling).removeClass('non_unique_text');
         }

    }
});


$(document).on('blur keyup change click', '.register-email', function (){
    if (this.nextElementSibling !== null && this.nextElementSibling.classList.contains('email-validator')){
        if (this.value.length === 0) {
            if (this.nextElementSibling != null){
                    this.nextElementSibling.remove();
                }
            if (this.previousElementSibling.classList.contains('char-counter')){
                    $(this.previousElementSibling.previousElementSibling).removeClass('incorrect_text');
            }else{
                $(this.previousElementSibling).removeClass('incorrect_text');
            }
            $(this).removeClass('incorrect');
        }
        if (check_email(this)){
            if (this.nextElementSibling != null){
                    this.nextElementSibling.remove();
                }
            if (this.previousElementSibling.classList.contains('char-counter')){
                    $(this.previousElementSibling.previousElementSibling).removeClass('incorrect_text');
            }else{
                $(this.previousElementSibling).removeClass('incorrect_text');
            }
            $(this).removeClass('incorrect');
        }
    }else{
        if (this.value.length > 0){
            if (check_email(this) === false) {
                if (this.previousElementSibling.classList.contains('char-counter')){
                    $(this.previousElementSibling.previousElementSibling).addClass('incorrect_text');
                }else{
                    $(this.previousElementSibling).addClass('incorrect_text');
                }
                $(this).addClass('incorrect');
                $(this).after('<div class="email-validator val"><div class="row"><div class="col-sm-12 validator" id="type-e">Must be an email</div></div></div>');
            }
        }
    }
});


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

