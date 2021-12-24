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


function check_match(pass, check) {
    var _matches = document.getElementById('type-m');
    if (_matches != null){
    if (pass == check) {
        _matches.classList.remove('validator');
        _matches.classList.add('validator-success');
        return true
    } else {
        _matches.classList.add('validator');
        _matches.classList.remove('validator-success');
        return false
    }
}}


$('.reset-password').on('blur keyup change click', function () {
    if (this.nextElementSibling !== null && this.nextElementSibling.classList.contains('password-validator')){
        // if above element exists
        var checker = document.getElementById('password2');
        if (this.value.length > 0) {
            // if password is not empty
            var l = check_length(this);
            var n = check_num(this);
            if (l && n){
                checker.removeAttribute('disabled');
                // if all requirements met
                if (this.nextElementSibling != null){
                    this.nextElementSibling.remove();
                }
                $(this.previousElementSibling).removeClass('incorrect_text');
                $(this).removeClass('incorrect');
            }else{
                $(this.previousElementSibling).addClass('incorrect_text');
                $(this).addClass('incorrect');
                checker.setAttribute('disabled', '');
                checker.value = ''
                if  (document.getElementById('type-m') != null) {
                    document.getElementById('type-m').remove();
                }
            }
        }else{
            this.nextElementSibling.remove();
            $(this).removeClass('incorrect');
            $(this.previousElementSibling).removeClass('incorrect_text');
            checker.setAttribute('disabled', '');
                checker.value = ''
                if  (document.getElementById('type-m') != null) {
                    document.getElementById('type-m').remove();
                }
        }

    }else {
        var l = check_length(this);
        var n = check_num(this);
            if (l && n){}else {
                $(this.previousElementSibling).addClass('incorrect_text');
                $(this).addClass('incorrect');
                $(this).after('<div class="password-validator val"><div class="row"><div class="col-sm-12 validator" id="type-l">8 characters and 1 number</div></div></div>')
            }
    }});


$('.reset-password2').on('blur keyup change click', function () {
    if (this.nextElementSibling !== null && this.nextElementSibling.classList.contains('password-validator2')){
        if (this.value.length > 0){
            var pass = document.getElementById('password');
            if (!check_match(pass.value, this.value)){
                $(this.previousElementSibling).addClass('incorrect_text');
                $(this).addClass('incorrect');
            }else{
                $(this.previousElementSibling).removeClass('incorrect_text');
                $(this).removeClass('incorrect');
            }
        }else{
            this.nextElementSibling.remove()
            $(this.previousElementSibling).removeClass('incorrect_text');
            $(this).removeClass('incorrect');
        }

    }else {
        var password = document.getElementById('password');
        if (this.hasAttribute('maxlength')  && this.value.length > 0 && password.value.length > 0){
            $(this).after('<div class="password-validator2"><div class="row"></div><div class="col-sm-4"></div><div class="col-sm-4 validator" id="type-m">Matches Above</div><div class="col-sm-4"></div></div></div>')
        check_match(this.value, password.value)
        }
    }});


