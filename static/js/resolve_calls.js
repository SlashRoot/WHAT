// Compiled from resolve_calls.coffee located in /static/js/coffee 

(function() {
  $(function() {
    return $(".resolve-check").click(function() {
      var row;
      row = $(this).parent().parent();
      return $.post('/comm/resolve_call/', {
        call_id: $(this).attr("id").split("_")[1],
        complete: $(this).is(':checked')
      }, function(data) {
        if (data === "2") {
          row.css({
            'background-color': 'gray'
          });
        }
        if (data === "1") {
          return row.css({
            'background-color': 'green'
          });
        }
      });
    });
  });
}).call(this);
