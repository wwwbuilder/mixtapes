$(function() {
    filepicker.setKey(fpApiKey);
});

//uploadFiles 

function uploadFiles (filetype, mixtapeid, mixtapetitle) {
    var mixtapeid = mixtapeid,
        uploadpolicy = $('#uploadpolicy').text(),
        uploadsignature = $('#uploadsignature').text(),
        mixtapetitle = '/' + mixtapetitle + '/'

    console.log(mixtapetitle);

    if (filetype == 'images') {
        var ajaxurl = '/routers/mixtapeimage-viewset/',
            mimefiletype = 'image'
    } else if (filetype == 'tracks') {
        var ajaxurl = '/routers/trackwrite-viewset/'
            mimefiletype = 'audio'
    }
    filepicker.pickAndStore(
        {
            multiple:true,
            mimetypes: ['' + mimefiletype + '/*',],
            policy: uploadpolicy,
            signature: uploadsignature,
            //mobile: true
        },
        {
            location:"S3",
            path: mixtapetitle
        },
        function(InkBlobs){
            var calls = []
            $.each(InkBlobs, function(){
                var iburl=this.url,
                    ibfilename=this.filename,
                    ibmixtapeid=mixtapeid,
                    ibmimetype=this.mimetype,
                    ibsize=this.size
                    ibawskey=this.key

                    calls.push(
                        $.ajax({
                            url:ajaxurl,
                            data:{
                                url:iburl,
                                filename:ibfilename,
                                mixtape:ibmixtapeid,
                                mimetype:ibmimetype,
                                size:ibsize,
                                awskey:ibawskey
                            },
                            type:'POST',
                            success:function(){
                                console.log('' + ibfilename + ' - SUCCESS!');
                            },
                            error:function(){
                                console.log('' + ibfilename + ' - ERROR!')
                            }
                        })
                    );
            });
            $.when.apply($, calls).then(function(){
                getEntries(filetype, mixtapeid);
            });
        }
    );
}
