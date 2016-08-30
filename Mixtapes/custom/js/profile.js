$(function () {
	filepicker.setKey($('#fp_api_key').text());
});

function getImages(userprofileid) {
		var endpoint = '/routers/userprofileimage-viewset/?userprofile=' + userprofileid,
		filters = {'object_id': userprofileid}
    $.ajax({
        url:endpoint,
        type:'GET',
		data: filters,
        success:function(data){
            var tableholder = $('#profileImages');
            tableholder.children().fadeOut().remove();

            var source = $('#profileimages-template').html(),
                template = Handlebars.compile(source),
                context = {'entries':data},
                html = template(context)
            
            tableholder.append(html).hide().fadeIn('slow');
        }
    });
}

function deleteEntry (fileid) {   
    var answer = confirm('Are you sure you wish to PERMANENTLY delete this image?'),
        url = '/routers/userprofileimage-viewset/' + fileid

    if (answer) {
        var userprofileid = $('h1').first().prop('id')
        $.ajax({
            type:'GET',
            url:url,
            success:function(data){
                var inkblob = {url:data.url}
                filepicker.remove(inkblob, function(){
                    console.log('file was removed!');
                });
                $.ajax({
                    type:'DELETE',
                    url:url,
                    success:function(){
                        window.location.reload();
                    }
                });
            }
        });
    }
}

function setprofileImage (fileid) {   
    var answer = confirm('Are you sure you wish to set this as your profile image?'),
        fileid = fileid

    if (answer) {
        $.ajax({
            type:'POST',
            url:'/setprofileimage/',
            data:JSON.stringify({
                'defaultimage':fileid
            }),
            success:function(){
                window.location.reload();
            }
        });
    }
}

//function uploadProfile (userprofileid, uploadpolicy ,uploadsignature) {
function uploadProfile (){
	var userprofileid = $('#userprofileid').text(),
        uploadpolicy = $('#fp_upload_pol').text(),
        uploadsignature = $('#fp_upload_sig').text()
    filepicker.pickAndStore(
        {
            multiple:true,
            mimetypes: ['image/*',],
            policy: uploadpolicy,
            signature: uploadsignature
        },
        {location:"S3"},
        function(InkBlobs){
            var calls = []
            $.each(InkBlobs, function(){
                var iburl=this.url,
                    ibfilename=this.filename,
                    ibuserprofileid=userprofileid,
                    ibmimetype=this.mimetype,
                    ibsize=this.size
                    ibawskey=this.key
				    ibobject_id = userprofileid
                
                    calls.push(
                        $.ajax({
                            url:'/userprofileimage/',
                            data:{
                                url:iburl, 
                                filename:ibfilename,
                                userprofile:ibuserprofileid,
                                mimetype:ibmimetype,
                                size:ibsize,
                                awskey:ibawskey,
							   object_id:ibobject_id
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
                window.location.reload();
            });
        }
    );
}

$('#upload-profile').click(function(){
uploadProfile();
});