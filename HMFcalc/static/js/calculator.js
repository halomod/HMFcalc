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
			//Update Plot
			myplot.updateOptions({"file":xhr.csv,
					"labels":xhr.labels});
			
			//Update modelbar
			$(".modelbar").remove()
			$("#model-div").append(xhr.new_labels);
			
			//Update table
			$("#scalar-values").html(xhr.table);
		},
		error: function(xhr, ajaxOptions, thrownError){
			window.location.replace("/500.html");
		}
	});
});

/* ============================================================================
 * Log-scale button
 * ===========================================================================*/
$('#log-button').click(function() {
	$(this).button("toggle");
	islog = $(this).hasClass("active");
	myplot.updateOptions({"logscale":islog})
});

/* ============================================================================
 * Compare button
 * ===========================================================================*/
$('#compare-button').click(function() {
	$(this).button("toggle");
	iscompare = $(this).hasClass("active");
	console.log("This button is active:"+iscompare);
	
	//Now re-draw
	$.ajax({
		type: "POST",
		url: "switch_compare/",
		//data: {"label":label},
		success: function(xhr){
			myplot.updateOptions({"file":xhr.csv,
					"labels":xhr.labels});
		},
		error: function(xhr, ajaxOptions, thrownError){
			window.location.replace("/500.html");
		}
		
	});
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
		},
		error: function(xhr, ajaxOptions, thrownError){
			window.location.replace("/500.html");
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
 * Primary buttons
 * ===========================================================================*/
$("body").on('click',".primary",function(){
	var label = $(this).closest(".modelbar").attr("id");
	
	//Find the previous primary button and make it not primary
	$(".modelbar").each(function(index){
		if ($(this).find(".primary").html().indexOf("glyphicon-star ") >= 0){
			$(this).find(".primary").html("<span class='glyphicon glyphicon-star-empty'></span>");
		}
	});
	
	//Make this button primary
	if ($(this).html().indexOf("glyphicon-star-empty") >= 0){
		$(this).html("<span class='glyphicon glyphicon-star '></span>");
	}
	
	
	//Now re-draw
	$.ajax({
		type: "POST",
		url: "compare_to/",
		data: {"label":label},
		success: function(xhr){
			myplot.updateOptions({"file":xhr.csv,
					"labels":xhr.labels});
		},
		error: function(xhr, ajaxOptions, thrownError){
			window.location.replace("/500.html");
		}
		
	});
});

/* ============================================================================
 * Deletion buttons
 * ===========================================================================*/
$("body").on('click',".delete",function(){
	//Make sure this isn't the primary one
	if ($(this).closest(".modelbar").find(".primary").html().indexOf("glyphicon-star ") >= 0){
		bootstrap_alert("#form_errors"," Cannot remove primary model",1500);
	}else{
		var label = $(this).closest(".modelbar").attr("id");
		$.ajax({
			type: "POST",
			url: "del/",
			data: {"label":label},
			success: function(j){
				myplot.updateOptions({"file":j.csv,
					"labels":j.labels});
				
				// Remove the modelbar
				$(jq(label)).remove();
				
				//Remove the table entry
				$("#scalar-values").html(xhr.table);
				
			},
			error: function(xhr, ajaxOptions, thrownError){
				window.location.replace("/500.html");
			}
			
		});
	}
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
	                console.log("here");
	                // Update the plot
	                myplot.updateOptions({'file':xhr.csv,
	                	"labels":xhr.labels,
	                	"xlabel":xhr.xlabel,
	                	"ylabel":xhr.ylabel});
	                console.log("here 2");
	                //Update the table of plots
	                $("#scalar-values").html(xhr.table);
	                
	                //Put new models in modelbars
	                if (id==null){
		                $("#model-div").append(xhr.new_labels);
	                }else{
	                	$(jq(id)).find(".model-label").html(xhr.new_labels);
	                	$(jq(id)).attr("id",xhr.new_labels);
	                };
	                console.log("here 3");
            	};
            },
            error: function (xhr, ajaxOptions, thrownError) {
            	console.log("error");
            	console.log(thrownError);
             	//probably actually want to redirect to 500 page here	
            	window.location.replace("/500");
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
 * Initialise
 * ===========================================================================*/
$(document).ready(function(){
	$.ajax({
		url: "reload/",
		success: function (xhr, ajaxOptions, thrownError) {
			// Update Plot
			myplot = new Dygraph(document.getElementById("image-div"), 
					xhr.csv,
					{
					legend: 'false',
					logscale: true,
					yAxisLabelWidth:80,
					//title: "<h3>Plot</h3>",
					});
			myplot.updateOptions({
				"xlabel":xhr.xlabel,
				"ylabel":xhr.ylabel,
			});

			// Update Model bars
			$("#model-div").append(xhr.new_labels);
			
			// Update Table
			$("#scalar-values").html(xhr.table);
		},
		error: function(xhr, ajaxOptions, thrownError){
			window.location.replace("/500");
		}
	});
});

function jq( myid ) {
	return "#" + myid.replace( /(:|\.|\[|\])/g, "\\$1" );
}

/* ============================================================================
 * Alert message
 * ===========================================================================*/
function bootstrap_alert(elem, message, timeout) {
	console.log(elem);
	console.log(message);
  $(elem).show().html('<div class="alert"><span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span><button type="button" class="close" onclick="$(\'.alert\').hide()" aria-hidden="true">&times;</button><span>'+message+'</span></div>');

  if (timeout || timeout === 0) {
    setTimeout(function() { 
      $(elem).alert().hide();
    }, timeout);    
  }
};


/* ============================================================================
 * Table Editing Modal
 * ===========================================================================*/
var tableAjaxSubmit = function(form, modal) {
    $(form).submit(function (e) {
        e.preventDefault();
        
        
        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function (xhr, ajaxOptions, thrownError) {
            	if ( $(xhr).find('.has-error').length > 0 ) {
            		$(modal).find('.modal-body').html(xhr);
            		tableAjaxSubmit(form, modal);
            	} else {
	            	// First close the modal
	                $(modal).modal('toggle');
	                //Now refresh the table
	                $("#scalar-values").html(xhr.table);
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
 * Tab edit modal click
 * ===========================================================================*/
$("body").on('click',"#tabedit",function(){
    $('#tabedit-modal-body').load('/hmf-calculator/table-edit/', function () {
        $('#tabedit-modal').modal('toggle');
        tableAjaxSubmit('#tabedit-modal-body form', '#tabedit-modal');
    });
});

$("body").on('click',"#checkall-table",function(){
   if($(this).hasClass("active")) {
	   $('#div_id_quantities input:checkbox').removeAttr('checked');
	   $(this).removeClass("active")
   } else {
	   $('#div_id_quantities input:checkbox').prop('checked','checked');
	   $(this).addClass("active")
   };
   
});