/*
 *  CSRF GENERATION
 */
//------------------------------------------------------------------------------
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
//------------------------------------------------------------------------------

/* ============================================================================
 * Clear all data button
 * ===========================================================================*/
$('#clear-button').click(function() {
	$.ajax({
		type: "GET",
		url: "clear/",
		success: function(xhr){
			myplot.updateOptions({"file":xhr.csv,
					"labels":xhr.labels});
			
			$(".modelbar").remove()
			$("#model-div").append(xhr.new_labels);
			
		}
	});
});

/* ============================================================================
 * Log-scale button
 * ===========================================================================*/
$('#log-button').click(function() {
	var islog = myplot.getOption("logscale");
	myplot.updateOptions({"logscale":!islog})
});
		
/* ============================================================================
 * y-axis selection options
 * ===========================================================================*/
$("body").on('change',"#id_x",function(){
	var xval = $(this).find(":selected").val();
	$.ajax({
		type: "POST",
		url: "axes/y-selector/",
		data: {"xval":xval},
		success: function(returned_html){
			console.log(returned_html);
			$("#id_y").html(returned_html);
		}
	});
});	
		
/* ============================================================================
 * Visibility buttons
 * ===========================================================================*/
/*
$("body").on('click',".visibility",function(){
	var label = $(this).closest(".modelbar").attr("id");
	if ($(this).html().indexOf("glyphicon-eye-open") >= 0){
		$(this).html("<span class='glyphicon glyphicon-eye-close'></span>");
		var val = false;
	}else{
		$(this).html("<span class='glyphicon glyphicon-eye-open'></span>");
		var val = true;
	}
	var id = myplot.getLabels().indexOf(label);

	
	myplot.setVisibility(id-1,val)
});
*/
/* ============================================================================
 * Deletion buttons
 * ===========================================================================*/
$("body").on('click',".delete",function(){
	var label = $(this).closest(".modelbar").attr("id");
	console.log("Box id: "+label);
	$.ajax({
		type: "POST",
		url: "del/",
		data: {"label":label},
		success: function(j){
			myplot.updateOptions({"file":j.csv,
				"labels":j.labels});
			
			// Remove the modelbar
			$(jq(label)).remove();
			
		}
	});
});
/* ============================================================================
 * Modal submission event
 * ===========================================================================*/
var formAjaxSubmit = function(form, modal,id) {
    $(form).submit(function (e) {
        e.preventDefault();
        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function (xhr, ajaxOptions, thrownError) {
            	if ( $(xhr).find('.has-error').length > 0 ) {
            		$(modal).find('.modal-body').html(xhr);
            		formAjaxSubmit(form, modal,id);
            	} else {
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
	                	$(jq(id)).find(".model-label").html(xhr.new_labels);
	                	$(jq(id)).attr("id",xhr.new_labels);
	                };
            	};
            },
            error: function (xhr, ajaxOptions, thrownError) {
             	//probably actually want to redirect to 500 page here	
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

/* ============================================================================
 * edit model button(s)
 * ===========================================================================*/
$("body").on('click',".edit",function(){
	var id = $(this).closest(".modelbar").attr("id");
    
	$('#form-modal-body').load('edit/'+id+"/", function () {
        $('#form-modal').modal('toggle');
        formLoaded();
        formAjaxSubmit('#form-modal-body form', '#form-modal',id);
    });
});

/* ============================================================================
 * add model button(s)
 * ===========================================================================*/
$("body").on('click',".add",function(){
	var id = $(this).closest(".modelbar").attr("id");
    
	$('#form-modal-body').load('add/'+id+"/", function () {
        $('#form-modal').modal('toggle');
        formLoaded();
        formAjaxSubmit('#form-modal-body form', '#form-modal',null);
    });
});
   
/* ============================================================================
 * Initial Plot
 * ===========================================================================*/
$(document).ready(function(){
	$.ajax({
		url: "reload/",
		success: function (xhr, ajaxOptions, thrownError) {
			myplot = new Dygraph(document.getElementById("image-div"), 
					xhr.csv,
					{
					labels:xhr.labels,
					legend: 'false',
					logscale: true,
					yAxisLabelWidth:80,
					});
			$("#model-div").append(xhr.new_labels);
		},
	});
});

function jq( myid ) {
	return "#" + myid.replace( /(:|\.|\[|\])/g, "\\$1" );
}
