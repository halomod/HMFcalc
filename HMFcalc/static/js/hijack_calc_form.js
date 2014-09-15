$(document).ready(function(){
	$('form').submit(function(event){
		// This is what Kon said to put in ;)
		var forminput = $('form').serializeArray();
		$.post( '/calculator/', forminput).success(function(response) {
			// response should be a csv data table
			myplot.updateOptions({'file':response}); 
					
        }); 
		
        // this should prevent the round trip to the server
        event.preventDefault();
        //return false;
	});
});