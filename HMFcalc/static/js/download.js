var downloadAjaxSubmit = function(form, modal) {
    $(form).submit(function (e) {
        e.preventDefault();
        
        
        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function (xhr, ajaxOptions, thrownError) {
            	if ( $(xhr).find('.has-error').length > 0 ) {
            		$(modal).find('.modal-body').html(xhr);
            		formAjaxSubmit(form, modal);
            	} else {
	            	// First close the modal
	                $(modal).modal('toggle');
	                $("body").append("<iframe src='/hmf-calculator/data/' style='display: none;' ></iframe>");
            	}
            	return false;
            },
            error: function (xhr, ajaxOptions, thrownError) {
             	//probably actually want to redirect to 500 page here	
            	window.location.replace("/500.html");
          	}
          	
    	});
    	
	});
}

/* ============================================================================
 * Axes modal click
 * ===========================================================================*/
$('#download-button').click(function() {
	console.log("HEY HEY HEY")
    $('#download-modal-body').load('/hmf-calculator/download/', function () {
        $('#download-modal').modal('toggle');
        downloadAjaxSubmit('#download-modal-body form', '#download-modal');
    });
});

$("body").on('click',"#checkall",function(){
   if($(this).hasClass("active")) {
	   $('#div_id_m input:checkbox').removeAttr('checked');
	   $('#div_id_k input:checkbox').removeAttr('checked');
	   $(this).removeClass("active")
   } else {
	   $('#div_id_m input:checkbox').prop('checked','checked');
	   $('#div_id_k input:checkbox').prop('checked','checked');
	   $(this).addClass("active")
   };
   
});