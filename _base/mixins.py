from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.text import slugify

#http://stackoverflow.com/questions/10689845/django-accessing-foreign-keys-manager-from-django-templates

class NotDeletedQuerySet(models.query.QuerySet):
	def not_deleted(self):
		return self.filter(deleted=False)

class NotDeletedManager(models.Manager):
	use_for_related_fields = True

	def get_queryset(self):
		return NotDeletedQuerySet(self.model)

	def not_deleted(self, *args, **kwargs):
		return self.get_query_set().not_deleted(*args, **kwargs)

class BaseMixin(models.Model):
	updated = models.DateTimeField(auto_now=True)
	updated_by = models.ForeignKey(User, blank=True, null=True, related_name='%(app_label)s_%(class)s_updated')
	created = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, blank=True, null=True, related_name='%(app_label)s_%(class)s_created')
	deleted = models.BooleanField(default=False)

	order = models.PositiveIntegerField(blank=True, null=True)
	name = models.CharField(max_length=200, blank=True)
	slug = models.SlugField(max_length=200, blank=True)

	objects = NotDeletedManager()

	class Meta:
		abstract = True
		ordering = ['order']

	def __unicode__(self):
		return ('%s: %s') % (self.created_by, self.created)

	def save(self, *args, **kwargs):
		#self.name = self.name
		#self.slug = slugify(self.name)
		super(BaseMixin, self).save(*args, **kwargs)

class GenericFKMixin(models.Model):
	#Below are the standard generic foreignkey fields
	#https://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/

	content_type = models.ForeignKey(ContentType, blank=True, null=True)
	object_id = models.PositiveIntegerField()
	content_object = generic.GenericForeignKey('content_type', 'object_id')

	class Meta:
		abstract = True