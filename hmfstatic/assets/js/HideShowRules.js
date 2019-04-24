$(function () {
    /* ************* COSMOLOGY FIELDS ****************************** */
    // Initially HIDE the file upload (since transfer_file
    // default is PLANCK) and set all the relevant cosmo
    // params to readonly.
    if ($('#id_transfer_file').val() != 'custom') { // Use != 'custom' here for if default cosmo changes.
        $('#div_id_transfer_file_upload').hide();
        $('#div_id_transfer_fit').hide(); // initially hide file upload AND transfer algorithm
        // Only set those parameters that affect transfer function to readonly
        $("#id_omegab").prop("readonly", true);
        $("#id_omegac").prop("readonly", true);
        $("#id_omegav").prop("readonly", true);
        $("#id_w_lam").prop("readonly", true);
        $("#id_omegan").prop("readonly", true);
        $("#id_H0").prop("readonly", true);
        $("#id_reion__optical_depth").prop("readonly", true);

    }


    //Actions for when the transfer_file setting is changed.
    $('#id_transfer_file').change(function () {
        //When changed to something other than custom
        if ($(this).val() != 'custom') {
            $('#div_id_transfer_fit').hide();
            $('#div_id_transfer_file_upload').hide(); // for when changed BACK to non-custom
            $("#id_omegab").prop("readonly", true);
            $("#id_omegac").prop("readonly", true);
            $("#id_omegav").prop("readonly", true);
            $("#id_w_lam").prop("readonly", true);
            $("#id_omegan").prop("readonly", true);
            $("#id_H0").prop("readonly", true);
            $("#id_reion__optical_depth").prop("readonly", true);


            //First, set the cosmo params to the correct values
            if ($(this).val() == "transfers/WMAP7_transfer.dat") {
                //Mean dens, crit dens, w and omega_neutrino are the same for all
                $("#id_label").val('WMAP7')
                $('#id_omegav').val('0.728')
                $('#id_omegac').val('0.226')
                $('#id_omegab').val('0.0455')
                $('#id_n').val('0.967')
                $('#id_sigma_8').val('0.81')
                $('#id_H0').val('70.4')
                $('#id_reion__optical_depth').val('0.085')
            }
            if ($(this).val() == "transfers/WMAP5_transfer.dat") {
                //Mean dens, crit dens, w and omega_neutrino are the same for all
                $("#id_label").val('WMAP5')
                $('#id_omegav').val('0.723')
                $('#id_omegac').val('0.231')
                $('#id_omegab').val('0.0459')
                $('#id_n').val('0.962')
                $('#id_sigma_8').val('0.817')
                $('#id_H0').val('70.2')
                $('#id_reion__optical_depth').val('0.088')
            }
            if ($(this).val() == "transfers/GiggleZ_transfer.dat") {
                //Mean dens, crit dens, w and omega_neutrino are the same for all
                $("#id_label").val('GiggleZ')
                $('#id_omegav').val('0.726')
                $('#id_omegac').val('0.228')
                $('#id_omegab').val('0.0456')
                $('#id_n').val('0.960')
                $('#id_sigma_8').val('0.812')
                $('#id_H0').val('70.5')
                $('#id_reion__optical_depth').val('0.088')
            }
            if ($(this).val() == "transfers/WMAP3_transfer.dat") {
                //Mean dens, crit dens, w and omega_neutrino are the same for all
                $("#id_label").val('WMAP3')
                $('#id_omegav').val('0.732')
                $('#id_omegac').val('0.224')
                $('#id_omegab').val('0.044')
                $('#id_n').val('0.947')
                $('#id_sigma_8').val('0.776')
                $('#id_H0').val('70.4')
                $('#id_reion__optical_depth').val('0.0867')
            }
            if ($(this).val() == "transfers/WMAP1_transfer.dat") {
                //Mean dens, crit dens, w and omega_neutrino are the same for all
                $("#id_label").val('WMAP1')
                $('#id_omegav').val('0.710')
                $('#id_omegac').val('0.243')
                $('#id_omegab').val('0.047')
                $('#id_n').val('0.99')
                $('#id_sigma_8').val('0.9')
                $('#id_H0').val('72.0')
                $('#id_reion__optical_depth').val('0.10')
            }
            if ($(this).val() == "transfers/Millennium_transfer.dat") {
                //Mean dens, crit dens, w and omega_neutrino are the same for all
                $("#id_label").val('Millennium')
                $('#id_omegav').val('0.750')
                $('#id_omegac').val('0.205')
                $('#id_omegab').val('0.045')
                $('#id_n').val('1')
                $('#id_sigma_8').val('0.9')
                $('#id_H0').val('73.0')
                $('#id_reion__optical_depth').val('0.10')
            }

            if ($(this).val() == "transfers/PLANCK_transfer.dat") {
                //Mean dens, crit dens, w and omega_neutrino are the same for all
                $("#id_label").val('PLANCK')
                $('#id_omegav').val('0.6817')
                $('#id_omegac').val('0.2678')
                $('#id_omegab').val('0.049')
                $('#id_n').val('0.9619')
                $('#id_sigma_8').val('0.8347')
                $('#id_H0').val('67.04')
                $('#id_reion__optical_depth').val('0.0925')
            }

            if ($(this).val() == "transfers/WMAP9_transfer.dat") {
                //Mean dens, crit dens, w and omega_neutrino are the same for all
                $("#id_label").val('WMAP9')
                $('#id_omegav').val('0.7181')
                $('#id_omegac').val('0.236')
                $('#id_omegab').val('0.0461')
                $('#id_n').val('0.9646')
                $('#id_sigma_8').val('0.817')
                $('#id_H0').val('69.7')
                $('#id_reion__optical_depth').val('0.08')
            }

        }

        //When changed to custom
        if ($(this).val() == 'custom') {
            $('#div_id_transfer_fit').show();
            $("#id_omegab").removeAttr("readonly");
            $("#id_omegac").removeAttr("readonly");
            $("#id_omegav").removeAttr("readonly");
            $("#id_w_lam").removeAttr("readonly");
            $("#id_omegan").removeAttr("readonly");
            $("#id_reion__optical_depth").removeAttr("readonly");
            $("#id_H0").removeAttr("readonly");
        }
    });

    $('#id_transfer_fit').change(function () {
        if ($(this).val() == 'FromFile') {
            $('#div_id_transfer_file_upload').show();
        }
    });

    //Change plotted image to whatever user clicks on
    $('#id_plot_choice').change(function () {
        var src = '../' + $(this).val() + '.png';
        $('#the_image').attr('src', src);

        //Also change download link
        if ($('#id_download_choice').val() == 'pdf-current') {
            var newlink = '../' + $('#id_plot_choice').val() + '.pdf';
            $('a#plot_download').attr('href', newlink);
        }
    });

    //Change download link depending on what user wants to download
    $('#id_download_choice').change(function () {
        if ($(this).val() == 'pdf-current') {
            var newlink = '../' + $('#id_plot_choice').val() + '.pdf'
            $('a#plot_download').attr('href', newlink);
        }
        //	if($(this).val() == 'pdf-all'){
        //		var newlink = "plots.zip"
        //		$('a#plot_download').attr('href',newlink);
        //	}
        if ($(this).val() == 'ASCII') {
            var newlink = "allData.zip"
            $('a#plot_download').attr('href', newlink);
        }
        //	if($(this).val() == 'ASCII-k'){
        //		var newlink = "power_spectrum.dat"
        //		$('a#plot_download').attr('href',newlink);
        //	}
        if ($(this).val() == 'parameters') {
            var newlink = "parameters.txt"
            $('a#plot_download').attr('href', newlink);
        }
        //	if($(this).val() == 'units'){
        //		var newlink = "units.dat"
        //		$('a#plot_download').attr('href',newlink);
        //	}
    });
});