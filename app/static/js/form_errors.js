let errors = $('.has-error').parents('div.panel');
    errors.each(function(){
        this.style.display = 'block';
        this.previousElementSibling.classList.add('active')
    })