function checker_(){
        var btn = document.getElementById('submit');
        var l = check_length(document.getElementById('password'));
        var n = check_num(document.getElementById('password'));
        var u = check_username(document.getElementById('username'));
        var p = document.getElementById('position_title').value.length > 2;
        var i = document.getElementById('industry_interest').value != 0 ;

        if (l && n && u && p && i){
                btn.removeAttribute('disabled')
        }else{
            btn.setAttribute('disabled', '')
        }
    }


$('form').on('blur keyup change click', function () {
    checker_()
})

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
                $('label[for="password"]').removeClass('special_label_incorrect');
                $(this).removeClass('special_input_incorrect')
            }

        }else{
            $('.password-validator').remove()
            $('label[for="password"]').removeClass('special_label_incorrect');
            $(this).removeClass('special_input_incorrect');
        }

    }else {
        if (this.value.length > 0){
            var l = check_length(this);
            var n = check_num(this);
            if (l && n){}else{
                $(this).addClass('special_input_incorrect');
                $('label[for="password"]').addClass('special_label_incorrect');
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
            $('label[for="username"]').removeClass('special_label_incorrect');
            $(this).removeClass('special_input_incorrect');
        }
        if (check_username(this)){
            if (this.previousElementSibling != null){
                    $('.username-validator').remove()
            }
            $('label[for="username"]').removeClass('special_label_incorrect');
            $(this).removeClass('special_input_incorrect');
        }
    }else{
        if (this.value.length > 0){
            if (check_username(this) === false) {
                $('label[for="username"]').addClass('special_label_incorrect');
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
        $('label[for="username"]').removeClass('non_unique_text');
    }
});