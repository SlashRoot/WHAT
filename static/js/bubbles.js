      $(function(){
                
            //Temporary to fix login - reintegrate at conveinence   
            $('#mainLogin').click(function(){
                            $('#mainLogin').removeClass('collapsed');
                            $('#mainLogin').addClass('expanded');
                                  })
            //End cheap terrible hack
            
            
                   
             $('.unselected').live('click',           
                function selectBubble() {
                           
                            //Fade out the old content.
                            $('.selected .smallCircleContent').fadeOut()
                          
                          //Switch the old class back to unselected
                          $('.selected').switchClass('selected', 'unselected'); 
                            
                            
                            //Make the previously selected content small.
                            if ( $('.selected').hasClass('smallCircle') ) {
                            $('.selected').animate({
                                            'padding-left':"-=15px",        
                                            marginLeft:"+=150px",
                                            marginTop:"+=75px",
                                            height:"60px",
                                            width: "60px",
                                            })
                           }
                          
                            
                          //For this object, add the selected class.
                          $(this).switchClass('unselected', 'selected');
 
                            
                            //Make this object big.
                           
                            if ( $(this).hasClass('smallCircle') ) {
                            $(this).animate({
                                            'padding-left':"+=15px",
                                            marginLeft:"-=150px",
                                            marginTop:"-=75px",
                                            height:"379px",
                                            width: "477px",            
                                            });
                            }
                            
                            //Fade in the content.
                            $(this).find('.smallCircleContent').fadeIn(4000);
                            
                            
                            
                            
                
                                            
                           
                }
            );    
                $('.unselected, .xClose').live('click',
                        function closeBubbles() {
                                                                             //Fade out the old content.
                            $('.selected .smallCircleContent').fadeOut()
                          
                          //Switch the old class back to unselected
                          $('.selected').switchClass('selected', 'unselected'); 
                                                                             //Make the previously selected content small.
                            if ( $('.selected').hasClass('smallCircle') ) {
                            $('.selected').animate({
                                            'padding-left':"-=15px",        
                                            marginLeft:"+=150px",
                                            marginTop:"+=75px",
                                            height:"60px",
                                            width: "60px",
                                            })
                           }
                            
                           //Hide any modals
                           $('.bigModal').fadeOut();
                          
                                                 }) 
                
            
        });
