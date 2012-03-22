function moveCaretToEnd(el) {
    if (typeof el.selectionStart == "number") {
        el.selectionStart = el.selectionEnd = el.value.length;
    } else if (typeof el.createTextRange != "undefined") {
        el.focus();
        var range = el.createTextRange();
        range.collapse(false);
        range.select();
    }
}


$(function(){

	$(".jp-jplayer").each(function(){
		var recording_id = $(this).attr('recording_id');
		$(this).jPlayer({
			ready: function () {
				$(this).jPlayer("setMedia", {
					mp3: $(this).attr('recording_url')
				})
				
			},
			swfPath: "/media/js/jPlayer",
			supplied: "mp3",
			solution: "flash, html",
			// preload: "auto",
			cssSelectorAncestor: "#jplayer-container_" + recording_id,
		});
	});



	
	$('#messageContainer').delegate('.messagesRow', 'click', function () {
    	$(this).fadeOut();
	})
	
	$(".sortableTable").tablesorter();
	
	$("abbr.timeago").timeago();
	
	$('.launchModal').qtip(
   {
      id: 'modal', // Since we're only creating one modal, give it an ID so we can style it
      content: {
         text: function(){
         var modal_id = this.attr('modal');
         return $('#' + modal_id);
         },
         
         title: {
            text: function(){
         var modal_id = this.attr('modal');
         return this.attr('modal');
         },
            button: true
         }
      },
      position: {
         my: 'center', // ...at the center of the viewport
         at: 'center',
         target: $(window)
      },
      show: {
         event: 'click', // Show it on click...
         solo: true, // ...and hide all other tooltips...
         modal: true // ...and make it modal
      },
      hide: false,
      style: {
      	classes: 'ui-tooltip-light ui-tooltip-rounded',
      	width:'420px',
      	}
   });
	
	
	$('body').delegate('.tooltip', 'mouseleave', function(){
		$(this).fadeOut('slow');	
	});
	
	$('body').delegate('.tooltipHover', 'hover', function tooltip_hover(){
		var tooltip = $(this).attr('tooltip');
		tooltipsToShow = $('.tooltipFor_' + tooltip);
		tooltipsToShow.fadeToggle(400, "linear");
	});
	
	

     $('body').delegate('.functionClick', 'click', function(){
            $this = $(this);
            f = $this.attr('function');
            window[f]($this);                                               
     });
	  
	  //Populate the big window with content.     
      $('body').delegate('.ajaxWindowClick', 'click', function(){
        
        //Start the animation
        $('#loadingAnimationLarge').fadeIn();
        $this = $(this);
        data = $this.attr('data');
        
        //Load the data in the big window and fade it in
        $('#centerWindow').load(data);
        $('#centerWindow').fadeIn();
        
        //Stop the animation
        $('#centerWindow').ajaxStop(function() {
            $('#loadingAnimationLarge').fadeOut();
        });
        
     })
     
      $('body').delegate('.submit', 'click', function(){
          if (!$(this).attr('form_element'))
     		{
     		form = $(this).parent();
     		}
     		
     else
         {
    	//if the form element is specified, find it.
     		form = $(this).attr('form_element')
         }
     
     form.submit();
     
      });
     
     
     
     
     //PLAIN GENERIC AJAX SUBMISSIONS
      $('body').delegate('.submitViaAjax', 'click', function(){
      //"submitViaAjax" buttons will automatically serialize the data in the form specified by the "form" attribute.
      //If none is specified, we assume that the parent element is the form.
       
       var clickedElement = $(this);
       
       if ($(this).attr('successCallback')) {
    	   var f = $(this).attr('successCallback');
       }
    	  
       if (!$(this).attr('form_element'))
       		{
       			var form = $(this).parent();
       		}
       		
       else
           {
           //if the form element is specified, find it.
       			var form = $(this).attr('form_element')
           }
       
       $('input', form).removeClass('invalidBorder');
       
       data = form.serialize();
       
       
     //Similarly, if there is a url atty specified, we POST to that URL.  
     //Otherwise, we POST to the generic handler.
 
       if (!$(this).attr('url')) 
	       {
	       //If there is no submit URL, assume the submission is generic
	       submitUrl = document.URL;
	       }
       else
           {
           //if there is a submit URL, extract it.
       		submitUrl = $(this).attr('url')
           }

       $.ajax({
               url: submitUrl,
               data: data,
               type: "POST",
               success: function(responseJSON){
               responseDICT = $.parseJSON(responseJSON)
               
               if (responseDICT['success']){
            	   form.find('input').val(''); //Clear inputs if ajax call is successful.
            	   
            	   if (f) {
	            	   //Some submission elements may specify a success callback function.  If so, let's execute it.
            		   window[f].apply(null, Array(responseDICT, clickedElement));
            	   }
                   
               }
               
               else {
               //If the submission is not successful, django will send us a list of fields that are bad, and we'll change add the class "invalidBorder" to them.
	               for (field in responseDICT['errors']) {
		               $('#id_' + dingbat[field]).addClass('invalidBorder');
	               }
               
               }
               
               }
               
               })
                                                               
       })       
})

function clearNotification(data, clickedElement) {
	clickedElement.parent().slideUp();
}