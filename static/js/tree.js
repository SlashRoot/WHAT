$(function(){

	$('.toggle_hidden_second_title').click(function(){
		$('#hidden_second_title').toggle();
	})

	$('#trunk').delegate('.growBranch', 'click', function(){
		var branch = $(this).attr('branch');	
		branchesToShow = $('.growFrom_' + branch);
		branchesToShow.fadeIn();
		
		$(this).parent().switchClass('normal', 'inverse', 600);
	});
	
	
	

});


//Keep the blog coolumn only a bit bigger than the blog content div. TODO: Move this somewhere more sensible.
$(function(){

$('.blogColumn').each(function(){
	 new_height = $('.blogContent', this)[0].offsetHeight + 10; 
	 $('.blogContainer', this).css('height', new_height);
	 })
})