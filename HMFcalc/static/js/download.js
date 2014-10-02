var formAjaxSubmit = function(form, modal,id) {
    $(form).submit(function (e) {
        e.preventDefault();
        console.log("yeah here I am");
        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function (xhr, ajaxOptions, thrownError) {
            	if ( $(xhr).find('.has-error').length > 0 ) {
            		console.log("weird error");
            		$(modal).find('.modal-body').html(xhr);
            		formAjaxSubmit(form, modal);
            	} else {
            		console.log("success");
	            	// First close the modal
	                $(modal).modal('toggle');
	                
	                // Update the plot
	                myplot.updateOptions({'file':xhr.csv,
	                	"labels":xhr.labels,
	                	"xlabel":xhr.xlabel,
	                	"ylabel":xhr.ylabel});
	                
	                //Update the table of plots
	                if (id==null){
		                $("#model-div").append(xhr.new_labels);
	                }else{
	                	$(".modelbar").each(function(i){
	                		if (i==id){
	                			$(this).html(xhr.new_labels);
	                		}
	                	});
	                }

            	}
            	return false;
            },
            error: function (xhr, ajaxOptions, thrownError) {
             	//probably actually want to redirect to 500 page here	
            	console.log("Main Error");
            	console.log(xhr);
            	console.log(thrownError);
          	}
    	});
	});
}

/* ============================================================================
 * Axes modal click
 * ===========================================================================*/
$('#axes-button').click(function() {
    $('#axes-modal-body').load('/hmf-calculator/axes/', function () {
        $('#axes-modal').modal('toggle');
        formAjaxSubmit('#axes-modal-body form', '#axes-modal',null);
    });
});