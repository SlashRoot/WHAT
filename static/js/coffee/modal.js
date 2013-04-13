(function() {

  $(function() {
    $("#services").click(function() {
      $("#membership-modal").dialog("close", {
        show: "fade"
      });
      $("#contact-modal").dialog("close", {
        show: "fade"
      });
      $("#services-modal").dialog({
        height: 346,
        width: 200,
        position: [360, 27],
        show: "fade"
      });
      return false;
    });
    $("#membership").click(function() {
      $("#services-modal").dialog("close", {
        show: "fade"
      });
      $("#contact-modal").dialog("close", {
        show: "fade"
      });
      $("#membership-modal").dialog({
        height: 346,
        width: 200,
        position: [360, 27],
        show: "fade"
      });
      return false;
    });
    return $("#contact").click(function() {
      $("#membership-modal").dialog("close", {
        show: "fade"
      });
      $("#services-modal").dialog("close", {
        show: "fade"
      });
      $("#contact-modal").dialog({
        height: 346,
        width: 200,
        position: [360, 27],
        show: "fade"
      });
      return false;
    });
  });

}).call(this);
