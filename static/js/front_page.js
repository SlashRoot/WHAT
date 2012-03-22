function modalPurpose($this) {

    }

$(function(){
	
	
	$('#sale').click(function postSale (){
		$.post('/pos/productSale/', {product:$('#product').val()}, function(data){
			alert(data);
			
			
		})
		
		
	});
	
	
     $('body').delegate('.bubbleLink', 'click', function(){
        $this = $(this);
        action = $this.attr('action'); //Pop, Crumb, Link, or Modal
        
        bubble = $this.parent().parent(); //The bubble in which this link resides

        //Crumb - we are assuming that all are script-based for the moment.  We'll add ajax versions later.
        if (action == 0)
            {
                 data = $this.attr('launch'); //The menu name of the menu to be launched
                 
                 //These all get DOM elements assigned
                 oldMenu = menu //The previous menu (Will be in the outer ring right now)
                 menu = bubble.parent() //The name of the current menu (In the inner ring, moving to outer)
                 newMenu = $('#' + data); //New menu that is emerging to be the inner ring
                 
                 background = $('.backgroundLayer', menu); //The background layer of this menu
                 newBackground = $('.backgroundLayer', newMenu);
                 
                 
                 //Cycles - to make the backgrounds cycle through colors
                 cycle = background.attr('cycle'); //Cycle number of this background
                 newCycle = parseInt(cycle) + 1
                 if (newCycle == 3) {newCycle = 1;}
                 
                 
                 //Darken this bubble
                 bubble.addClass('crumb');
                 
                 //Make all the bubbles that weren't clicked semi transparent
                 //$('.loggedInBubble', menu).not(bubble).addClass('kindaTransparent');//css('opacity', '0.5');
                 
                 //Explode the old outer menu
                 oldMenu.fadeOut(1000);
                 
                 //Change this menu and its background layer from inner to outer
                 $('.loggedInBubble', menu).switchClass('inner', 'outer', 300);
                 background.switchClass('inner', 'outer', 300);
                 
                 
                 //Fade in the new inner menu
                 newBackground.addClass('cycle_' + newCycle).attr('cycle', newCycle)
                 newMenu.fadeIn();         
                 
                 
                 
                 
                 
                //TODO: The lines below were supposed to get the bubbles to rotate.  
                //If you can make it happen, rock out.
                         //$('.loggedInBubble', menu).each(function(){
                                                
                                                //id = $(this).attr('id').split('_')[1]
                                                
                                                // if (id == 1) {
                                                //             id = 4
                                                //           }
                                                //$(this).switchClass('bubble_' + id, 'bubble_' + (id-1), 200 );
                                                //$(this).unbind();
                 
                                                    //})         
                 
             }

        //Static Pop
        if (action == 1) 
        {
            
            width=data.split('_')[0]
            height=data.split('_')[1]
            
            bubble.css('width', width + 'px').css('height', height + 'px');
            $('.bubbleContent', bubble).fadeIn()              
                    
        }
        
        //Modal
        if (action == 3)
        {
            data = $this.attr('data'); //The menu name of the menu to be launched
            $('#' + data).fadeIn();
         
         }
        
       
        
        
        //Ajax-based crumb
          
          
          //$('.loggedInBubble').switchClass('inner', 'outer', 300);
                                               
                                               })
          
                                
          
                                      })






