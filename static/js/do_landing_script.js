
$('#hiddenMagneticCard').keyup(function() {
  clearTimeout($.data(this, 'timer'));
  var wait = setTimeout(authenticateByCard, 500);
  $(this).data('timer', wait);
});

function authenticateByCard() {
  $.post("/mellon/authenticate_card/", {rawString: "" + $('#hiddenMagneticCard').val() + ""}, function(data){
   		if (data == 1){
   			window.location.reload();
   		}
    });
 
}


//For the moment, when the user logs in or out, we'll refresh.  

function logout() {
window.location.reload();
}

function loggedIn() {
window.location.reload();
}

//Traverse through the verbs every 10 seconds.


var verbTraverseCounter = 1;

var secondsForTimeout = 60; //Pause for one minute
lengthOfDelay = 4000; //Delay for ten seconds between traversal
var timeoutTimer;
var traversalTimer;
var secondsOnClock;
var startedTraversing = 0;

//The countdown itself

function countdown() {
	secondsOnClock--;
	if(secondsOnClock > 0) {
		if (secondsOnClock < 51) {
	    	$('#counter').html(resumeMessage + ' in <b>'+secondsOnClock+'</b>');
	    }
	} else {
		// If the user is authenticated, a timeout will log them out.  If not, it will just resume traversing.
		if (startedLoggedIn) {
			$("#widgetLogout").click();
		} else {
			goTraversing();
		}

	    clearInterval(timeoutTimer);
	}
}


function verbTraverse() {

	var verbToClick = $('#verbClick_' + verbTraverseCounter).click();
		
	verb_id = verbToClick.attr('verb_id');
	verb_name = verbToClick.attr('verb_name');
	
	//Now we'll click on the first task in the verb.
	
	taskTraverseCounter = 1;
		
	verbTraverseCounter = verbTraverseCounter + 1;
	
	if (verbTraverseCounter > totalNumberOfVerbs) {
		verbTraverseCounter = 1	//Go back to #1 if we have exceeded the total number of verbs.
	}
		
}

//Do the actual traversal
function timedTaskTraverse()

{
	var taskBox = $('.taskCounter_' + taskTraverseCounter, $('#taskList'));
	var taskToClick = $('.navButton.taskName', taskBox).click(); //Click on the next Task in the list.
	taskTraverseCounter = taskTraverseCounter + 1;


	if (taskTraverseCounter > totalNumberOfTasks){
		verbTraverse();
	}

}

function beginTimeoutTimer() {
    secondsOnClock = secondsForTimeout;
    clearInterval(traversalTimer);
    clearInterval(timeoutTimer);
	timeoutTimer = setInterval(countdown, 1000);
}


function goTraversing() {
	$('#counter').html('Traversing');
	timedTaskTraverse();
	traversalTimer=setInterval('timedTaskTraverse()', lengthOfDelay);
	
	//whenever we are traversing we want to allow a user to swipe a card
	$('#hiddenMagneticCard').val('');
	$('#hiddenMagneticCard').focus();
}

var hoverToPauseTraversing = function pauseTraversing(length) {
	$('#counter').html('Paused');
	beginTimeoutTimer();			
}


$(function() {
	if (startedLoggedIn) {
		beginTimeoutTimer();
	} else {
		verbTraverse();		
	}
});

$('.content').bind('mousemove', hoverToPauseTraversing);



//   PUSH STUFF


$(function(){ 

    stomp = new STOMPClient();
    stomp.onopen = function() {
    };
    stomp.onclose = function(c) { alert('Lost Connection, Code: ' + c);};
    stomp.onerror = function(error) {
        alert("Error: " + error);
    };
    stomp.onerrorframe = function(frame) {
        alert("Error: " + frame.body);
    };
    stomp.onconnectedframe = function() {
        stomp.subscribe("/do/new_tasks");        
    };
    
    
    
    stomp.onmessageframe = function(frame) {
    	wholeFrame=frame;
    	dest = frame.headers['destination'];
       	      	
       	var task_box_dict = $.parseJSON(frame.body);
       	var task_id = task_box_dict.task_id;
       	var box_html = task_box_dict.box;
       	var verb_id = task_box_dict.verb_id;
       	var container = $('#taskBoxContainer_' + task_id);
       	
       	verbBoxClick = $('[verb_id=' + verb_id + ']');

       	if (traversalTimer != undefined) {
       		navOpen(verbBoxClick);
       	}
       	
       	
       	
       	container.fadeOut(function(){
       		container.html(box_html);
       	});
       	
       	container.show('drop', 2000)

	        
    };
    stomp.connect('localhost', 61613);
});

//And some specific binding stuff.
$(function(){

	$('body').ajaxComplete(function() {
		//window.location.reload();
	})

	$('.markResolved').click(function markResolvedClick() {
		task_id = $(this).attr('task');
		$('#markCompleted').attr('url', '/do/mark_completed/' + task_id + '/');
		$('#markAbandoned').attr('url', '/do/mark_abandoned/' + task_id + '/');
	});
})

function refreshTask(post_data) {
	task_id = post_data['task_id']; //We need to know both the ID of the task...
	box = post_data['box']; //And the HTML that we're putting in the task box.
	
	$('#taskBoxContainer_' + task_id).slideUp(function(){ //First, slide up the whole container.
		taskBoxContainer = $('#taskBoxContainer_' + task_id).html(box); //Now fill in the HTML
		taskBoxContainer.slideDown(function(){ //Now slide down the newly filled container....
			$('[exclude="taskBoxes"]', taskBoxContainer).click(); //And once the sliding is done, click down the relevant nav buttons.
    		$('[shows="taskChildren"]', taskBoxContainer).click();
		});
    	
	});
    
  
}