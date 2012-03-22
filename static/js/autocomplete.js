function set_hidden_sibling(field, value) {
	sibling = $('#' + field.attr('id').replace("_lookup", "") );
	sibling.val(value);
	
	//Divert in the case of TaskPrototype - we want to do certain things if the TaskPrototype exists.
	//However, secondary task prototypes on the main do page need to not trigger this behaviour.
	if (this.criterion == "do.taskprototype" && field.prev().hasClass("topLevel") ) {

		id = this.elephant.split('_')[1] //Elephant looks like module_name.model_name.id
	
		$.get("/do/list_children_as_checkbox/", { "is_prototype": 1, "id": id },
	   	function(data){
	   	 $('#taskChildren').html(data);
	   }, "html");
	   
	   $('.taskPrototypeDoesNotExist').slideUp();
	   $('.taskPrototypeDoesExist').slideDown();	   
	   $('.taskDetails', '#ui-tooltip-modal-content').slideDown();
	   
	   $('#submitTask').fadeIn();
	   
	
	}
	try{
		found(); //Simple way of customizing function.  TODO: Expand to full observer pattern.
		}
	catch(err) {
	
	}
	
}
	
	$(function() {


        //First, well use the keydown function to make sure that the field always defaults to yellow inbetween every .css property change
        //Its a litte wet, but for good reason
        $('body').delegate('.autocompleteField', 'keydown', function autocompleteKeydown(){        
	        $(this).css("backgroundImage", "-moz-linear-gradient(top, #FFDF80, #DCDCDC)");
	        $(this).css("background", "-webkit-gradient(linear, left top, left bottom, from(#FFDF80), to(#dcdcdc))");	        
        });


		//This can be migrated to a task-specific JS file.
		$('body').delegate('#ui-tooltip-modal-content #id_name_lookup', 'keydown', function() {
			$('#ui-tooltip-modal-content .everythingButNameField').slideUp();
		});
		
		$('body').delegate('#ui-tooltip-modal-content #redirectToCreatePrototype', 'click', function() {
			var name = $('#id_name_lookup', $(this).parent().parent()).val();
			window.location.href = "/do/create_task_prototype/?name=" + name;
		}); 

        //Get the criterion
        $( ".autocompleteField, .mustBeUniqueField" ).focus(function(){
        criterion = $(this).attr('elephant_data');
        fieldChanging = $(this);
        });
        
    	//Whenever focus is gained by an autocomplete field, bind autocomplete to this element.
        $('body').delegate(".autocompleteField", 'focus', function(){
        	
	        $( this ).autocomplete({
	        	delay: 500,
	            minLength: 2,
	            
	            //Source is either a cache or our autocomplete view
	            source: function( request, response ) {
	                var term = request.term;
	                request.criterion = criterion;
	                
	                //request.lookup_type = this.element.attr('lookupType');  //Possibly deprecated?	                
	                
	                $.getJSON( "/utility/autocomplete/", request, 
	                		function( data, status ) {
	                			if (data[0] == undefined)
	                				{

	                				fieldChanging.css("backgroundImage", "-moz-linear-gradient(top, #D11D00, #DCDCDC)");
	                				fieldChanging.css("background", "-webkit-gradient(linear, left top, left bottom, from(#D11D00), to(#dcdcdc))");
	                				
	                				try{
	                					notFound(); //Simple way of customizing function.  TODO: Expand to full observer pattern.
	                					}
	                				catch(err){
	                				}
	                				
	                				//Divert in the case of TaskPrototype
									if (criterion == "do.taskprototype") { //TODO: Apparently we need to count on the global "criterion?!" pretty sad.
										$('.taskPrototypeDoesExist').slideUp();
										$('.taskPrototypeDoesNotExist').slideDown();								
									}
	                				
	                				}
	                			else
	                				{
		                				elephant = data[0].elephant; //Not sure why we'd set this to 0 here - are we just assuming that the first answer is the one they want until they challenge that assumption?		                				
	        
	                				}
			                    response(data);
	                });
	                
	            },
		 
		            
		            //When we select an option, the hidden field is populated.
		            select: function(event, ui){
	            	set_hidden_sibling($(this), ui.item.elephant + "___" + ui.item.label); //The elephant in the function here used to use the "elephant" variable defined in the else block above, but it's safer to take it directly from the elmenet each time.  It will be something like auth.user_420	            	
			        fieldChanging.css("backgroundImage", "-moz-linear-gradient(top, #4BAB5E, #DCDCDC)");
			          
			        },

		           search: function(event, ui) {
		           
		           fieldChanging.css("backgroundImage", "-moz-linear-gradient(top, #D16F00, #DCDCDC)");
		           fieldChanging.css("background", "-webkit-gradient(linear, left top, left bottom, from(#D16F00), to(#dcdcdc))");
		           
		           
		           },
		           
		           
		            //See http://stackoverflow.com/questions/3689405/making-jquery-uis-autocomplete-widget-actually-autocomplete
				    open: function(event, ui) {
				        
				        //What happens if there is only one result?
				        if ($(this).data("autocomplete").menu.element.find("li").size() == 1)
				        {				        
				        var current = this.value;
				        var suggested = $(this).data("autocomplete").menu.element.find("li:first-child a").text();
				
				        this.value = suggested;
				        this.setSelectionRange(current.length, suggested.length);
				        set_hidden_sibling($(this), elephant + "___" + suggested);
				        
				        //Change the background to green
				        fieldChanging.css("backgroundImage", "-moz-linear-gradient(top, #4BAB5E, #DCDCDC)"); 
				        fieldChanging.css("background", "-webkit-gradient(linear, left top, left bottom, from(#4BAB5E), to(#dcdcdc))");				        
				        }
				    },
	            
	            

			    
			});
        
        });
        
       
      //If someone goes way over the number of characters that's typical for an input, let's change it to a textarea.
      $('.autocompleteField').keyup(function(){
      	length = this.value.length;
      	if (length > 30) {
      		field_name = $(this).attr('name');
      		if (field_name) {
      			//We only want to go through with this if in fact the field has a name.
      			text = this.value;
      			new_id = 'sub_textarea_' + field_name
      			$(this).fadeOut();
      			newTextArea = $('<textarea id="' + new_id + '" cols="30" rows="5" name="' + field_name + '">' + text + '</textarea>').insertAfter(this);
      			$('#' + new_id).focus();
      			moveCaretToEnd(newTextArea[0]);
      			
      		}
      	} 
      	
      })
                
    });
    