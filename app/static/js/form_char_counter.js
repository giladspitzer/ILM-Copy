$('input[type=text], textarea').on('blur keyup change click', function () {
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
