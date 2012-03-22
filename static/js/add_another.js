$(function(){
	
	$('body').delegate('.quickClone', 'click', function(){
				//Like clone() but with no need to deal with formset stuff.  Just for the simplest case.
				
				id = $(this).attr('id').split("_")[1];  //Get the ID of the button that was just clicked.
				original = $('#original_' + id); 		//Get the original form based on the ID of the button.  This will be the one we clone.
				clone = original.clone(true); 			//And here's the clone.
		
		        var num     = original.parent().children().size(); // how many "duplicatable" input fields we currently have
                var newNum  = new Number(num + 1);      // the numeric ID of the new input field being added
 
                // create the new element via clone(), and manipulate it's ID using newNum value
                var newElem = clone.attr('id', id + newNum);
 
                // manipulate the name/id values of the input inside the new element
                clone.find('input,select').attr('id', 'name' + newNum).attr('name', function(){
                
                return $(this).attr('name') + '-' + newNum;
                
                });
                
                clone.children('input').val("");
 
                // insert the new element after the last "duplicatable" input field
                $('div:last', original.parent().parent()).after(newElem);
                newElem.fadeIn();	
            
	});

	$('.clone').click(function(){
		id = $(this).attr('id').split("_")[1]; //Get the ID of the button that was just clicked.  It will be a number.
		original = $('#original_' + id); //Get the original form based on the ID of the button.  This will be the one we clone.
		clone = original.clone(true); //And here's the clone.
		prefix = $(this).attr('data'); //Get the prefix from the buttons - we'll use this to determine what formset this is from so we can increment it.
		management_counter = $('#id_' + prefix + '-TOTAL_FORMS', $('#management_forms')) //Get the management counter based on the prefix - this is how many forms we have in the formset. 
		$('#form_list').append( clone ); //Now we'll append the thing for real.
		last = $('input:last', original); //The very last input in the cloned element. <=- The old way.
		//counter = last.attr('id').split('-')[1]; //This will be the "0" in the above. <=- The old way.
		
		counter = management_counter.val(); 
		
		//Let's parse the ID a bit.  The ID will look like "id_Coconuts-0-amount" where Coconuts is the form prefix and amount is a field name.
				
		clone.attr('id', 'formClone_' + counter);
		
		clone.addClass('clonedForm');
		
		$('.counter', clone).html(counter);
		
		clone.slideDown();
		
		fields = $('input, select, textarea,', clone) //All the fields in the cloned set.
		//fields = all_fields.not('input:hidden'); //We don't want the first few hidden fields in each formset. (This line made sense when the management forms were here.  Now they play in their own div.)
		
		labels = $('label', clone);
		
		//First let's set their ID properly.
		fields.attr('id', function() {return this.id.split('-')[0] + "-" + counter + "-" + this.id.split('-')[2]});
		
		//...and while we're on the subject, let's set the ID of the 'total' field. 
		$('.formTotal', clone).attr('id', function() {return this.id.split('-')[0] + "-" + counter + "-" + this.id.split('-')[2]});
		
		//OK, now let's update the names of the fields. 
		fields.attr('name', function() {return this.name.split('-')[0] + "-" + counter + "-" + this.name.split('-')[2]});
		
		//And the 'for' field in labels
		labels.attr('for', function() {return this.htmlFor.split('-')[0] + "-" + counter + "-" + this.htmlFor.split('-')[2]});
		
		//Also, let's modify 'last', so that we'll have the right number next time.
		last.attr('id', function() {return this.id.split('-')[0] + "-" + counter + "-" + this.id.split('-')[2]});
		
		//...and update the number of forms in this formset.
		counter++;
		management_counter.val(counter);
	});
	
	$('#form_list').delegate('.xClose', 'click', function(){
		$(this).parent().parent().slideUp('slow', function() {
		$(this).remove();
		});
	});
	
})