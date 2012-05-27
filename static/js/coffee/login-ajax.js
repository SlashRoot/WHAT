(function() {
  $(function() {
    $('#widgetLogout').click(function() {
      $('#loadingAnimationSmall').fadeIn(500);
      return $.post('/bare_logout', {
        logMeOut: 1
      }, function(data) {
        if (data === 1) {
          return window.location.replace('/');
        }
      });
    });
    return $('#widgetLogin').click(function() {
      var password, username;
      username = $('#widgetLoginUsername').val();
      password = $('#widgetLoginPassword').val();
      return $.post('/bare_login', {
        username: username,
        password: password
      }, function(data) {
        if (data === 0) {
          alert("Invalid username and/or password.");
        }
        if (data === 1) {
          window.location.replace('/iam');
        }
        if (data === 2) {
          return askPurpose();
        }
      });
    });
  });
}).call(this);
