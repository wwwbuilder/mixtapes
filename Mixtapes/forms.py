from django import forms
from django.http import HttpResponseRedirect
from django.forms.models import inlineformset_factory
from django.forms import fields
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from userprofile.models import UserProfile
from mixtape.models import Mixtape
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from parsley.decorators import parsleyfy
from django.forms.models import formset_factory
import re
base_class_excludes = ('order', 'slug', 'updated', 'created', 'featured', 'promoted', 'sponsor', 'created_by',)
base_image_class_excludes = ('slug', 'updated', 'created', 'created_by')

@parsleyfy
class MixtapeCreateForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(MixtapeCreateForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'form-horizontal'
		self.helper.form_method = 'post'
		self.helper.form_action = HttpResponseRedirect('/mixtape-list')
		self.helper.form_id = 'mt-create-step1'
		self.helper.layout = Layout(
			Fieldset(
				'',
				'name',
				'primaryGenre', 
				'primaryArtist',
				Div(					
					HTML('<hr><div class="label label-info optional">Optional</div>'),
					'video_url',
					'releaseDatetime',
				),

			)
		)

	name = forms.CharField(required=True)
	primaryArtist = forms.CharField(label='Featured Artist', widget=forms.TextInput(attrs={'autocomplete':'off', 'data-storage':'false', 'autocapitalize': 'off', 'spellcheck': 'false', 'autocorrect': 'off'}))
	
	class Meta:		
		model = Mixtape

		fields = (
			'name', 
			'primaryGenre', 
			'primaryArtist',
			'video_url',
			'releaseDatetime',
			)

		#Explicit exclude is needed for form validation in the view
		exclude = base_class_excludes + (
			'listens', 'rank', 'editable', 'approved', 'addons', 
			'soundcloud_id', 'soundcloud_uri', 'soundcloud_permalink',
			)
		
@parsleyfy
class UserProfileCreateForm(forms.ModelForm):

	class Meta:
		model = UserProfile
		exclude = (
	                'created_by', 'user', 'slug', 'official', 'premium',
	                'download_limit',
	                )
		fields = ('username', 'genres',)


@parsleyfy
class UserProfileUpdateForm(forms.ModelForm):
	user=None
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('place_user',None)
		super(UserProfileUpdateForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'form-horizontal'
		self.helper.form_method = 'post'
		self.helper.form_action = HttpResponseRedirect('/my-profile')
		self.helper.layout = Layout(
			Fieldset(
				'',
				Div(
					HTML('<h3>Basic Info</h3>'),
					'username',
					'video',
					'homepage',
					css_class='alert alert-success'
				),
				HTML('<hr>'),
				Div(			
					HTML('<h3>Social Media</h3>'),
					PrependedText('facebook', '<i class="icon-facebook"></i>', placeholder='http://www.facebook.com/<your_handle>', css_class='span8'),
					PrependedText('twitter', '<i class="icon-twitter"></i>', placeholder='http://www.twitter.com/<your_handle>', css_class='span8'),
					PrependedText('google', '<i class="icon-google-plus"></i>', placeholder='http://plus.google.com/u/0/<your_handle>/posts', css_class='span8'),
					PrependedText('youtube', '<i class="icon-youtube-play"></i>', placeholder='http://www.youtube.com/user/<your_handle>?feature=watch', css_class='span8'),
					PrependedText('pinterest', '<i class="icon-pinterest"></i>', placeholder='http://pinterest.com/<your_handle>', css_class='span8'),
					css_class='alert alert-warning'
					)
				),
				ButtonHolder(
					Submit('submit', 'Submit', css_class='btn btn-large btn-success')
				)
			)

	username = forms.CharField(label='Username', help_text='You may change your username at any time, but <strong>be careful!</strong> This will affect old links to your mixtapes and profile page.')
	#genres = forms.ModelMultipleChoiceField(label='Genres', help_text='What type of music do you create?', queryset=Genre.objects.all(), widget=forms.CheckboxSelectMultiple)
	video = forms.URLField(required=False, label='Profile Video', help_text='This will be displayed on your own profile page. Include a YouTube or Vimeo link to your newest track or vlog.')
	google = forms.URLField(required=False, label='Instagram')
	aboutme = forms.CharField(label='Description',max_length = 160)
	
	def clean_username(self):
		username = self.cleaned_data['username']
		if self.user.username not in (username.strip(),None):
			if UserProfile.objects.filter(username=username).exists():
			    raise forms.ValidationError('Username already exists.', code='invalid')
		return username	
	   
	
	
	def clean(self):
		return self.cleaned_data
	   
	def clean_facebook(self):
		s='^(https?|ftp)://[^\s/$.?#].[^\s]*$'
		facebook = self.cleaned_data['facebook']
		if facebook != '':
			result = re.match(s,facebook)
			if result != None:
				if 'facebook.com' not in facebook:
					raise forms.ValidationError('Invalid facebook Url.', code='invalid')
			else:
				raise forms.ValidationError('Invalid facebook Url.', code='invalid')
		return facebook	
	   
	def clean_twitter(self):
		
		s='^(https?|ftp)://[^\s/$.?#].[^\s]*$'
		twitter = self.cleaned_data['twitter']
		if twitter !='':
			result = re.match(s,twitter)
			if result != None:
			    if 'twitter.com' not in twitter:
			    	raise forms.ValidationError('Invalid twitter Url.', code='invalid')
			else:
				raise forms.ValidationError('Invalid twitter Url.', code='invalid')
			return twitter
	
	def clean_google(self):
		#return self.cleaned_data['google']
		s='^(https?|ftp)://[^\s/$.?#].[^\s]*$'
		google = self.cleaned_data['google']
		if google != '':
			result = re.match(s,google)
			if result != None:
				if 'instagram.com' not in google:
					raise forms.ValidationError('Invalid Instagram Url.', code='invalid')
			else:
				raise forms.ValidationError('Invalid Instagram Url.', code='invalid')
			return google

	def clean_youtube(self):
		
		s='^(https?|ftp)://[^\s/$.?#].[^\s]*$'
		youtube = self.cleaned_data['youtube']
		if youtube != '':
			result = re.match(s,youtube)
			if result != None:
			    if 'youtube.com' not in youtube:
			    	raise forms.ValidationError('Invalid youtube Url.', code='invalid')
			else:
				raise forms.ValidationError('Invalid youtube Url.', code='invalid')
			return youtube	
	  

	class Meta:		
		model = UserProfile
		
		fields = (
				    'username', 
				    'aboutme',
				    'video', 
				    'facebook',
				    'twitter',
		            'google',
		            'youtube',
		            		            
				    )		

		exclude = (
			'created_by', 'user', 'slug', 'official', 'premium',
			'download_limit', 'soundcloud', 'genre',
			)