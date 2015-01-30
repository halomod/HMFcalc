var formLoaded = function(){
	// Call this function whenever the form is loaded.
	// It sets the appropriate values for cosmology and hides/shows certain bits
	
	if ($("#id_transfer_fit").val() == 'FromFile'){
		$('#div_id_transfer_file_upload').show();
	}else{
		$('#div_id_transfer_file_upload').hide();
	}
	
	transferFile($('#id_transfer_file').val());
	
};

var setParams = function(ov,oc,ob,n,s8,H0){
	$('#id_omegav').val(ov);
	$('#id_omegac').val(oc);
	$('#id_omegab').val(ob);
	$('#id_n').val(n);
	$('#id_sigma_8').val(s8);
	$('#id_H0').val(H0);
};

var transferFile = function(tfile_val){
	if (tfile_val != 'custom')
	{
		$('#div_id_transfer_fit').hide();
		$('#div_id_transfer_file_upload').hide(); // for when changed BACK to non-custom
		$("#id_omegab").prop("readonly",true);
		$("#id_omegac").prop("readonly",true);
		$("#id_omegav").prop("readonly",true);
		$("#id_H0").prop("readonly",true);
		
		
		//Set the cosmo params to the correct values
		if(tfile_val == "transfers/WMAP7_transfer.dat" )
		{
			setParams('0.728','0.226','0.0455','0.967','0.81','70.4');
		}
		if(tfile_val == "transfers/WMAP5_transfer.dat" )
		{
			setParams('0.723','0.231','0.0459','0.962','0.817','70.2');
		}
		if(tfile_val == "transfers/GiggleZ_transfer.dat" )
		{
			setParams('0.726','0.228','0.0456','0.960','0.812','70.5');
		}
		if(tfile_val == "transfers/WMAP3_transfer.dat" )
		{
			setParams('0.732','0.224','0.044','0.947','0.776','70.4');
		}
		if(tfile_val == "transfers/WMAP1_transfer.dat" )
		{
			setParams('0.710','0.243','0.047','0.99','0.9','72.0');
		}
		if(tfile_val == "transfers/Millennium_transfer.dat" )
		{
			setParams('0.750','0.205','0.045','1.0','0.9','73.0');
		}		
		if(tfile_val == "transfers/PLANCK_transfer.dat" )
		{
			setParams('0.6817','0.2678','0.049','0.9619','0.8347','67.04');
		}		
		if(tfile_val == "transfers/WMAP9_transfer.dat" )
		{
			setParams('0.7181','0.236','0.0461','0.9646','0.817','69.7');
		}
	}	
	//When changed to custom
	if (tfile_val == 'custom')
	{
		if($("#id_transfer_fit").val() =="FromFile"){
			$('#id_transfer_fit').val("CAMB");
		}
		$('#div_id_transfer_fit').show();
		$("#id_omegab").removeAttr("readonly");
		$("#id_omegac").removeAttr("readonly");
		$("#id_omegav").removeAttr("readonly");
		$("#id_H0").removeAttr("readonly");
	}
	
}
//Actions for when the transfer_file setting is changed.
$("body").on('change',"#id_transfer_file",function(){
	transferFile($(this).val());
});

$("body").on('change',"#id_transfer_fit",function(){
	if ($(this).val() == 'FromFile'){
		$('#div_id_transfer_file_upload').show();
	}else{
		$('#div_id_transfer_file_upload').hide();
	}
});

//Actions for when wdm_model is changed
$("body").on("change","#id_wdm_model",function(){
	if ($(this).val() == "Schneider13"){
		$("#id_filter").val("SharpK");	
	}
});





