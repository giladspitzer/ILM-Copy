function check_length(element){
    var _length = document.getElementById('type-l');
    if (_length != null){
    if(element.value.length > 8){
            _length.classList.remove('validator');
            _length.classList.add('validator-success');
            return true
        }else{
            _length.classList.add('validator');
            _length.classList.remove('validator-success');
            return false
        }}

}

function check_char(element){
    var _char = document.getElementById('type-c');
    if (_char != null){
    var pattern = new RegExp(/[~`!@#$%\^^&*+()_=\-\[\]\\';,/{}|\\":<>\?]/);
    if (pattern.test(element.value)){
            _char.classList.remove('validator');
            _char.classList.add('validator-success');
            return true
        }else{
            _char.classList.add('validator');
            _char.classList.remove('validator-success');
            return false
}
}}

function check_num(element){
    var _num = document.getElementById('type-n');
    if (_num != null){
        function checkStringForNumbers(input){
            let str = String(input);
            for( let i = 0; i < str.length; i++){
                if(!isNaN(str.charAt(i))){           //if the string is a number, do the following
                    return true;
                }
            }
        }

        if(checkStringForNumbers(element.value)){
            _num.classList.remove('validator');
            _num.classList.add('validator-success');
            return true
        }else{
            _num.classList.add('validator');
            _num.classList.remove('validator-success');
            return false
        }
}}

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

function check_username(element) {
    var _username = document.getElementById('type-u');
    if (element.value.length > 2 && !element.value.includes('@') && !element.value.includes(' ')){
        if (_username != null) {
            _username.classList.remove('validator');
            _username.classList.add('validator-success');
        }
        return true
    }else{
        if (_username != null) {
            _username.classList.add('validator');
            _username.classList.remove('validator-success');
        }
        return false
    }
}

function check_zip(element){
    var _zip = document.getElementById('type-z');

    if (!isNaN(element.value) && element.value.length > 3){
        if (_zip != null) {
            _zip.classList.remove('validator');
            _zip.classList.add('validator-success');
        }
        return true
    } else {
        if (_zip != null) {
            _zip.classList.add('validator');
            _zip.classList.remove('validator-success');
        }
        return false
    }
}


$('.register-password').on('blur keyup change click', function () {
    if (this.previousElementSibling !== null && this.previousElementSibling.classList.contains('password-validator')){
        // if above element exists
        if (this.value.length > 0) {
            // if password is not empty
            var checker = document.getElementById('password2');
            var l = check_length(this);
            var c = check_char(this);
            var n = check_num(this);
            if (l && c && n){
                // if all requirements met
                checker.removeAttribute('disabled');
            }else{
                checker.setAttribute('disabled', '');
                checker.value = '';
                if  (document.getElementById('type-m') != null) {
                    document.getElementById('type-m').remove();
                }
            }

        }else{
            this.previousElementSibling.remove();
        }

    }else {
        if (this.hasAttribute('maxlength')  && this.value.length > 0){
            $(this).before('<div class="password-validator val"><div class="row"></div><div class="col-sm-4 validator" id="type-l">Length > 8 </div><div class="col-sm-4 validator" id="type-n">1 number</div><div class="col-sm-4 validator" id="type-c">1 Special Character</div></div></div>')
            var checker1 = document.getElementById('password2');
        }
    }});


$('.register-password2').on('blur keyup change click', function () {
    if (this.previousElementSibling !== null && this.previousElementSibling.classList.contains('password-validator2')){
        if (this.value.length > 0){
            var pass = document.getElementById('password');
            check_match(pass.value, this.value)
        }else{
            this.previousElementSibling.remove()
        }

    }else {
        var password = document.getElementById('password');
        if (this.hasAttribute('maxlength')  && this.value.length > 0 && password.value.length > 0){
            $(this).before('<div class="password-validator2 val"><div class="row"></div><div class="col-sm-4"></div><div class="col-sm-4 validator" id="type-m">Matches Above</div><div class="col-sm-4"></div></div></div>')
        check_match(this.value, password.value)
        }
    }});


$('.register-zip').on('blur keyup change click', function () {
    if (this.previousElementSibling !== null && this.previousElementSibling.classList.contains('zip-validator')){
        // if above element exists
        check_zip(this);
        if (this.value.length === 0) {
            this.previousElementSibling.remove();
        }

    }else {
        if (this.value.length > 0 && isNaN(this.value)){
            $(this).before('<div class="zip-validator val"><div class="row"></div><div class="col-sm-1"></div><div class="col-sm-10 validator" id="type-z">Must be a zip code</div><div class="col-sm-1"></div></div></div>')
            check_zip(this)
        }
    }});


$('.register-username').on('blur keyup change click', function (){
    if (this.previousElementSibling.previousElementSibling !== null && (this.previousElementSibling.previousElementSibling.classList.contains('username-validator') || this.previousElementSibling.classList.contains('username-validator'))){
        check_username(this);
        if (this.value.length == 0) {
            this.previousElementSibling.remove()
        }
    }else{
        if (this.value.length > 0){
            $(this.previousElementSibling).before('<div class="username-validator val"><div class="row"></div><div class="col-sm-1"></div><div class="col-sm-10 validator" id="type-u">No spaces or ampersand character (>3)</div><div class="col-sm-1"></div></div></div>');
            check_username(this)
        }
    }
});