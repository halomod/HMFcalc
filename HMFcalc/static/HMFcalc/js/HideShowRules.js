$(function () {
    jQuery.fn.extend({
       toggle_params: function(){
           var these =$('div[data-component='+$(this).attr("data-component")+'][data-model~='+$(this).val()+']');
            these.show();
            these.find("input").prop("required", true);

            var those = $('div[data-component='+$(this).attr("data-component")+']').not('[data-model~='+$(this).val()+']');
            those.hide();
            those.find('input').removeAttr("required");
       }
    });

    /* Hide all params that aren't required here */
    $('.hmf_model').toggle_params();

    $('.hmf_model').change(function() {
        $(this).toggle_params();
    });

    // Shadow out the delete button if there's only one left!
    if ($('[id*="-table-delete-button"]').length === 1) {
        console.log("doing this...");
        console.log($('[id*="-table-delete-button"]'));
        $('[id*="-table-delete-button"]').replaceWith(function() {
            return $('<span/>', {
                href: this.href,
                html: this.innerHTML
            });
        });
    }

    if ($('[id*="-table-delete-button"]').length > 1) {
        $('[id*="-table-delete-button"]').replaceWith(function() {
            return $('<a/>', {
                href: this.href,
                html: this.innerHTML
            });
        });
    }

    //Actions for when the cosmology is changed.
    $('#id_cosmo_model').change(function () {
        if ($(this).val() === "WMAP7") {
            console.log("YEAH!");
            $('#id_cosmo_Om0').val('0.226');
            $('#id_cosmo_Ob0').val('0.0455');
            $('#id_n').val('0.967');
            $('#id_sigma_8').val('0.81');
            $('#id_cosmo_H0').val('70.4');
        }
        if ($(this).val() === "WMAP5") {
            $('#id_cosmo_Om0').val('0.231');
            $('#id_cosmo_Ob0').val('0.0459');
            $('#id_n').val('0.962');
            $('#id_sigma_8').val('0.817');
            $('#id_cosmo_H0').val('70.2');

        }
        if ($(this).val() === "GiggleZ") {
            $('#id_cosmo_Om0').val('0.228');
            $('#id_cosmo_Ob0').val('0.0456');
            $('#id_n').val('0.960');
            $('#id_sigma_8').val('0.812');
            $('#id_cosmo_H0').val('70.5');

        }
        if ($(this).val() === "WMAP3") {
            $('#id_cosmo_Om0').val('0.224');
            $('#id_cosmo_Ob0').val('0.044');
            $('#id_n').val('0.947');
            $('#id_sigma_8').val('0.776');
            $('#id_cosmo_H0').val('70.4');
        }
        if ($(this).val() === "WMAP1") {
            $('#id_cosmo_Om0').val('0.243');
            $('#id_cosmo_Ob0').val('0.047');
            $('#id_n').val('0.99');
            $('#id_sigma_8').val('0.9');
            $('#id_cosmo_H0').val('72.0')
        }
        if ($(this).val() === "Millennium") {
            $('#id_cosmo_Om0').val('0.205');
            $('#id_cosmo_Ob0').val('0.045');
            $('#id_n').val('1');
            $('#id_sigma_8').val('0.9');
            $('#id_cosmo_H0').val('73.0')
        }

        if ($(this).val() === "Planck13") {
            $('#id_cosmo_Om0').val('0.2678');
            $('#id_cosmo_Ob0').val('0.049');
            $('#id_n').val('0.9619');
            $('#id_sigma_8').val('0.8347');
            $('#id_cosmo_H0').val('67.04');
        }

        if ($(this).val() === "WMAP9") {
            $('#id_cosmo_Om0').val('0.236');
            $('#id_cosmo_Ob0').val('0.0461');
            $('#id_n').val('0.9646');
            $('#id_sigma_8').val('0.817');
            $('#id_cosmo_H0').val('69.7');
        }

        if ($(this).val() === "Planck15") {
            $('#id_cosmo_Om0').val('0.3075');
            $('#id_cosmo_Ob0').val('0.0486');
            $('#id_n').val('0.965');
            $('#id_sigma_8').val('0.802');
            $('#id_cosmo_H0').val('67.74');
        }

    });

    //Change plotted image to whatever user clicks on
    $('#id_plot_choice').change(function () {
        var src = $(this).val() + '.png';
        $('#the_image').attr('src', src);

        //Also change download link
        if ($('#id_download_choice').val() == 'pdf-current') {
            var newlink = 'download/' + $('#id_plot_choice').val() + '.pdf';
            $('a#plot_download').attr('href', newlink);
        }
    });

    //Change download link depending on what user wants to download
    $('#id_download_choice').change(function () {
        if ($(this).val() == 'pdf-current') {
            var newlink = $('#id_plot_choice').val() + '.pdf'
            $('a#plot_download').attr('href', newlink);
        }
        if ($(this).val() == 'ASCII') {
            var newlink = "download/allData.zip"
            $('a#plot_download').attr('href', newlink);
        }
        if ($(this).val() == 'parameters') {
            var newlink = "download/parameters.txt"
            $('a#plot_download').attr('href', newlink);
        }
        if ($(this).val() == 'halogen') {
            var newlink = "download/halogen.zip"
            $('a#plot_download').attr('href', newlink);
        }
    });
});