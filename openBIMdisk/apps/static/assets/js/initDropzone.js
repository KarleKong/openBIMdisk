//App函数对象
var App = function () {
    //默认的Dropzone参数
    var defaultDropzoneOpts = {
        url: "", // 文件提交地址
        method: "post",  // 也可用put
        paramName: "dropFile", // 提交的参数,默认为file
        maxFiles: 2,// 一次性上传的文件数量上限
        maxFilesize: 200, // 文件大小，单位：MB
        acceptedFiles: ".ifc,.ifcjson", // 上传的类型
        addRemoveLinks: true,
        parallelUploads: 2,// 一次上传的文件数量
        dictDefaultMessage: 'Drag files here or click upload',
        dictMaxFilesExceeded: "Only upload a maximum of "+this.maxFiles+"files!",
        dictResponseError: 'File upload failed!',
        dictInvalidFileType: "The file type can only be *.ifc,*.ifcjson",
        dictFallbackMessage: "Browser not supported",
        dictFileTooBig: "File oversize upload file maximum support.",
        dictRemoveLinks: "Delete",
        dictCancelUpload: "Cancle"
    };
    /*
    * 初始化Dropzone
    * */
    var handlerInitDropzone = function (opts) {
        //关闭Dropzone自动发现功能
        Dropzone.autoDiscover = false;
        //继承
        $.extend(defaultDropzoneOpts,opts);
        return new Dropzone(defaultDropzoneOpts.id, defaultDropzoneOpts);
    };
    return{
        //初始化Dropzone
        initDropzone:function (opts) {
            return handlerInitDropzone(opts);
        }
    }
}();