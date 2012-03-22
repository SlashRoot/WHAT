//This file covers the actual function of logging in via ajax.
//The login button in the upper right triggers this function.

$(function(){

		
	//This is pretty straightforward.
		$('#widgetLogout').click(function(){
			$('#loadingAnimationSmall').fadeIn(500);							
			$.post('/bareLogout', {'logMeOut': 1}, function(data){
				if (data == 1) {
					//logout();
					window.location.replace('/');
				}
			});
			
										})	
			
{% comment %}

	$("#loginLabel").click(function(){
		//Change this to change the effect time.
		var transTime = 500;
		$("#mainLoginForm").fadeOut(transTime, function(){
								$("#mainLoginForm").toggleClass("expanded");
							});
		$("#mainLoginForm").fadeIn(transTime);
	});		
	$('#widgetLoginSubmit').click(function(){
											
		$('#loadingAnimationSmall').fadeIn(500); //Fade in the animation	
		
{% endcomment %}									


		username = $('#widgetLoginUsername').val();
		password = $('#widgetLoginPassword').val();
		
		
		//Post to bareLogin view, which was written for this purpose alone.
		$.post("/bareLogin", { username: username, password: password },
			function(data){
						if (data == 1) {
									//This widget assumes that this function will disable the loading animation.
									//See the loggedIn() function in main_landing.html
									//loggedIn();
									window.location.replace('/iam');
									}
	
				
						if (data == 2) {
									//This widget assumes that this function will disable the loading animation.
									//See askPurpose.js
									askPurpose();
									}
	
						
						}, "json");
	

		
	});

});