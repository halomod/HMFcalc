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
$("body").on('click',".visibility",function(){
	var id = Number($(this).closest(".modelbar").attr("id"));
	if ($(this).html().indexOf("glyphicon-eye-open") >= 0){
		$(this).html("<span class='glyphicon glyphicon-eye-close'></span>");
		var val = false;
	}else{
		$(this).html("<span class='glyphicon glyphicon-eye-open'></span>");
		var val = true;
	}
	
	myplot.setVisibility(id,val)
});

/* ============================================================================
 * Deletion buttons
 * ===========================================================================*/
$("body").on('click',".delete",function(){
	var id = Number($(this).closest(".modelbar").attr("id"));
	console.log("Box id");
	console.log(id);
	$.ajax({
		type: "POST",
		url: "del/",
		data: {"id":id},
		success: function(j){
			myplot.updateOptions({"file":j.csv,
				"labels":j.labels});
			// All models before this one stay the same
			// This model is deleted
			// Any models after it have updated ID's
			$(".modelbar").each(function(i){
				console.log("Loop i");
				console.log(i);
				if (i==id){
					$(this).remove();
					console.log("Removing...");
					console.log(i);
				}
				if (i>id){
					var thisid = Number($(this).attr("id"));
					$(this).attr("id",(i-1).toString());
					console.log("Set"+thisid.toString() +"to"+(i-1).toString());
					
				}
			});
		}
	});
});
/* ============================================================================
 * Modal submission event
 * ===========================================================================*/
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

/* ============================================================================
 * edit model button(s)
 * ===========================================================================*/
$("body").on('click',".edit",function(){
	var id = $(this).closest(".modelbar").attr("id");
    
	$('#form-modal-body').load('edit/'+id+"/", function () {
        $('#form-modal').modal('toggle');
        formLoaded();
        formAjaxSubmit('#form-modal-body form', '#form-modal',Number(id));
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
					});
			$("#model-div").append(xhr.new_labels);
		},
	});
});
