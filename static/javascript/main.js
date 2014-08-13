/**
 * Created by simonhutton on 06/08/2014.
 */
window.App = Backbone.View.extend({
    initialize: function () {
        var that = this;

        this.tests = {
            fileReader: typeof FileReader != 'undefined',
            dnd: 'draggable' in document.createElement('span'),
            formData: !!window.FormData,
            progress: "upload" in new XMLHttpRequest
        };

        this.holder.on('drop', function (e) {
            that.onDrop(e);
        });
        this.holder.on('dragover', function (e) {
            return false;
        });
        this.holder.on('dragend', function (e) {
            return false;
        });
    },

    holder: $('#holder'),

    linkContainer: $('.link-container'),

    downloadLinks: $('.download-link'),

    events: {
    },

    onDrop: function (e) {
        e.preventDefault();
        this.sendFiles(e.originalEvent.dataTransfer.files);
    },

    sendFiles: function (files) {
        var that = this;

        var formData = this.tests.formData ? new FormData() : null;

        for (var i = 0; i < files.length; i++) {
            formData.append('file', files[i]);
        }

        $.ajax({
            type: "POST",
            url: "/upload",
            data: formData,
            processData: false,
            contentType: false
        }).done(function (data) {
            var response = jQuery.parseJSON(data);

            if (response.key != null) {
                that.showDownloadLinks(response.key, response.filename, response.paid);
            }
        });
    },

    showDownloadLinks: function(key, filename, paid){
        this.linkContainer.show();

        this.downloadLinks.each(function(index, element){
            var el = $(element);

            var split = el.attr("href").split(".");

            var extension = split[split.length - 1];

            $('input[type=hidden]').val(key);

            el.attr("href", "/download/" + key + "/" + filename + "." + extension);
        });
    }
});

//if (tests.dnd) {
//    holder.ondragover = function () {
//        this.className = 'hover';
//        return false;
//    };
//    holder.ondragend = function () {
//        this.className = '';
//        return false;
//    };
//    holder.ondrop = function (e) {
//        this.className = '';
//        e.preventDefault();
//        readfiles(e.dataTransfer.files);
//    }
//} else {
//    fileupload.className = 'hidden';
//    fileupload.querySelector('input').onchange = function () {
//        readfiles(this.files);
//    };
//}

$(document).ready(function () {
    window.App = new App();

});