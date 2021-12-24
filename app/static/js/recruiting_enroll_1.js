$(document).ready(function () {
    $('#loading_modal').modal({backdrop: 'static', keyboard: false});
    $.get('/enroll_resume_upload', {}, function (response) {
        for (i = 0; i < response['institutions'].length; i++){
            $('#institutions_confirm').append('<li class="institution_attended" id="' + response['institutions'][i]['id'].toString() +'">' + response['institutions'][i]['name'].toString() + '<button style="margin-left: 15px" type="button" class="close remove_institution">\n' +
                '                                  <span aria-hidden="true" style="color: red">&times;</span>\n' +
                '                                </button></li>');
        }
        for (i = 0; i < response['employers'].length; i++){
            $('#employers_confirm').append('<li class="employer_attended" id="' +  response['employers'][i]['id'].toString() +'">' + response['employers'][i]['name'].toString() + '<button style="margin-left: 15px" type="button" class="close remove_employer">\n' +
                '                                  <span aria-hidden="true" style="color: red">&times;</span>\n' +
                '                                </button></li>');
        }
        $('#loading_modal').modal('hide');
        $('#recruiting_enroll_confirm').modal({backdrop: 'static', keyboard: false});
    })
});