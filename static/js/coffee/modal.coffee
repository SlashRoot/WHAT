$ ->
  $("#services").click ->
    $("#membership-modal").dialog("close", {show:"fade"});
    $("#contact-modal").dialog("close", {show:"fade"});
    $("#services-modal").dialog({ height: 346, width: 200,  position: [360, 27], show: "fade", buttons: { Ok: function() { $( this ).dialog( "close" ); } }});
    return false;
    
  $("#membership").click ->
    $("#services-modal").dialog("close", {show:"fade"});
    $("#contact-modal").dialog("close", {show:"fade"});
    $("#membership-modal").dialog({ height: 346, width: 200,  position: [360, 27], show: "fade" });
    return false;

  $("#contact").click ->
    $("#membership-modal").dialog("close", {show:"fade"});
    $("#services-modal").dialog("close", {show:"fade"});
    $("#contact-modal" ).dialog({ height: 346, width: 200,  position: [360, 27], show: "fade" });
    return false;
