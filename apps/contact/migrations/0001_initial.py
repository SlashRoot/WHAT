# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ContactInfo'
        db.create_table('contact_contactinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('address_line2', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('postal_code', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('contact', ['ContactInfo'])

        # Adding M2M table for field websites on 'ContactInfo'
        db.create_table('contact_contactinfo_websites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contactinfo', models.ForeignKey(orm['contact.contactinfo'], null=False)),
            ('link', models.ForeignKey(orm['social.link'], null=False))
        ))
        db.create_unique('contact_contactinfo_websites', ['contactinfo_id', 'link_id'])

        # Adding model 'PhoneNumber'
        db.create_table('contact_phonenumber', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('number', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(unique=True, max_length=20)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='phone_numbers', null=True, to=orm['contact.ContactInfo'])),
        ))
        db.send_create_signal('contact', ['PhoneNumber'])

        # Adding model 'PhoneProvider'
        db.create_table('contact_phoneprovider', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('contact', ['PhoneProvider'])

        # Adding model 'AdditionalEmail'
        db.create_table('contact_additionalemail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75)),
            ('contact_info', self.gf('django.db.models.fields.related.ForeignKey')(related_name='additional_emails', to=orm['contact.ContactInfo'])),
        ))
        db.send_create_signal('contact', ['AdditionalEmail'])

        # Adding model 'Message'
        db.create_table('contact_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('contact', ['Message'])

        # Adding model 'MailHandlerAction'
        db.create_table('contact_mailhandleraction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('contact', ['MailHandlerAction'])

        # Adding model 'MailHandler'
        db.create_table('contact_mailhandler', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('contact', ['MailHandler'])

        # Adding M2M table for field actions on 'MailHandler'
        db.create_table('contact_mailhandler_actions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mailhandler', models.ForeignKey(orm['contact.mailhandler'], null=False)),
            ('mailhandleraction', models.ForeignKey(orm['contact.mailhandleraction'], null=False))
        ))
        db.create_unique('contact_mailhandler_actions', ['mailhandler_id', 'mailhandleraction_id'])

        # Adding M2M table for field users on 'MailHandler'
        db.create_table('contact_mailhandler_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mailhandler', models.ForeignKey(orm['contact.mailhandler'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('contact_mailhandler_users', ['mailhandler_id', 'user_id'])

        # Adding M2M table for field groups on 'MailHandler'
        db.create_table('contact_mailhandler_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mailhandler', models.ForeignKey(orm['contact.mailhandler'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('contact_mailhandler_groups', ['mailhandler_id', 'group_id'])

        # Adding model 'MailMessage'
        db.create_table('contact_mailmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.TextField')()),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('recipient', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('sender', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('contact', ['MailMessage'])

        # Adding model 'DialList'
        db.create_table('contact_diallist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('contact', ['DialList'])

        # Adding model 'DialListParticipation'
        db.create_table('contact_diallistparticipation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.related.ForeignKey')(related_name='dial_lists', to=orm['contact.PhoneNumber'])),
            ('list', self.gf('django.db.models.fields.related.ForeignKey')(related_name='numbers', to=orm['contact.DialList'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('green_phone', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('contact', ['DialListParticipation'])

        # Adding unique constraint on 'DialListParticipation', fields ['number', 'list']
        db.create_unique('contact_diallistparticipation', ['number_id', 'list_id'])

        # Adding model 'DialListClientParticipation'
        db.create_table('contact_diallistclientparticipation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='dial_lists_as_client', to=orm['auth.User'])),
            ('list', self.gf('django.db.models.fields.related.ForeignKey')(related_name='clients', to=orm['contact.DialList'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('contact', ['DialListClientParticipation'])

        # Adding unique constraint on 'DialListClientParticipation', fields ['user', 'list']
        db.create_unique('contact_diallistclientparticipation', ['user_id', 'list_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'DialListClientParticipation', fields ['user', 'list']
        db.delete_unique('contact_diallistclientparticipation', ['user_id', 'list_id'])

        # Removing unique constraint on 'DialListParticipation', fields ['number', 'list']
        db.delete_unique('contact_diallistparticipation', ['number_id', 'list_id'])

        # Deleting model 'ContactInfo'
        db.delete_table('contact_contactinfo')

        # Removing M2M table for field websites on 'ContactInfo'
        db.delete_table('contact_contactinfo_websites')

        # Deleting model 'PhoneNumber'
        db.delete_table('contact_phonenumber')

        # Deleting model 'PhoneProvider'
        db.delete_table('contact_phoneprovider')

        # Deleting model 'AdditionalEmail'
        db.delete_table('contact_additionalemail')

        # Deleting model 'Message'
        db.delete_table('contact_message')

        # Deleting model 'MailHandlerAction'
        db.delete_table('contact_mailhandleraction')

        # Deleting model 'MailHandler'
        db.delete_table('contact_mailhandler')

        # Removing M2M table for field actions on 'MailHandler'
        db.delete_table('contact_mailhandler_actions')

        # Removing M2M table for field users on 'MailHandler'
        db.delete_table('contact_mailhandler_users')

        # Removing M2M table for field groups on 'MailHandler'
        db.delete_table('contact_mailhandler_groups')

        # Deleting model 'MailMessage'
        db.delete_table('contact_mailmessage')

        # Deleting model 'DialList'
        db.delete_table('contact_diallist')

        # Deleting model 'DialListParticipation'
        db.delete_table('contact_diallistparticipation')

        # Deleting model 'DialListClientParticipation'
        db.delete_table('contact_diallistclientparticipation')

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
        'contact.additionalemail': {
            'Meta': {'object_name': 'AdditionalEmail'},
            'contact_info': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'additional_emails'", 'to': "orm['contact.ContactInfo']"}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'contact.contactinfo': {
            'Meta': {'object_name': 'ContactInfo'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'address_line2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'websites': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'operators'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['social.Link']"})
        },
        'contact.diallist': {
            'Meta': {'object_name': 'DialList'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'contact.diallistclientparticipation': {
            'Meta': {'unique_together': "(['user', 'list'],)", 'object_name': 'DialListClientParticipation'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'clients'", 'to': "orm['contact.DialList']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dial_lists_as_client'", 'to': "orm['auth.User']"})
        },
        'contact.diallistparticipation': {
            'Meta': {'unique_together': "(['number', 'list'],)", 'object_name': 'DialListParticipation'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'green_phone': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'numbers'", 'to': "orm['contact.DialList']"}),
            'number': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dial_lists'", 'to': "orm['contact.PhoneNumber']"})
        },
        'contact.mailhandler': {
            'Meta': {'object_name': 'MailHandler'},
            'actions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['contact.MailHandlerAction']", 'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'contact.mailhandleraction': {
            'Meta': {'object_name': 'MailHandlerAction'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'contact.mailmessage': {
            'Meta': {'object_name': 'MailMessage'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sender': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'subject': ('django.db.models.fields.TextField', [], {})
        },
        'contact.message': {
            'Meta': {'object_name': 'Message'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'contact.phonenumber': {
            'Meta': {'object_name': 'PhoneNumber'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'unique': 'True', 'max_length': '20'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'phone_numbers'", 'null': 'True', 'to': "orm['contact.ContactInfo']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'contact.phoneprovider': {
            'Meta': {'object_name': 'PhoneProvider'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'social.link': {
            'Meta': {'object_name': 'Link'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['contact']