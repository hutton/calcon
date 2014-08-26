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
            //that.holderDropFile.removeClass('file-type-jump-now');
        });
        this.holder.on('dragover', function (e) {
            //that.holderDropFile.addClass('file-type-jump-now');
            return false;
        });
        this.holder.on('dragend', function (e) {
            that.holderDropFile.removeClass('file-type-jump-now');
            return false;
        });
    },

    holder: $('#holder'),

    holderDropFile: $('#holder-drop-file'),

    statusPanel: $('#status-panel'),

    uploadingMessage: $('#uploading-message'),

    processingMessage: $('#processing-message'),

    fileMessage: $('#file-message'),

    linkContainer: $('.link-container'),

    downloadLinks: $('.download-link'),

    fileUploadFailedMessage: $('#file-upload-failed'),

    uploadingProgress: $('#uploading-message > .progress > span'),

    el: $("body"),

    events: {
        "click .download-link": "downloadStart"
    },

    onDrop: function (e) {
        e.preventDefault();
        this.clearFile();

        this.sendFiles(e.originalEvent.dataTransfer.files);
    },

    sendFiles: function (files) {
        var that = this;

        var formData = this.tests.formData ? new FormData() : null;

        for (var i = 0; i < files.length; i++) {
            formData.append('file', files[i]);

            this.setFileInfo({'full_filename': files[i].name});
        }

        this.showUploading();

        $.ajax({
            type: "POST",
            url: "/upload",
            data: formData,
            processData: false,
            contentType: false,
            xhr: function() {
                myXhr = $.ajaxSettings.xhr();
                if(myXhr.upload){
                    myXhr.upload.addEventListener('progress', that.showProgress, false);
                } else {
                    console.log("Upload progress is not supported.");
                }
                return myXhr;
            }
            }).done(function (data) {
                var response = jQuery.parseJSON(data);

                if (response.key != null) {
                    that.showDownloadLinks(response.key, response.filename, response.paid);
                    that.setFileInfo(response);
                    that.showFileStatus();
                }
            }).fail(function(data){
                var response = jQuery.parseJSON(data.responseText);

                that.showUploadingFailed(response.message);
            });
    },

    showProgress: function(evt){

        if (evt.lengthComputable) {
            var percentComplete = (evt.loaded / evt.total) * 100;

            if (percentComplete < 100){
                window.App.uploadingProgress.css("width", percentComplete + "%");
            } else{
                window.App.showProcessing();
            }
        }
    },

    showDownloadLinks: function(key, filename, paid){

        this.linkContainer.addClass('show_file');

        if (paid){
            this.linkContainer.addClass('paid');
        }

        this.downloadLinks.each(function(index, element){
            var el = $(element);

            var split = el.attr("href").split(".");

            var extension = split[split.length - 1];

            $('input[type=hidden]').val(key);

            el.attr("href", "/download/" + key + "/" + filename + "." + extension);
        });
    },

    clearFile: function(){
        this.statusPanel.hide();
        this.linkContainer.removeClass('show_file');
        this.linkContainer.removeClass('paid');
    },

    showUploading: function(){

        this.statusPanel.show();

        this.uploadingMessage.show();
        this.processingMessage.hide();
        this.fileMessage.hide();
        this.fileUploadFailedMessage.hide();
    },

    showProcessing: function(){
        this.statusPanel.show();

        this.uploadingMessage.hide();
        this.processingMessage.show();
        this.fileMessage.hide();
        this.fileUploadFailedMessage.hide();
    },

    showFileStatus: function(){
        this.statusPanel.show();

        this.uploadingMessage.hide();
        this.processingMessage.hide();
        this.fileMessage.show();
        this.fileUploadFailedMessage.hide();
    },

    showUploadingFailed: function(message){
        this.statusPanel.show();

        this.uploadingMessage.hide();
        this.processingMessage.hide();
        this.fileMessage.hide();
        this.fileUploadFailedMessage.show();

        $('#file-upload-failed-message').html(message);
    },

    setFileInfo: function(convertionInfo){
        this.uploadingMessage.find('> span').html(convertionInfo.full_filename);
        this.processingMessage.find('> span').html(convertionInfo.full_filename);

        this.fileMessage.find('#filename').html(convertionInfo.full_filename);

        if (_.isUndefined(convertionInfo.event_count) && convertionInfo.event_count > 0){
            this.fileMessage.find('#event-count').hide();
        } else {
            this.fileMessage.find('#event-count').show();
            this.fileMessage.find('#event-count').html(convertionInfo.event_count + " Events");
        }

        if (_.isUndefined(convertionInfo.todo_count) && convertionInfo.todo_count > 0){
            this.fileMessage.find('#todo-count').hide();
        } else {
            this.fileMessage.find('#todo-count').show();
            this.fileMessage.find('#todo-count').html(convertionInfo.todo_count + " Todos");
        }
    },

    downloadStart: function(event){
        var target = $(event.currentTarget);

        var link = target.attr('href');

        var downloadId = link;

        $.get( "download-progress?downloadId=" + downloadId, function( data ) {
        }).always(function() {

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