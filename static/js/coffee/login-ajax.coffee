$ ->
  $('#widgetLogout').click ->
    $('#loadingAnimationSmall').fadeIn(500)
    $.post '/bare_logout/',
      logMeOut:1
      (data) ->
        if data == 1
          # logout()
          window.location.replace('/')

  $('#widgetLogin').click ->
    username = $('#widgetLoginUsername').val()
    password = $('#widgetLoginPassword').val()

    $.post '/bare_login/',
      username: username
      password: password
      (data) ->
        if data == 0
          alert "Invalid username and/or password."
        if data == 1
          window.location.replace('/iam')
        if data == 2
          askPurpose()