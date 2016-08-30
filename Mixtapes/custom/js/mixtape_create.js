$(function () {
	filepicker.setKey($('#fp_api_key').text());
});

var init_mixtape_data_panel = function(){
	$('.panel-heading').first().click(function(){
		$(this).siblings('.panel-collapse').collapse('toggle')
	});
};

window.progress = 0;
//Reuseable actions
track_id=0;
upgrade ='';
var update_progress = function(){
	var completeness = Math.round((window.progress/3)*100)
	$('#upload_progress').css('width', '' + completeness + '%').text(completeness + '% complete!');
};

var enable_next_step = function(elem){
	$(elem).closest('.panel').next().children('.panel-heading').click(function(){
		$(this).siblings('.panel-collapse').collapse('toggle');
	});
};

var closepanel = function(elem){
	$(elem).closest('.panel-collapse').collapse('hide');
};

var opennextpanel = function(elem){
	$(elem).closest('.panel').next().find('.panel-collapse').collapse('show');
};

var openprevpanel = function(elem){
	$(elem).closest('.panel').prev().find('.panel-collapse').collapse('show');
};

var showcheck = function(elem){
	$(elem).closest('.panel').find('i.hidden').removeClass('hidden');
};

var marksuccessful = function(elem, step){
	window.progress = step;
	showcheck(elem);
	enable_next_step(elem);

	//When closed, this now appears green (ie. success)
	$(elem).closest('.panel-collapse').on('hide.bs.collapse', function(){
		$(elem).closest('.panel').toggleClass('panel-success', true);
	});
	//Remove green (ie. still show blue, primary, colors) when open
	$(elem).closest('.panel-collapse').on('show.bs.collapse', function(){
		$(elem).closest('.panel').toggleClass('panel-success', false);
	});

	//If everything is done, show the button
//	if (window.progress == 4) {
//		$('#all_done').removeClass('hidden').hide().fadeIn();
//	} else {
//		$('#all_done').fadeOut().addClass('hidden');
//	};
};

//Initialize select2 autocomplete
function enableAutocomplete (elem, multiple, placeholder) {
	if (elem == '#tracks-holder input.parsley-check[name="name"]'){
		url='/routers/autocompletetrack-viewset';
	}else{
		url = '/routers/autocompleteuserprofile-viewset';
	}
	$(elem).select2({
		allowClear: true,
		placeholder: placeholder || "Please Select",
		minimumInputLength: 2,
		width: "100%",
		multiple: multiple || false,

		ajax: {
			url: url,
			quietMillis: 100,
			data: function (term, page) {
			// page is the one-based page number tracked by Select2
			return {
					q: term, //search term
				};
			},
			results: function (data, page) {
				return { results: data };
			}
		},
		initSelection: function(element, callback){
			//Provide the ajax data in the format of the rest of the select2 constructor
			//The data returned by the ajax call should be the subset for which you want to preopulate
			var prepop = $(element).data('prepop')
			callback(prepop);
			// if (prepop !== undefined){
			// 	if (prepop.length > 1){
			// 		callback(prepop)
			// 	} else {
			// 		callback(prepop[0])
			// 	}
			// }
		},
		formatResult: function (data) {
			if (elem == '#tracks-holder input.parsley-check[name="name"]'){
				return "<div class='select2-user-result'>" + data.filename + "</div>";
			}else{
				return "<div class='select2-user-result'>" + data.username + "</div>";
			}
		},
		formatSelection: function(data){
			if (elem == '#tracks-holder input.parsley-check[name="name"]'){
				return data.filename
			}else{
				return data.username;
			}
			
		}
	});
}

//Initialize the select2
$(function () {
         primaryArtist = $('#primaryArtist').val();
	 if (primaryArtist) {
		enableAutocomplete('#artist_select',false,primaryArtist);
		$('#artist_select').val(primaryArtist);
		}
	else {
		enableAutocomplete('#artist_select');
	}
	secondaryArtist = $('#secondaryArtist').val();
	 if (secondaryArtist) {
		enableAutocomplete('#artist_select1',false,secondaryArtist);
		}
	else {
		enableAutocomplete('#artist_select1');
	}
	producer = $('#producer').val();
	 if (producer) {
		enableAutocomplete('#artist_select3',false,producer);
		}
	else {
		enableAutocomplete('#artist_select3');
	}
	djs = $('#djs').val();
	 if (djs) {
		enableAutocomplete('#artist_select2',false,djs);
		}
	else {
		enableAutocomplete('#artist_select2');
	}
	enableAutocomplete('#djs_select');
});

//Initialize back buttons
$(function () {
	$('.stepback').click(function(){
		closepanel(this);
		openprevpanel(this);
	})
});

//Toggle primary class for active panel
$(function () {
	//Make the active panel blue (ie. primary)
	$('.panel-collapse').on('show.bs.collapse', function(){
		$(this).parent('.panel').toggleClass('panel-primary', true);
	});
	//Remove blue once it is closed
	$('.panel-collapse').on('hide.bs.collapse', function(){
		$(this).parent('.panel').toggleClass('panel-primary', false);
	});
});

//Initilize first panel
init_mixtape_data_panel();

function ytVidId(url) {
    var p = /^(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?(?=.*v=((\w|-){11}))(?:\S+)?$/;
    return (url.match(p)) ? RegExp.$1 : false;
}


//Next button on mixtape data panel

	$('#mixtape_data_next').click(function(){
		var form_valid = $('#mixtape_data').parsley().validate(),
		artist_valid = ($('#artist_select').val() != ""),
		currentstep = $('#mixtape_data_next'),
		current_mixtape_id = $('#mixtapeid').val();
		
		mixtape_list_url = '/mixtape_list/'
		if (current_mixtape_id == undefined){
		
			var endpoint = mixtape_list_url,
			method = 'post'
		} else {
			var endpoint = '/mixtape_list/' + current_mixtape_id,
			method = 'post'
		};
		var url = $('form input[name="video_url"]').val();
		if (url != ''){
	    if (ytVidId(url) == false) {
	       	$('#video_url_form_group').addClass('has-error')
	    	$('#video_url_form_group').append('<span class="type" style="display: inline;">This value should be a valid youtube url.</span>')
	        return false;
	       
	    }}
		/*The select2 artist field needs to be validated
		independently from the form*/
		if (form_valid && artist_valid){
			//Send this data to the back end
			var data = $('#mixtape_data').serialize()
			$.ajax({
				url: endpoint,
				type: method,
				data: data,
				success: function(data) {
					//Store mixtape data in the next button as a data attributes
					currentstep.data('current_mixtape_id', data.mixtapeid);
					currentstep.data('current_mixtape_full_mixtape_slug', data.full_mixtape_slug);
					currentstep.data('current_mixtape_content_type_id', data.content_type_id);
					//Go through the usual precedure
					
					
					marksuccessful(currentstep, 1);
					closepanel(currentstep);
					update_progress();
					opennextpanel(currentstep);
					getEntries('images', data.current_mixtape_id, data.current_mixtape_content_type_id);
				},
				error: function(data){
					$.pnotify({
						title: 'Error',
						text: data.responseText,
						icon: 'fa fa-exclamation-circle',
						type: 'error'
					})
				}
			});
		}
	});


//Next button on images panel
//On both of the next buttons, close the panel
$('#upload_images_next').click(function(){
	marksuccessful(this, 2);
	closepanel(this);
	update_progress();
	opennextpanel(this);
	var mixtape_id = $('#mixtape_data_next').data('current_mixtape_id');
	var content_type_id = $('#mixtape_data_next').data('content_type_id');
	getEntries('tracks', mixtape_id, content_type_id);
});


//Next button on tracks panel
//On both of the next buttons, close the panel
$('#upload_tracks_next').click(function(){
	//validation for track upload
	if ($('#tracks-holder table tr').length>0){
		marksuccessful(this, 3);
		$('.error_track').hide();
		closepanel(this);
		update_progress();
		opennextpanel(this);
	}else{
		$('.error_track').show();
	}
	
});


//Fetch the list view of all the images or tracks associated with a give mixtape
function getEntries (filetype, mixtape_id, mixtape_content_type_id) {
	if (filetype == 'images'){
		var endpoint = '/routers/mixtapeimage-viewset/?mixtape=' + mixtape_id, //image-list',
		filters = {'object_id': mixtape_id, 'content_type': mixtape_content_type_id}
	} else if (filetype == 'tracks'){
		var endpoint = '/routers/track-viewset/?mixtape=' + mixtape_id, //track_list_url,
		filters = {'mixtape': mixtape_id}
	};
	//Get all associated images or tracks
	$.ajax({
		url: endpoint,
		type: 'get',
		data: filters,
		success: function (data) {
		     var context = {'entries': data},
			source = $('#' + filetype + '-table').html(),
			template = Handlebars.compile(source),
			html = template(context)

			$('#' + filetype + '-holder').empty().append(html).hide().fadeIn();

			//If this for tracks, also enable the autocomplete
			//if (filetype == 'tracks'){
				//enableAutocomplete('.ajax-multiple-select', true, 'Select artist(s)');
			//};
			$('#' + filetype + '-holder table').tablesorter();
			enableAutocomplete('input[name=artists]');
			enableAutocomplete('input[name=producers]');
			enableAutocomplete('input[name=djs]');
			//enableAutocomplete('#tracks-holder input.parsley-check[name="name"]');
			if (filetype == 'images'){
				$('#images-holder input.parsley-check[name="name"]').val($('#title-holder input').val());
				
			}
			try{
                            var arrayLength = data.length;
                            if(data[0] != 'undefined' ){
                                for (var i = 0; i < arrayLength; i++) {
                                    $('.table tr[data-track_id="'+data[i].id+'"] td:nth-child(3)').find('input').val(data[i].filename)
                                    if (data[i].artists[0] == undefined)
                                        continue;
                                    $('.table tr[data-track_id="'+data[i].id+'"] td:nth-child(4)').find('.select2-chosen').text(data[i].artists[0].username)
                                    if (data[i].producers[0] == undefined)
                                        continue;
                                    $('.table tr[data-track_id="'+data[i].id+'"] td:nth-child(5)').find('.select2-chosen').text(data[i].producers[0].username)
                                    if (data[i].djs[0] == undefined)
                                        continue;
                                    $('.table tr[data-track_id="'+data[i].id+'"] td:nth-child(6)').find('.select2-chosen').text(data[i].djs[0].username)
                                    //$('.table tr[data-track_id="'+data[0].id+'"]').find('.select2-chosen').text(data[0].artists[0].username)
                            }
                            }
			}
			catch(i){}
			
		},
		error: function(data){
			$.pnotify({
				title: 'API Error',
				icon: 'fa fa-exclamation-circle',
				text: 'There seems to be an error retrieving your files. Please contact our support team.',
				type: 'error'
			});
		}
	});
	
};

//Save Inkblobs
function saveInkblobs (filetype, data, finalcallback) {
  	var mixtape_id = $('#mixtape_data_next').data('current_mixtape_id'),
	mixtape_content_type_id = $('#mixtape_data_next').data('current_mixtape_content_type_id')
	addon = false;
	window.num_success = [];
	window.num_error = [];
	if (filetype == 'images') {
		var endpoint = '/image-list/'
	} else if (filetype == 'tracks') {
		var endpoint = '/track-list/'//track_list_url
	}else{
		mixtape_id = filetype[0];
		mixtape_content_type_id =filetype[2];
		var endpoint = '/image-list/'
		addon = true;
		
	}

	//Add mixtape id to each of the objects in the array
	var calls = []
	for (var i = 0, len = data.length; i < len; i++) {
		var inkblob = data[i]
		console.log(inkblob);
		inkblob['mixtape'] = mixtape_id
                inkblob['order'] = ''
		inkblob['object_id'] = mixtape_id
		inkblob['content_type'] = mixtape_content_type_id
		if (addon == true){
			inkblob['level'] = filetype[3];
			filetype = 'images';
		}else{
			inkblob['level'] = 0;
		}
		
		//inkblob['content_type'] = mixtape_content_type_id
		//inkblob['content_type'] = mixtape_content_type_id
		//console.log(inkblob);
		//Posting each track (individually)
		calls.push(
				
			$.ajax({
				url: endpoint,
				type: 'post',
				data: inkblob,
				success: function (data) {
					window.num_success.push(data);
					track_id=data.id;
					upgrade=data.url;
					$('#addon_upgrade').attr('href',upgrade);
				},
				error: function(data){
					window.num_error.push(data);
				}
			})
			);
	};

	//Apply the calls and only run the next step after completion
	$.when.apply($, calls).then(function(){

		//Show the files that have been uploaded
		var textblock = '<p>' + window.num_success.length + ' succeeded <i class="fa fa-check"></i></p>' + '<p>' + window.num_error.length + ' failed <i class="fa fa-times"></i></p>'

		$.pnotify({
			title: 'Upload Complete',
			icon: 'fa fa-cloud-upload',
			text: textblock,
			type: 'info'
		});

		getEntries(filetype, mixtape_id, mixtape_content_type_id);
	});
};

//Load Filepicker pick and store modal
function uploadFiles (filetype) {
	var current_mixtape_id = $('#mixtape_data_next').data('current_mixtape_id');
	current_mixtape_full_mixtape_slug = $('#mixtape_data_next').data('current_mixtape_full_mixtape_slug')

	if (filetype == 'images') {
		mimefiletype = 'image/*'
	} else if (filetype == 'tracks') {
		mimefiletype = 'audio/*'
	}else{
		filetype =filetype.split('|');
		current_mixtape_id = filetype[0];
		current_mixtape_full_mixtape_slug =filetype[1];
		mimefiletype = 'image/*';
	}

	filepicker.pickAndStore(
	{
		mimetype: mimefiletype,
		multiple: true,
		policy: $('#fp_upload_pol').text(),
		signature: $('#fp_upload_sig').text(),
                //mobile: true
		 				
	},
	{
		location: 'S3',
		path: "/" + current_mixtape_full_mixtape_slug + "/"
		
		
	},
	function(data){
		window.uploadfilesuccess = data;
		saveInkblobs(filetype, data);
	},
	function(data){
		//Do this in pnofity
		console.log('ERROR');
		console.log(data);
		window.allfailure = data;
	}
	)
};

//Instrument the upload images and upload tracks buttons
	$('#upload_images_button').click(function(){

		var filetype = $(this).attr('filetype');

		// For some browsers, `attr` is undefined; for others,
		// `attr` is false.  Check for both.
		if (typeof filetype !== typeof undefined && filetype !== false) {
			uploadFiles(filetype)
		}
		else{
			uploadFiles('images');
		}


		
		
});
	
	$('.upload_images_button').click(function(){

		var filetype = $(this).attr('filetype');

		// For some browsers, `attr` is undefined; for others,
		// `attr` is false.  Check for both.
		if (typeof filetype !== typeof undefined && filetype !== false) {
			uploadFiles(filetype)
		}
		else{
			uploadFiles('images');
		}


		
		
});
	
	

	$('#upload_tracks_button').click(function(){
		uploadFiles('tracks');
});

//Delete an image from within the images table inside the panel
function deleteFile (filetype, object_id) {
	if (filetype == 'images'){
		var ft = 'image',
		endpoint = '/image-list/'//image_list_url
	} else if (filetype == 'tracks'){
		var ft = 'track',
		endpoint = '/track-list/'//track_list_url
	}

	if (confirm('Delete ' + ft + ': This can not be undone. Proceed?')){
		$.ajax({
			url: endpoint,// + object_id,
			type: 'delete',
			success: function (data) {
				var thisrow = $('tr[data-' + ft + '_id=' + object_id + ']')

				//If this is the only row, remove the rest of the table as well
				if (thisrow.siblings().length == 0){
					thisrow.closest('table').fadeOut(300, function(){
						$(this).remove();
					});
				} else {
					$('tr[data-' + ft + '_id=' + object_id + ']').fadeOut(200, function(){
						$(this).remove();
					});
				}
			},
			error: function(data){
				$.pnotify({
					title: 'Could Not Delete',
					text: data.responseText,
					icon: 'fa fa-exclamation-circle',
					type: 'error'
				})
			}
		});
	}
};

//Copy optional data back into the hidden fields
function saveOptionalModal () {
	var modal = $('#optional-modal'),
	track_id = modal.data('track_id'),
	video_url = modal.find('input').val(),
	lyrics = modal.find('textarea').val(),
	tr = $('#tracks-holder tr[data-track_id=' + track_id + ']')

	tr.find('[name="lyrics"]').val(lyrics);
	tr.find('[name="video_url"]').val(video_url);

	modal.modal('hide');
};

//Load the optional data modal for tracks
function loadOptionalModal (track_id) {
	var modal = $('#optional-modal'),
	modalTitle = modal.find('.modal-title')
	tr = $('tr[data-track_id=' + track_id + ']'),
	name = tr.find('[name="name"]').val() || 'Additional Track Details',
	lyrics = tr.find('[name="lyrics"]').val(),
	video_url = tr.find('[name="video_url"]').val()

	//Set modal's track id attribute
	modal.data('track_id', track_id);
	modalTitle.text(name);
	modal.find('[name="lyrics"]').val(lyrics);
	modal.find('[name="video_url"]').val(video_url);
	modal.modal();
};

//Automatically clear all info when the modal closes
$(function () {
	$('#optional-modal').on('hide.bs.modal', function(){
		var themodal = $('#optional-modal')
		themodal.find('input, textarea').val('');
		themodal.data('track_id', '');
	});
});

//Serialize tracks table
function serializeRow (jqueryObj) {
	var data = jqueryObj.find('input, textarea').serialize()
	console.log(data);
};

//Update all track data
function updateFiles (filetype) {
	if (filetype == 'images'){
		var holder = $('#images-holder'),
		endpoint = '/image-list/'//image_list_url
	} else {
		var holder = $('#tracks-holder'),
		endpoint = '/track-list/'//track_list_url
	}

	window.num_success = [];
	window.num_error = [];
	var calls = []

	holder.find('tbody tr').each(function(i, v){

		$(v).find('textarea, input').parsley().validate();

		var doublecheck = true

		if (filetype == 'tracks'){
			if ($(v).find('textarea').val() == ''){
				var doublecheck = false
			}
		}

		//Only bother if the form is not valid
		if ($(v).find('textarea, input').parsley().validate() == true && doublecheck){
			//console.log('Row #' + i + ' is valid!');

			//Images
			if (filetype == 'images') {
				var obj = $(v),
				image_id = obj.data('image_id'),
				object_id = image_id,
				order = obj.find('[name="order"]').val(),

				//Here, the name is the caption
				caption = obj.find('[name="name"]').val(),

				//Construct the array first
				thedata = JSON.stringify({
					'order': order,
					'name': caption
				})

			//Tracks
			} else if (filetype == 'tracks'){
                            if ($(v).find('[name="artists"]').select2('val') != '[object Object]'){
                                artis = $(v).find('[name="artists"]').select2('val');
                            }
                            else{
                                artis = $(v).find('td:nth-child(4)').find('span:first').text();
                            }
                            if ($(v).find('[name="producers"]').select2('val') != '[object Object]'){
                                produc = $(v).find('[name="producers"]').select2('val');
                            }
                            else{
                                produc = $(v).find('td:nth-child(5)').find('span:first').text();
                            }
                            if ($(v).find('[name="djs"]').select2('val') != '[object Object]'){
                                dj = $(v).find('[name="djs"]').select2('val');
                            }
                            else{
                                dj = $(v).find('td:nth-child(6)').find('span:first').text();
                            }
				var obj = $(v),
				track_id = obj.data('track_id'),
				object_id = track_id,
				order = obj.find('[name="order"]').val(),
				name = obj.find('[name="name"]').val(),
				artists = artis,
				producers = produc,
				djs = dj,
				lyrics = obj.find('[name="lyrics"]').val(),
				video_url = obj.find('[name="video_url"]').val(),


				//Construct the array first
				thedata = JSON.stringify({
					'order': order,
					'name': name,
					'artists': artists,
					'producers': producers,
					'djs': djs,
					'lyrics': lyrics,
					'video_url': video_url
				})
			};

			calls.push(
				//Specify contentType when sending the patch
				$.ajax({
					//contentType: 'application/JSON',
					url: endpoint,
					type: 'POST',
                                        async: false,
					data: {
						'order': order,
						'name': name,
						'artists': artists,
						'producers': producers,
						'djs': djs,
						'lyrics': lyrics,
						'video_url': video_url,
						'track_id' :track_id
					},
					success: function (data) {
						window.num_success.push(1);
						$(v).fadeOut().remove();
					},
					error: function(data){
						console.log(data);
					}
				})
			);

		//else, add to the failed list
		} else {
			window.num_error.push(1)
                        // console.log('NUM ERRORS: ' + window.num_error.length)
		}
	});

	$.when.apply($, calls).done(function(){
		//If everything is fine, reload the table
		if (window.num_error.length == 0){
			//console.log('THERE ARE ACTUALLY ' + window.num_error.length + ' errors in the queue!')

			var mixtape_id = $('#mixtape_data_next').data('current_mixtape_id'),
			content_type_id = $('#mixtape_data_next').data('current_mixtape_content_type_id')

			getEntries(filetype, mixtape_id, content_type_id);
		}
	});
};

//Wire up the buttons
$(function () {
	$('#update_tracks').click(function(){
		updateFiles('tracks');
	});
	$('#update_images').click(function(){
		updateFiles('images');
	});
});

//Clear everything on close of the add userprofile modal
$(function() {
	$('#add_userprofile_modal').on('hidden.bs.modal', function(){
                $('#form_messages').empty();
		$(this).find('input, textarea').val('')
	})
});

function submit_userprofile_add () {
	var modal = $('#add_userprofile_modal')

	if (modal.find('form').parsley().validate()){
		var data = modal.find('form').serialize(),
		name = modal.find('form input[name="username"]').val()
		$.ajax({
			url: 'userprofile-list',//userprofile_list_url,
			type: 'post',
			data: data,
			success: function(data){
				$.pnotify({
					title: 'Success',
					text: name + ' created',
					icon: 'fa fa-check-circle',
					type: 'success'
				});
				modal.modal('hide');
			},
			error: function(data){
				$.pnotify({
					title: 'Error',
					text: data.responseText,
					icon: 'fa fa-exclamation-circle',
					type: 'error'
				})
			}
		});
	}
};



$('#all_done').click(function () {
	current_mixtape_id = $('#mixtape_data_next').data('current_mixtape_id')
	$.ajax({
			url: '/notifyadmin/',
			type: 'post',
			data: {'mixtape_id': current_mixtape_id},
			success: function (data) {
				$("#done-message").removeClass("hidden");
			},
			error: function(data){
				console.log('it did not work');
			}
		});
	
});
