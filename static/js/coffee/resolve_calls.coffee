$ ->
  $(".resolve-check").click ->
    row = $(this).parent().parent()
    $.post '/comm/resolve_call/',
      call_id: $(this).attr("id").split("_")[1]
      complete: $(this).is(':checked')
      (data) ->
        if data == "2"
          row.css({'background-color':'gray'})
        if data == "1"
          row.css({'background-color':'green'})