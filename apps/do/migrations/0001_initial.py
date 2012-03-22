# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Verb'
        db.create_table('do_verb', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('do', ['Verb'])

        # Adding model 'Task'
        db.create_table('do_task', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('prototype', self.gf('django.db.models.fields.related.ForeignKey')(related_name='instances', to=orm['do.TaskPrototype'])),
            ('projected', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('weight', self.gf('django.db.models.fields.IntegerField')()),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_tasks', to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('do', ['Task'])

        # Adding model 'TaskResolution'
        db.create_table('do_taskresolution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='resolved_tasks', to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(related_name='resolutions', to=orm['do.Task'])),
        ))
        db.send_create_signal('do', ['TaskResolution'])

        # Adding model 'TaskProgeny'
        db.create_table('do_taskprogeny', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parents', to=orm['do.Task'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='children', to=orm['do.Task'])),
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('do', ['TaskProgeny'])

        # Adding unique constraint on 'TaskProgeny', fields ['child', 'parent']
        db.create_unique('do_taskprogeny', ['child_id', 'parent_id'])

        # Adding unique constraint on 'TaskProgeny', fields ['parent', 'priority']
        db.create_unique('do_taskprogeny', ['parent_id', 'priority'])

        # Adding model 'TaskPrototype'
        db.create_table('do_taskprototype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='prototypes', to=orm['do.Verb'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_task_prototypes', to=orm['auth.User'])),
            ('weight', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('do', ['TaskPrototype'])

        # Adding model 'TaskPrototypeEvolution'
        db.create_table('do_taskprototypeevolution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('old_prototype', self.gf('django.db.models.fields.related.ForeignKey')(related_name='evolved_into', to=orm['do.TaskPrototype'])),
            ('new_prototype', self.gf('django.db.models.fields.related.ForeignKey')(related_name='evolved_from', to=orm['do.TaskPrototype'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='evolved_task_prototypes', to=orm['auth.User'])),
        ))
        db.send_create_signal('do', ['TaskPrototypeEvolution'])

        # Adding model 'TaskPrototypeProgeny'
        db.create_table('do_taskprototypeprogeny', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parents', to=orm['do.TaskPrototype'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='children', to=orm['do.TaskPrototype'])),
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('revision', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('do', ['TaskPrototypeProgeny'])

        # Adding unique constraint on 'TaskPrototypeProgeny', fields ['child', 'parent']
        db.create_unique('do_taskprototypeprogeny', ['child_id', 'parent_id'])

        # Adding unique constraint on 'TaskPrototypeProgeny', fields ['parent', 'priority']
        db.create_unique('do_taskprototypeprogeny', ['parent_id', 'priority'])

        # Adding model 'TaskGenerator'
        db.create_table('do_taskgenerator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('prototype', self.gf('django.db.models.fields.related.ForeignKey')(related_name='generators', to=orm['do.TaskPrototype'])),
        ))
        db.send_create_signal('do', ['TaskGenerator'])

        # Adding model 'RandomRecurringTaskGenerator'
        db.create_table('do_randomrecurringtaskgenerator', (
            ('taskgenerator_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['do.TaskGenerator'], unique=True, primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('frequency', self.gf('django.db.models.fields.IntegerField')()),
            ('backlog', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('timeframe', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('do', ['RandomRecurringTaskGenerator'])

        # Adding model 'ScheduledRecurringTaskGenerator'
        db.create_table('do_scheduledrecurringtaskgenerator', (
            ('taskgenerator_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['do.TaskGenerator'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('do', ['ScheduledRecurringTaskGenerator'])

        # Adding model 'EventDrivenTaskGenerator'
        db.create_table('do_eventdriventaskgenerator', (
            ('taskgenerator_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['do.TaskGenerator'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('do', ['EventDrivenTaskGenerator'])

        # Adding model 'TaskOwnership'
        db.create_table('do_taskownership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_tasks', to=orm['auth.User'])),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ownership', to=orm['do.Task'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('do', ['TaskOwnership'])

        # Adding unique constraint on 'TaskOwnership', fields ['owner', 'task']
        db.create_unique('do_taskownership', ['owner_id', 'task_id'])

        # Adding model 'TaskAccessPrototype'
        db.create_table('do_taskaccessprototype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('privilege', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tasks', to=orm['mellon.Privilege'])),
            ('type', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal('do', ['TaskAccessPrototype'])

        # Adding unique constraint on 'TaskAccessPrototype', fields ['privilege', 'type']
        db.create_unique('do_taskaccessprototype', ['privilege_id', 'type'])

        # Adding model 'TaskAccess'
        db.create_table('do_taskaccess', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('prototype', self.gf('django.db.models.fields.related.ForeignKey')(related_name='applications', to=orm['do.TaskAccessPrototype'])),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(related_name='access_requirements', to=orm['do.Task'])),
        ))
        db.send_create_signal('do', ['TaskAccess'])

        # Adding unique constraint on 'TaskAccess', fields ['prototype', 'task']
        db.create_unique('do_taskaccess', ['prototype_id', 'task_id'])

        # Adding model 'TaskRelatedObject'
        db.create_table('do_taskrelatedobject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(related_name='related_objects', to=orm['do.Task'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('do', ['TaskRelatedObject'])

        # Adding unique constraint on 'TaskRelatedObject', fields ['object_id', 'content_type', 'task']
        db.create_unique('do_taskrelatedobject', ['object_id', 'content_type_id', 'task_id'])

        # Adding model 'Protocol'
        db.create_table('do_protocol', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('do', ['Protocol'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'TaskRelatedObject', fields ['object_id', 'content_type', 'task']
        db.delete_unique('do_taskrelatedobject', ['object_id', 'content_type_id', 'task_id'])

        # Removing unique constraint on 'TaskAccess', fields ['prototype', 'task']
        db.delete_unique('do_taskaccess', ['prototype_id', 'task_id'])

        # Removing unique constraint on 'TaskAccessPrototype', fields ['privilege', 'type']
        db.delete_unique('do_taskaccessprototype', ['privilege_id', 'type'])

        # Removing unique constraint on 'TaskOwnership', fields ['owner', 'task']
        db.delete_unique('do_taskownership', ['owner_id', 'task_id'])

        # Removing unique constraint on 'TaskPrototypeProgeny', fields ['parent', 'priority']
        db.delete_unique('do_taskprototypeprogeny', ['parent_id', 'priority'])

        # Removing unique constraint on 'TaskPrototypeProgeny', fields ['child', 'parent']
        db.delete_unique('do_taskprototypeprogeny', ['child_id', 'parent_id'])

        # Removing unique constraint on 'TaskProgeny', fields ['parent', 'priority']
        db.delete_unique('do_taskprogeny', ['parent_id', 'priority'])

        # Removing unique constraint on 'TaskProgeny', fields ['child', 'parent']
        db.delete_unique('do_taskprogeny', ['child_id', 'parent_id'])

        # Deleting model 'Verb'
        db.delete_table('do_verb')

        # Deleting model 'Task'
        db.delete_table('do_task')

        # Deleting model 'TaskResolution'
        db.delete_table('do_taskresolution')

        # Deleting model 'TaskProgeny'
        db.delete_table('do_taskprogeny')

        # Deleting model 'TaskPrototype'
        db.delete_table('do_taskprototype')

        # Deleting model 'TaskPrototypeEvolution'
        db.delete_table('do_taskprototypeevolution')

        # Deleting model 'TaskPrototypeProgeny'
        db.delete_table('do_taskprototypeprogeny')

        # Deleting model 'TaskGenerator'
        db.delete_table('do_taskgenerator')

        # Deleting model 'RandomRecurringTaskGenerator'
        db.delete_table('do_randomrecurringtaskgenerator')

        # Deleting model 'ScheduledRecurringTaskGenerator'
        db.delete_table('do_scheduledrecurringtaskgenerator')

        # Deleting model 'EventDrivenTaskGenerator'
        db.delete_table('do_eventdriventaskgenerator')

        # Deleting model 'TaskOwnership'
        db.delete_table('do_taskownership')

        # Deleting model 'TaskAccessPrototype'
        db.delete_table('do_taskaccessprototype')

        # Deleting model 'TaskAccess'
        db.delete_table('do_taskaccess')

        # Deleting model 'TaskRelatedObject'
        db.delete_table('do_taskrelatedobject')

        # Deleting model 'Protocol'
        db.delete_table('do_protocol')


    models = {
        'accounting.budgetcategory': {
            'Meta': {'object_name': 'BudgetCategory'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'accounting.budgetline': {
            'Meta': {'object_name': 'BudgetLine'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounting.BudgetCategory']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
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
        'commerce.budgetperspective': {
            'Meta': {'object_name': 'BudgetPerspective'},
            'category_perspectives': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['commerce.TradeCategoryPerspective']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'commerce.quantificationdimension': {
            'Meta': {'object_name': 'QuantificationDimension'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'commerce.tradecategory': {
            'Meta': {'object_name': 'TradeCategory'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['commerce.TradeCategory']"}),
            'quantification_dimensions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['commerce.QuantificationDimension']", 'null': 'True', 'blank': 'True'})
        },
        'commerce.tradecategoryperspective': {
            'Meta': {'unique_together': "(['trade_category', 'incoming_budget_line', 'outgoing_budget_line'],)", 'object_name': 'TradeCategoryPerspective'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incoming_budget_line': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incoming_perspectives'", 'to': "orm['accounting.BudgetLine']"}),
            'outgoing_budget_line': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outgoing_perspectives'", 'to': "orm['accounting.BudgetLine']"}),
            'trade_category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'budget_perspectives'", 'to': "orm['commerce.TradeCategory']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'do.eventdriventaskgenerator': {
            'Meta': {'object_name': 'EventDrivenTaskGenerator', '_ormbases': ['do.TaskGenerator']},
            'taskgenerator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['do.TaskGenerator']", 'unique': 'True', 'primary_key': 'True'})
        },
        'do.protocol': {
            'Meta': {'object_name': 'Protocol'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'do.randomrecurringtaskgenerator': {
            'Meta': {'object_name': 'RandomRecurringTaskGenerator', '_ormbases': ['do.TaskGenerator']},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'backlog': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'frequency': ('django.db.models.fields.IntegerField', [], {}),
            'taskgenerator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['do.TaskGenerator']", 'unique': 'True', 'primary_key': 'True'}),
            'timeframe': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'do.scheduledrecurringtaskgenerator': {
            'Meta': {'object_name': 'ScheduledRecurringTaskGenerator', '_ormbases': ['do.TaskGenerator']},
            'taskgenerator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['do.TaskGenerator']", 'unique': 'True', 'primary_key': 'True'})
        },
        'do.task': {
            'Meta': {'object_name': 'Task'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_tasks'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'projected': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'prototype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'instances'", 'to': "orm['do.TaskPrototype']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {})
        },
        'do.taskaccess': {
            'Meta': {'unique_together': "(('prototype', 'task'),)", 'object_name': 'TaskAccess'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prototype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'applications'", 'to': "orm['do.TaskAccessPrototype']"}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'access_requirements'", 'to': "orm['do.Task']"})
        },
        'do.taskaccessprototype': {
            'Meta': {'unique_together': "(('privilege', 'type'),)", 'object_name': 'TaskAccessPrototype'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'privilege': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'to': "orm['mellon.Privilege']"}),
            'type': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'do.taskgenerator': {
            'Meta': {'object_name': 'TaskGenerator'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prototype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'generators'", 'to': "orm['do.TaskPrototype']"})
        },
        'do.taskownership': {
            'Meta': {'unique_together': "(('owner', 'task'),)", 'object_name': 'TaskOwnership'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_tasks'", 'to': "orm['auth.User']"}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ownership'", 'to': "orm['do.Task']"})
        },
        'do.taskprogeny': {
            'Meta': {'unique_together': "(('child', 'parent'), ('parent', 'priority'))", 'object_name': 'TaskProgeny'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parents'", 'to': "orm['do.Task']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'to': "orm['do.Task']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {})
        },
        'do.taskprototype': {
            'Meta': {'object_name': 'TaskPrototype'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_task_prototypes'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'prototypes'", 'to': "orm['do.Verb']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'do.taskprototypeevolution': {
            'Meta': {'object_name': 'TaskPrototypeEvolution'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'evolved_task_prototypes'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_prototype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'evolved_from'", 'to': "orm['do.TaskPrototype']"}),
            'old_prototype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'evolved_into'", 'to': "orm['do.TaskPrototype']"})
        },
        'do.taskprototypeprogeny': {
            'Meta': {'unique_together': "(('child', 'parent'), ('parent', 'priority'))", 'object_name': 'TaskPrototypeProgeny'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parents'", 'to': "orm['do.TaskPrototype']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'to': "orm['do.TaskPrototype']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'revision': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'do.taskrelatedobject': {
            'Meta': {'unique_together': "(('object_id', 'content_type', 'task'),)", 'object_name': 'TaskRelatedObject'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'related_objects'", 'to': "orm['do.Task']"})
        },
        'do.taskresolution': {
            'Meta': {'object_name': 'TaskResolution'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resolved_tasks'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resolutions'", 'to': "orm['do.Task']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'do.verb': {
            'Meta': {'object_name': 'Verb'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'mellon.privilege': {
            'Meta': {'object_name': 'Privilege'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jurisdiction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'prototype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mellon.PrivilegePrototype']"}),
            'very_private': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'mellon.privilegeprototype': {
            'Meta': {'object_name': 'PrivilegePrototype'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'people.genericparty': {
            'Meta': {'object_name': 'GenericParty'},
            'budget_perspectives': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['commerce.BudgetPerspective']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.Group']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'social.drawattention': {
            'Meta': {'object_name': 'DrawAttention'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'target': ('utility.models.GenericPartyForeignKey', [], {'related_name': "'notices'", 'to': "orm['people.GenericParty']"})
        },
        'social.message': {
            'Meta': {'object_name': 'Message'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {})
        },
        'social.toplevelmessage': {
            'Meta': {'object_name': 'TopLevelMessage', '_ormbases': ['social.Message']},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'message_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['social.Message']", 'unique': 'True', 'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        }
    }

    complete_apps = ['do']
