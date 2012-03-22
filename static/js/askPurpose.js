
    $('#id_purpose').change(function(){
                           $('#submitPurpose').fadeIn()
                                       })
    
    $('#submitPurpose').click(function(){
                        purpose = $('#id_purpose').val()
                        $.post('/presence/tellPurpose', {purpose:purpose}, function(data) {
                                    if (data == 1) {
                                    loggedIn();
                                    }
                                    
                                    
                                        })
    });
    
    
