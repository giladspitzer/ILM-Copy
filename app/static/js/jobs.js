
$(document).ready(function () {
    var autocomplete;
    autocomplete = new google.maps.places.Autocomplete((document.getElementById('city')), {
        types: ['(cities)'],
    });

    google.maps.event.addListener(autocomplete, 'place_changed', function () {
        var near_place = autocomplete.getPlace();
    });
});

$(document).on('change click', '.checkbox', function () {
    if (document.getElementById('l_specific').checked){
        $('#l_specific_true').css({'display':'block'})
    }else{
        $('#l_specific_true').css({'display':'none'});
        $('#city').val('')
    }
})

$(document).on('change click blur hover keyup keydown', '#form', function () {
    var btn = $('#submit')
    if (document.getElementById('l_specific').checked){
        if (document.getElementById('title').value.length > 3 &&
            document.getElementById('industry').value !== '0' &&
            document.getElementById('city').value.length > 3){
            btn.removeAttr('disabled')
        }else{
            btn.attr('disabled', '')
        }
    }else{
        if (document.getElementById('title').value.length > 3 &&
            document.getElementById('industry').value !== '0'){
            btn.removeAttr('disabled')
        }else{
            btn.attr('disabled', '')
        }
    }
})

