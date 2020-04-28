$(document).ready(function () {
    // Pentru vizualizarea imaginii inainte de upload
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                document.getElementById('upload_placeholder').src = e.target.result;
                document.getElementById('upload_placeholder').style.visibility = "visible";
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    $('#file').change(function () {
        readURL(this);
    });

    // Pentru schimbarea link-ului de navbar
    $('.navbar-nav a').on('click', function () {
        $('.navbar-nav').find('li.active').removeClass('active');
    });

    // Pentru selectia picturilor
    $('.card.painting').click(function () {
        // console.log(this.id);
        let selected_card = document.getElementById(this.id);
        let all_cards = document.getElementsByClassName('painting');
        let i;
        for (i = 0; i < all_cards.length; i++) {
            if ($(all_cards[i]).hasClass("selected"))
                $(all_cards[i]).removeClass("selected");
        }
        // console.log(all_cards);
        $(selected_card).addClass("selected");
    });
    $('.card.inside_outside').click(function () {
        // console.log(this.id);
        let selected_card = document.getElementById(this.id);
        let all_cards = document.getElementsByClassName('inside_outside');
        let i;
        for (i = 0; i < all_cards.length; i++) {
            if ($(all_cards[i]).hasClass("selected"))
                $(all_cards[i]).removeClass("selected");
        }
        // console.log(all_cards);
        $(selected_card).addClass("selected");
    });
    $('#for_post').click(function () {
        if ($("#img_styled_placeholder").has("img")) {
            $("#img_styled").remove();
        }
        let selected_model = document.getElementsByClassName('selected')[0];
        let selected_mode = document.getElementsByClassName('selected')[1];

        if (selected_model !== undefined) {
            selected_model = selected_model.id;
        } else {
            alert("Please select a picture before continuing!");
        }

        if (selected_mode !== undefined) {
            selected_mode = selected_mode.id;
        } else {
            alert("Please select a mode before continuing!");
        }
        console.log(selected_model, selected_mode);
        if (selected_mode !== undefined && selected_model !== undefined) {
            $('html, body').animate({scrollTop: $(document).height()}, 'slow');
            document.getElementById('loading').className += " spinner-grow";
            let image_url = document.getElementById('uploaded_user_img').src;
            let image_name = image_url.substring(image_url.lastIndexOf('/') + 1);
            $.ajax({
                url: "/style_image",
                type: "POST",
                dataType: "json",
                data: {
                    'selected_model': selected_model,
                    'selected_mode': selected_mode,
                    'image_name': image_name,
                    csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value
                },
                success: function (result) {
                    console.log("SUCCESS");
                    console.log(result['styled_image_url']);
                    document.getElementById('loading').className -= " spinner-grow";
                    var img = $('<img id="img_styled">');
                    img.attr('src', result['styled_image_url']);
                    img.attr('class', 'img-fluid');
                    img.appendTo('#img_styled_placeholder');
                    $('html, body').animate({scrollTop: $(document).height()}, 'slow');
                },
                error: function (e) {
                    console.log("EROARE " + e);
                }
            });
        }
    });


    $("#submitforstyle").click(function () {
        let selected_model = document.getElementsByClassName('selected')[0];
        let selected_mode = document.getElementsByClassName('selected')[1];

        if (selected_model !== undefined) {
            selected_model = selected_model.id;
        } else {
            alert("Please select a picture before continuing!");
        }

        if (selected_mode !== undefined) {
            selected_mode = selected_mode.id;
        } else {
            alert("Please select a mode before continuing!");
        }

        if (selected_mode !== undefined && selected_model !== undefined) {
            // document.getElementById('loading').className += " spinner-grow";
            $('input[name="painting_id"]').val(selected_model);
            $('input[name="selected_mode"]').val(selected_mode);
            $("#myform").submit();
            // Spinner
            document.getElementById('loading_element').className += " is-active";
        }
    });


    var $form = $('.box');
    var $label = $form.find('label');

    $('input[type="file"]').change(function (e) {
        var fileName = e.target.files[0].name;
        $label.text(fileName);
    });

    var isAdvancedUpload = function () {
        var div = document.createElement('div');
        return (('draggable' in div) || ('ondragstart' in div && 'ondrop' in div)) && 'FormData' in window && 'FileReader' in window;
    }();


    if (isAdvancedUpload) {
        $form.addClass('has-advanced-upload');
        var showFiles = function (file) {
            $label.text(file[0].name);
        };

        var droppedFiles = false;

        $form.on('drag dragstart dragend dragover dragenter dragleave drop', function (e) {
            e.preventDefault();
            e.stopPropagation();
        })
            .on('dragover dragenter', function () {
                $form.addClass('is-dragover');
            })
            .on('dragleave dragend drop', function () {
                $form.removeClass('is-dragover');
            })
            .on('drop', function (e) {
                // Action for dropped file
                droppedFiles = e.originalEvent.dataTransfer.files;
                var reader = new FileReader();
                const imageType = /image.*/;
                if (droppedFiles.length === 1 && droppedFiles[0].type.match(imageType)) {
                    reader.onload = function (e) {
                        document.getElementById('upload_placeholder').src = e.target.result;
                        document.getElementById('upload_placeholder').style.visibility = "visible";
                    };
                    reader.readAsDataURL(droppedFiles[0]);
                    showFiles(droppedFiles);
                    document.querySelector('.box__file').files = droppedFiles;
                } else {
                    if (!droppedFiles[0].type.match(imageType)) {
                        alert("Please upload ONLY images!");
                    }
                    if (droppedFiles.length > 1) {
                        alert("Please upload ONLY ONE file!");
                    }
                }
            });
    }
});