$(function(){

	/* ************** EXTRAPOLATION FIELDS *************************** */
	// Make the initial state of the extrapolate fields correct
	if($('#id_extrapolate').not(':checked')){
		$('#div_id_k_begins_at').hide();
		$('#div_id_k_ends_at').hide();
	};
	if($('#id_extrapolate').is(':checked')){
		$('#div_id_k_begins_at').show();
		$('#div_id_k_ends_at').show();
	};
	
	// Make the state of the extrapolate fields correct upon change
	$('#id_extrapolate').change(function(){
		$('#div_id_k_begins_at').toggle();
		$('#div_id_k_ends_at').toggle();
	});
	
	
	/* ************* COSMOLOGY FIELDS ****************************** */
	// Initially HIDE the file upload (since transfer_file
	// default is WMAP7) and set all the relevant cosmo
	// params to readonly.
	if ($('#id_co_transfer_file').val() != 'custom'){ // Use != 'custom' here for if default cosmo changes.
		$('#div_id_co_transfer_file_upload').hide();
		// Only set those parameters that affect transfer function to readonly
		$("#id_cp_omegab").prop("readonly",true);
		$("#id_cp_omegac").prop("readonly",true);
		$("#id_cp_omegav").prop("readonly",true);
		$("#id_cp_w_lam").prop("readonly",true);
		$("#id_cp_omegan").prop("readonly",true);
		$("#id_cp_H0").prop("readonly",true);
		$("#id_cp_reion__optical_depth").prop("readonly",true);
	}

	
	//Actions for when the transfer_file setting is changed.
	$('#id_co_transfer_file').change(function(){
		//When changed to something other than custom
		if ($(this).val() != 'custom')
		{
			//First, set the cosmo params to the correct values
			if($(this).val() == "transfers/WMAP7_transfer.dat" )
			{
				//Mean dens, crit dens, w and omega_neutrino are the same for all
				$("#id_cp_label").val('WMAP7')
				$('#id_cp_omegav').val('0.728')
				$('#id_cp_omegac').val('0.226')
				$('#id_cp_omegab').val('0.0455')
				$('#id_cp_n').val('0.967')
				$('#id_cp_sigma_8').val('0.81')
				$('#id_cp_H0').val('70.4')
				$('#id_cp_reion__optical_depth').val('0.085')
			}
			if($(this).val() == "transfers/WMAP5_transfer.dat" )
			{
				//Mean dens, crit dens, w and omega_neutrino are the same for all
				$("#id_cp_label").val('WMAP5')
				$('#id_cp_omegav').val('0.723')
				$('#id_cp_omegac').val('0.231')
				$('#id_cp_omegab').val('0.0459')
				$('#id_cp_n').val('0.962')
				$('#id_cp_sigma_8').val('0.817')
				$('#id_cp_H0').val('70.2')
				$('#id_cp_reion__optical_depth').val('0.088')
			}
			if($(this).val() == "transfers/GiggleZ_transfer.dat" )
			{
				//Mean dens, crit dens, w and omega_neutrino are the same for all
				$("#id_cp_label").val('GiggleZ')
				$('#id_cp_omegav').val('0.726')
				$('#id_cp_omegac').val('0.228')
				$('#id_cp_omegab').val('0.0456')
				$('#id_cp_n').val('0.960')
				$('#id_cp_sigma_8').val('0.812')
				$('#id_cp_H0').val('70.5')
				$('#id_cp_reion__optical_depth').val('0.088')
			}
			if($(this).val() == "transfers/WMAP3_transfer.dat" )
			{
				//Mean dens, crit dens, w and omega_neutrino are the same for all
				$("#id_cp_label").val('WMAP3')
				$('#id_cp_omegav').val('0.732')
				$('#id_cp_omegac').val('0.224')
				$('#id_cp_omegab').val('0.044')
				$('#id_cp_n').val('0.947')
				$('#id_cp_sigma_8').val('0.776')
				$('#id_cp_H0').val('70.4')
				$('#id_cp_reion__optical_depth').val('0.0867')
			}
			if($(this).val() == "transfers/WMAP1_transfer.dat" )
			{
				//Mean dens, crit dens, w and omega_neutrino are the same for all
				$("#id_cp_label").val('WMAP1')
				$('#id_cp_omegav').val('0.710')
				$('#id_cp_omegac').val('0.243')
				$('#id_cp_omegab').val('0.047')
				$('#id_cp_n').val('0.99')
				$('#id_cp_sigma_8').val('0.9')
				$('#id_cp_H0').val('72.0')
				$('#id_cp_reion__optical_depth').val('0.10')
			}
			if($(this).val() == "transfers/Millennium_transfer.dat" )
			{
				//Mean dens, crit dens, w and omega_neutrino are the same for all
				$("#id_cp_label").val('Millennium')
				$('#id_cp_omegav').val('0.750')
				$('#id_cp_omegac').val('0.205')
				$('#id_cp_omegab').val('0.045')
				$('#id_cp_n').val('1')
				$('#id_cp_sigma_8').val('0.9')
				$('#id_cp_H0').val('73.0')
				$('#id_cp_reion__optical_depth').val('0.10')
			}
			
			if($(this).val() == "transfers/PLANCK_transfer.dat" )
			{
				//Mean dens, crit dens, w and omega_neutrino are the same for all
				$("#id_cp_label").val('PLANCK')
				$('#id_cp_omegav').val('0.6817')
				$('#id_cp_omegac').val('0.2678')
				$('#id_cp_omegab').val('0.049')
				$('#id_cp_n').val('0.9619')
				$('#id_cp_sigma_8').val('0.8347')
				$('#id_cp_H0').val('67.04')
				$('#id_cp_reion__optical_depth').val('0.0925')
			}
			
			if($(this).val() == "transfers/WMAP9_transfer.dat" )
			{
				//Mean dens, crit dens, w and omega_neutrino are the same for all
				$("#id_cp_label").val('WMAP9')
				$('#id_cp_omegav').val('0.7181')
				$('#id_cp_omegac').val('0.236')
				$('#id_cp_omegab').val('0.0461')
				$('#id_cp_n').val('0.9646')
				$('#id_cp_sigma_8').val('0.817')
				$('#id_cp_H0').val('69.7')
				$('#id_cp_reion__optical_depth').val('0.08')
			}
			
			//HIDE upload, and set the cosmo params affecting both transfer and mf to readonly
			$('#div_id_co_transfer_file_upload').hide();
			$("#id_cp_omegab").prop("readonly",true);
			$("#id_cp_omegac").prop("readonly",true);
			$("#id_cp_omegav").prop("readonly",true);
			$("#id_cp_w_lam").prop("readonly",true);
			$("#id_cp_omegan").prop("readonly",true);
			$("#id_cp_H0").prop("readonly",true);
			$("#id_cp_reion__optical_depth").prop("readonly",true);
		}
		
		//When changed to custom
		if ($(this).val() == 'custom')
		{
			//Show upload, and make cosmo params editable.
			$('#div_id_co_transfer_file_upload').show();
			$("#id_cp_omegab").removeAttr("readonly");
			$("#id_cp_omegac").removeAttr("readonly");
			$("#id_cp_omegav").removeAttr("readonly");
			$("#id_cp_w_lam").removeAttr("readonly");
			$("#id_cp_omegan").removeAttr("readonly");
			$("#id_cp_reion__optical_depth").removeAttr("readonly");
			$("#id_cp_H0").removeAttr("readonly");
		}
	});
	
	//Change plotted image to whatever user clicks on
	$('#id_plot_choice').change(function(){
		var src = '../'+$(this).val()+'.png';
	        $('#the_image').attr('src',src);

	    //Also change download link
	    if($('#id_download_choice').val()=='pdf-current'){
	    	var newlink = '../'+$('#id_plot_choice').val()+'.pdf';
	    	$('a#plot_download').attr('href',newlink);
	    }
	});

	//Change download link depending on what user wants to download
	$('#id_download_choice').change(function(){
		if($(this).val() == 'pdf-current'){
			var newlink = '../'+$('#id_plot_choice').val()+'.pdf'
			$('a#plot_download').attr('href',newlink);
		}
		if($(this).val() == 'pdf-all'){
			var newlink = "plots.zip"
			$('a#plot_download').attr('href',newlink);
		}
		if($(this).val() == 'ASCII-mass'){
			var newlink = "mass_function.dat"
			$('a#plot_download').attr('href',newlink);
		}
		if($(this).val() == 'ASCII-k'){
			var newlink = "power_spectrum.dat"
			$('a#plot_download').attr('href',newlink);
		}
		if($(this).val() == 'parameters'){
			var newlink = "parameters.dat"
			$('a#plot_download').attr('href',newlink);
		}
	});
});