function checker_(){
        var l = check_length(document.getElementById('password'));
        var n = check_num(document.getElementById('password'));
        var m = check_match(document.getElementById('password').value, document.getElementById('password2').value);
        var btn = document.getElementById('submit');

        if (l && n && m){
                btn.removeAttribute('disabled')
        }else{
            btn.setAttribute('disabled', '')
        }
    }

$('form').on('blur keyup change click', function () {
    checker_()
})
