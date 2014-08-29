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

        this.currentPaid = this.linkContainer.hasClass('paid');

        if (this.tests.dnd){
            this.holderTitle.show();
            this.fileUpload.hide();
        } else {
            this.holderTitle.hide();
            this.fileUpload.show();

            $('#file-upload').on('change', function(event){
                if (this.files != null && this.files.length > 0){

                    that.Routes.navigate("", {trigger: true});

                    that.sendFiles(this.files);
                }
            });
        }
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

    downloadBigMessage: $('#link-container-footer'),

    downloadFreeMessage: $('#free-download-footer'),

    holderTitle: $('#holder-title'),

    fileUpload: $('#file-upload-container'),

    el: $("body"),

    events: {
        "click .download-link": "downloadStart"
    },

    onDrop: function (e) {
        e.preventDefault();

        this.Routes.navigate("", {trigger: true});

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
                    that.currentPaid = response.paid;

                    that.showDownloadLinks(response.key, response.filename);
                    that.setFileInfo(response);

                    that.Routes.navigate(response.key, {trigger: true});

                    // that.showFileStatus();
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

    showDownloadLinks: function(key, filename){
        this.downloadLinks.each(function(index, element){
            var el = $(element);

            var split = el.attr("href").split(".");

            var extension = split[split.length - 1];

            $('input[type=hidden]').val(key);

            el.attr("href", "/download/" + key + "/" + filename + "." + extension);
        });
    },

    clearFile: function(){
        this.holderTitle.html('Drop file here');

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
        this.holderTitle.html('Drop another');

        this.statusPanel.show();

        this.uploadingMessage.hide();
        this.processingMessage.hide();
        this.fileMessage.show();
        this.fileUploadFailedMessage.hide();

        this.linkContainer.addClass('show_file');

        if (this.currentPaid){
            this.linkContainer.addClass('paid');
        }
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
        var that = this;

        event.preventDefault();

        var target = $(event.currentTarget);

        var link = target.attr('href');

        var pattern = /[\/\\]download[\/\\]([0-9a-z]+)[\/\\]([0-9a-zA-Z\^\&\'\@\{\}\[\]\,\$\=\!\-\#\(\)\.\%\+\~\_ ]+)/g

        var matches = pattern.exec(link)

        if (matches != null){
            var hash = matches[1];
            var filename = matches[2];

            var downloadId = hash + "_" + filename;

            var fileType = target.find('.file-type');

            this.linkContainer.find('a').addClass('disable-link');
            fileType.addClass('file-type-spinny');

            this.downloadBigMessage.html('Downloading...');
            this.downloadFreeMessage.html('Downloading...');

            this.checkForDownload(downloadId, function(){
                fileType.removeClass('file-type-spinny');
                that.linkContainer.find('a').removeClass('disable-link');
                that.downloadBigMessage.html('Click to download');
                that.downloadFreeMessage.html('Click to<br/>download');
            });

            _.delay(function(){
                window.location.href = link;
            }, 100);
        }
    },

    checkForDownload: function(downloadId, done){
        var that = this;

        if (_.isUndefined($.cookie(downloadId))){
            _.delay(function(){
                that.checkForDownload(downloadId, done);
            }, 500);
        } else {
            done();

            $.removeCookie(downloadId);
        }
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

window.Workspace = Backbone.Router.extend({

    routes: {
        ":hash":        "showFile",
        "":             "home"
    },

    home: function() {
        App.clearFile();
    },

    showFile: function() {
        App.showFileStatus();
    }
});

$(document).ready(function () {
    window.App = new App();

    window.App.Routes = new Workspace();

    Backbone.history.start({pushState: true});
});