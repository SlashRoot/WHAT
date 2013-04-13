# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Page'
        db.create_table('cms_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('cms', ['Page'])

        # Adding model 'ContentBlock'
        db.create_table('cms_contentblock', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('headline', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('subhead', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('cms', ['ContentBlock'])

        # Adding model 'QandA'
        db.create_table('cms_qanda', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('cms', ['QandA'])

        # Adding model 'Question'
        db.create_table('cms_question', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
            ('answer_type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('cms', ['Question'])

        # Adding model 'QuestionOnForm'
        db.create_table('cms_questiononform', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cms.QandA'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cms.Question'])),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('cms', ['QuestionOnForm'])

        # Adding model 'Answer'
        db.create_table('cms_answer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('application', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answers', to=orm['cms.QandA'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answers', to=orm['cms.Question'])),
        ))
        db.send_create_signal('cms', ['Answer'])

        # Adding model 'BooleanAnswer'
        db.create_table('cms_booleananswer', (
            ('answer_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.Answer'], unique=True, primary_key=True)),
            ('answer', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('cms', ['BooleanAnswer'])

        # Adding model 'TextAnswer'
        db.create_table('cms_textanswer', (
            ('answer_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.Answer'], unique=True, primary_key=True)),
            ('answer', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('cms', ['TextAnswer'])

    def backwards(self, orm):
        # Deleting model 'Page'
        db.delete_table('cms_page')

        # Deleting model 'ContentBlock'
        db.delete_table('cms_contentblock')

        # Deleting model 'QandA'
        db.delete_table('cms_qanda')

        # Deleting model 'Question'
        db.delete_table('cms_question')

        # Deleting model 'QuestionOnForm'
        db.delete_table('cms_questiononform')

        # Deleting model 'Answer'
        db.delete_table('cms_answer')

        # Deleting model 'BooleanAnswer'
        db.delete_table('cms_booleananswer')

        # Deleting model 'TextAnswer'
        db.delete_table('cms_textanswer')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cms.answer': {
            'Meta': {'object_name': 'Answer'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': "orm['cms.QandA']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': "orm['cms.Question']"})
        },
        'cms.booleananswer': {
            'Meta': {'object_name': 'BooleanAnswer', '_ormbases': ['cms.Answer']},
            'answer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'answer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.Answer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'cms.contentblock': {
            'Meta': {'object_name': 'ContentBlock'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'subhead': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'cms.page': {
            'Meta': {'object_name': 'Page'},
            'created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cms.qanda': {
            'Meta': {'object_name': 'QandA'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'questions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cms.Question']", 'through': "orm['cms.QuestionOnForm']", 'symmetrical': 'False'})
        },
        'cms.question': {
            'Meta': {'object_name': 'Question'},
            'answer_type': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'})
        },
        'cms.questiononform': {
            'Meta': {'object_name': 'QuestionOnForm'},
            'form': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.QandA']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Question']"}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'cms.textanswer': {
            'Meta': {'object_name': 'TextAnswer', '_ormbases': ['cms.Answer']},
            'answer': ('django.db.models.fields.TextField', [], {}),
            'answer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.Answer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        }
    }

    complete_apps = ['cms']