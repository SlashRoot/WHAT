function navOpen(navButton) {		
	var set = navButton.attr('shows'); //Which set does this button show?
	var exclusive = navButton.attr('exclude');
	$('[exclusive=' + exclusive + '][set!=' + set + ']').hide(); //Hide all the elements that are exclusive with this one but in a different set.
	$('[exclude=' + exclusive + '][shows!=' + set + ']').removeClass('open') //Obviously any others are no longer open
				
	if (navButton.hasClass('open')) //This is already open - they must be trying to close it!
		{
		$('[set=' + set + ']').fadeOut(); //Fade out the elements in this set.
		$('.inverse[item=' + set + ']').switchClass('inverse', 'normal', 250); //And also revert the inversion.
		navButton.removeClass('open') //No longer open.
		
	} else { //It's not already open - let's open it.		
		navButton.addClass('open') //Now we know that this is open.
		//$('[exclusive!='']',) //TODO: Hide all elements that were visible only because the 'parent' nav button was clicked. 
		$('[set=' + set + ']').slideDown(); //Show only the elements in this set.
		$('.normal[item=' + set + ']').switchClass('normal', 'inverse', 250);
		$('.inverse[selected=' + exclusive + '][item!=' + set + ']').switchClass('inverse', 'normal', 250);
	}
}
		
		

$(function loadNavScript() {

		$( "#slider-range" ).slider({
			range: true,
			min: 0,
			max: 12,
			values: [ 0, 12],
			slide: function( event, ui ) {
				$( "#amount" ).val( ui.values[ 0 ] + " - " + ui.values[ 1 ] );
			}
		});



	$('.nav').delegate('.navButton', 'click', function loadFromClick(){
		navOpen($(this));
			
	});
		
	$('#taskList').delegate('.expandable', 'click', function clickOnTask (){
			$('.expansive', $(this)).slideDown();
		});
		
	$('#taskList').delegate('.expandable', 'mouseleave', function hoverOverTask (){
		$('.expansive', $(this)).slideUp();													
		});

});