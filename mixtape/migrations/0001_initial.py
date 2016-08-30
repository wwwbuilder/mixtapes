# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AddonCategory'
        db.create_table(u'mixtape_addoncategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'mixtape_addoncategory_updated', null=True, to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'mixtape_addoncategory_created', null=True, to=orm['auth.User'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200, blank=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['mixtape.AddonCategory'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'mixtape', ['AddonCategory'])

        # Adding model 'AddonType'
        db.create_table(u'mixtape_addontype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'mixtape_addontype_updated', null=True, to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'mixtape_addontype_created', null=True, to=orm['auth.User'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200, blank=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['mixtape.AddonType'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='addontypes', null=True, to=orm['mixtape.AddonCategory'])),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'mixtape', ['AddonType'])

        # Adding model 'AddonCharge'
        db.create_table(u'mixtape_addoncharge', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'mixtape_addoncharge_updated', null=True, to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'mixtape_addoncharge_created', null=True, to=orm['auth.User'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['mixtape.AddonCharge'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('end_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('charge', self.gf('django.db.models.fields.related.ForeignKey')(related_name='addon_charges', to=orm['payments.Charge'])),
            ('addon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mixtape.AddonType'])),
        ))
        db.send_create_signal(u'mixtape', ['AddonCharge'])

        # Adding model 'Genre'
        db.create_table(u'mixtape_genre', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'mixtape_genre_updated', null=True, to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'mixtape_genre_created', null=True, to=orm['auth.User'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200, blank=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['mixtape.Genre'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'mixtape', ['Genre'])

        # Adding model 'Mixtape'
        db.create_table(u'mixtape_mixtape', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'mixtape_mixtape_updated', null=True, to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'mixtape_mixtape_created', null=True, to=orm['auth.User'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200, blank=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['mixtape.Mixtape'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('primaryGenre', self.gf('django.db.models.fields.related.ForeignKey')(related_name='mixtape_primaryGenre', to=orm['mixtape.Genre'])),
            ('primaryArtist', self.gf('django.db.models.fields.related.ForeignKey')(related_name='mixtape_primaryArtist', to=orm['userprofile.UserProfile'])),
            ('video_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('releaseDatetime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 8, 20, 0, 0), null=True, blank=True)),
            ('editable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('soundcloud_id', self.gf('django.db.models.fields.IntegerField')(max_length=100, null=True, blank=True)),
            ('soundcloud_uri', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('soundcloud_permalink', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('soundcloud_playback_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('soundcloud_favoritings_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('soundcloud_comment_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('use_soundcloud_player', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'mixtape', ['Mixtape'])

        # Adding unique constraint on 'Mixtape', fields ['primaryArtist', 'slug', 'created_by']
        db.create_unique(u'mixtape_mixtape', ['primaryArtist_id', 'slug', 'created_by_id'])

        # Adding model 'Track'
        db.create_table(u'mixtape_track', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'mixtape_track_updated', null=True, to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'mixtape_track_created', null=True, to=orm['auth.User'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200, blank=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['mixtape.Track'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('mimetype', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('size', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('isWriteable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('mixtape', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tracks', to=orm['mixtape.Mixtape'])),
            ('lyrics', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('video_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('soundcloud_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('soundcloud_uri', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('soundcloud_permalink', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('soundcloud_playback_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('soundcloud_favoritings_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('soundcloud_comment_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'mixtape', ['Track'])

        # Adding M2M table for field genres on 'Track'
        m2m_table_name = db.shorten_name(u'mixtape_track_genres')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('track', models.ForeignKey(orm[u'mixtape.track'], null=False)),
            ('genre', models.ForeignKey(orm[u'mixtape.genre'], null=False))
        ))
        db.create_unique(m2m_table_name, ['track_id', 'genre_id'])

        # Adding M2M table for field artists on 'Track'
        m2m_table_name = db.shorten_name(u'mixtape_track_artists')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('track', models.ForeignKey(orm[u'mixtape.track'], null=False)),
            ('userprofile', models.ForeignKey(orm[u'userprofile.userprofile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['track_id', 'userprofile_id'])

        # Adding M2M table for field producers on 'Track'
        m2m_table_name = db.shorten_name(u'mixtape_track_producers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('track', models.ForeignKey(orm[u'mixtape.track'], null=False)),
            ('userprofile', models.ForeignKey(orm[u'userprofile.userprofile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['track_id', 'userprofile_id'])

        # Adding M2M table for field djs on 'Track'
        m2m_table_name = db.shorten_name(u'mixtape_track_djs')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('track', models.ForeignKey(orm[u'mixtape.track'], null=False)),
            ('userprofile', models.ForeignKey(orm[u'userprofile.userprofile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['track_id', 'userprofile_id'])

        # Adding model 'MixtapePageView'
        db.create_table(u'mixtape_mixtapepageview', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('mixtape', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pageview', to=orm['mixtape.Mixtape'])),
        ))
        db.send_create_signal(u'mixtape', ['MixtapePageView'])

        # Adding model 'MixtapeSpotLight'
        db.create_table(u'mixtape_mixtapespotlight', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(related_name='artist', to=orm['userprofile.UserProfile'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'mixtape', ['MixtapeSpotLight'])


    def backwards(self, orm):
        # Removing unique constraint on 'Mixtape', fields ['primaryArtist', 'slug', 'created_by']
        db.delete_unique(u'mixtape_mixtape', ['primaryArtist_id', 'slug', 'created_by_id'])

        # Deleting model 'AddonCategory'
        db.delete_table(u'mixtape_addoncategory')

        # Deleting model 'AddonType'
        db.delete_table(u'mixtape_addontype')

        # Deleting model 'AddonCharge'
        db.delete_table(u'mixtape_addoncharge')

        # Deleting model 'Genre'
        db.delete_table(u'mixtape_genre')

        # Deleting model 'Mixtape'
        db.delete_table(u'mixtape_mixtape')

        # Deleting model 'Track'
        db.delete_table(u'mixtape_track')

        # Removing M2M table for field genres on 'Track'
        db.delete_table(db.shorten_name(u'mixtape_track_genres'))

        # Removing M2M table for field artists on 'Track'
        db.delete_table(db.shorten_name(u'mixtape_track_artists'))

        # Removing M2M table for field producers on 'Track'
        db.delete_table(db.shorten_name(u'mixtape_track_producers'))

        # Removing M2M table for field djs on 'Track'
        db.delete_table(db.shorten_name(u'mixtape_track_djs'))

        # Deleting model 'MixtapePageView'
        db.delete_table(u'mixtape_mixtapepageview')

        # Deleting model 'MixtapeSpotLight'
        db.delete_table(u'mixtape_mixtapespotlight')


    models = {
        u'_misc.image': {
            'Meta': {'object_name': 'Image'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'_misc_image_created'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isWriteable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['_misc.Image']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'_misc_image_updated'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'locality.country': {
            'Meta': {'ordering': "('iso2', 'name')", 'object_name': 'Country'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso2': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'iso3': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'locality.territory': {
            'Meta': {'ordering': "('abbr', 'name')", 'object_name': 'Territory'},
            'abbr': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'territories'", 'to': u"orm['locality.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'mixtape.addoncategory': {
            'Meta': {'object_name': 'AddonCategory'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'mixtape_addoncategory_created'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['mixtape.AddonCategory']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'mixtape_addoncategory_updated'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'mixtape.addoncharge': {
            'Meta': {'object_name': 'AddonCharge'},
            'addon': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mixtape.AddonType']"}),
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'addon_charges'", 'to': u"orm['payments.Charge']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'mixtape_addoncharge_created'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['mixtape.AddonCharge']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'mixtape_addoncharge_updated'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'mixtape.addontype': {
            'Meta': {'object_name': 'AddonType'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'addontypes'", 'null': 'True', 'to': u"orm['mixtape.AddonCategory']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'mixtape_addontype_created'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['mixtape.AddonType']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'mixtape_addontype_updated'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'mixtape.genre': {
            'Meta': {'object_name': 'Genre'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'mixtape_genre_created'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['mixtape.Genre']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'mixtape_genre_updated'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'mixtape.mixtape': {
            'Meta': {'unique_together': "(('primaryArtist', 'slug', 'created_by'),)", 'object_name': 'Mixtape'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'mixtape_mixtape_created'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'editable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['mixtape.Mixtape']"}),
            'primaryArtist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mixtape_primaryArtist'", 'to': u"orm['userprofile.UserProfile']"}),
            'primaryGenre': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mixtape_primaryGenre'", 'to': u"orm['mixtape.Genre']"}),
            'releaseDatetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 8, 20, 0, 0)', 'null': 'True', 'blank': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'blank': 'True'}),
            'soundcloud_comment_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'soundcloud_favoritings_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'soundcloud_id': ('django.db.models.fields.IntegerField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'soundcloud_permalink': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'soundcloud_playback_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'soundcloud_uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'mixtape_mixtape_updated'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'use_soundcloud_player': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'video_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'mixtape.mixtapepageview': {
            'Meta': {'object_name': 'MixtapePageView'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mixtape': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pageview'", 'to': u"orm['mixtape.Mixtape']"})
        },
        u'mixtape.mixtapespotlight': {
            'Meta': {'object_name': 'MixtapeSpotLight'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'artist'", 'to': u"orm['userprofile.UserProfile']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'mixtape.track': {
            'Meta': {'object_name': 'Track'},
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'artist_tracks'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['userprofile.UserProfile']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'mixtape_track_created'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'djs': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'dj_tracks'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['userprofile.UserProfile']"}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'genres': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'genre_tracks'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['mixtape.Genre']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isWriteable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lyrics': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'mixtape': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tracks'", 'to': u"orm['mixtape.Mixtape']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['mixtape.Track']"}),
            'producers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'producer_tracks'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['userprofile.UserProfile']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'blank': 'True'}),
            'soundcloud_comment_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'soundcloud_favoritings_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'soundcloud_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'soundcloud_permalink': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'soundcloud_playback_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'soundcloud_uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'mixtape_track_updated'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'video_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'payments.charge': {
            'Meta': {'object_name': 'Charge'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2'}),
            'amount_refunded': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2'}),
            'card_kind': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'card_last_4': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'}),
            'charge_created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'charges'", 'to': u"orm['payments.Customer']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'disputed': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'fee': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'charges'", 'null': 'True', 'to': u"orm['payments.Invoice']"}),
            'paid': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'receipt_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'refunded': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'stripe_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'payments.customer': {
            'Meta': {'object_name': 'Customer'},
            'card_fingerprint': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'card_kind': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'card_last_4': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_purged': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stripe_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True'})
        },
        u'payments.invoice': {
            'Meta': {'ordering': "['-date']", 'object_name': 'Invoice'},
            'attempted': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'attempts': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'charge': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'to': u"orm['payments.Customer']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'period_end': ('django.db.models.fields.DateTimeField', [], {}),
            'period_start': ('django.db.models.fields.DateTimeField', [], {}),
            'stripe_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subtotal': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'total': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'})
        },
        u'userprofile.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'aboutme': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'cell_phone': ('django.db.models.fields.CharField', [], {'max_length': '25', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['locality.Country']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'userprofile_userprofile_created'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'download_limit': ('django.db.models.fields.PositiveIntegerField', [], {'default': '5', 'null': 'True', 'blank': 'True'}),
            'facebook': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'genres': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['mixtape.Genre']", 'null': 'True', 'blank': 'True'}),
            'google': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'official': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['userprofile.UserProfile']"}),
            'pinterest': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'premium': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'blank': 'True'}),
            'soundcloud': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'territory': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['locality.Territory']", 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'twitter': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'userprofile_userprofile_updated'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            'video': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'youtube': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['mixtape']