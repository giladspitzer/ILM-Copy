function post_validator() {
    btn = document.getElementById('submit');
    title = document.getElementById('title');
    post = document.getElementById('body');
    if (title.value.length > 4 && post.value.length > 4){
        btn.removeAttribute('disabled')
    }else{
        btn.setAttribute('disabled', '')
    }
}

$('input[type=text], textarea').on('blur keyup change click', function () {
    post_validator()
})
