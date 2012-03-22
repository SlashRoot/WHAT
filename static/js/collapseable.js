$(function(){

	
	$('.collapsable .head.expanded').prepend('<span class="expand_button"><img src="/media/images/nav/collapse_minus.png" /> </span> ');
	
	$('.collapsable .head.collapsed').prepend('<span class="expand_button"><img src="/media/images/nav/collapse_arrow.png" /> </span> ').next().hide();
	
	$('.collapsable .head').click(function() {
		$(this).next().toggle('fast');
		
		return false;
	});
	
	
	$('.collapsable .head').toggle(function() {
	
    		$('.expand_button', this).html('<img src="/media/images/nav/collapse_arrow.png" /> ');
		  },
		  function () {
		    $('.expand_button', this).html('<img src="/media/images/nav/collapse_minus.png" /> ');
		  
		  });
	
	
	
});
