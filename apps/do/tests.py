from django.test import TestCase 

from django.test.client import Client

from django.contrib.auth.models import User
from do.models import Task, TaskPrototype, TaskPrototypeProgeny, Verb
from people.models import GenericParty

from unittest import expectedFailure

def make_task_tree(test_case):
    test_case.user = User.objects.create(username="test_user", email="test_user@nowhere.com")
    test_case.user.set_password('test_password')
    test_case.user.save()
    
    #Create an verb to associate our TaskPrototypes
    test_case.verb = Verb.objects.create(name="Test_Verb", description="test_description")        
    
    #Create TaskPrototype events
    top_prototype = TaskPrototype.objects.create(name="Top Task", weight=10, type=test_case.verb, creator=test_case.user)
    
    #Two children of the top task.
    second_level = TaskPrototype.objects.create(name="Second Level", weight=10, type=test_case.verb, creator=test_case.user)
    second_level_deadend = TaskPrototype.objects.create(name="Second Level Dead End", weight=10, type=test_case.verb, creator=test_case.user)
    
    #....and the progeny objects to enforce them.
    highest_progeny = TaskPrototypeProgeny.objects.create(parent=top_prototype, child=second_level, priority=1)
    deadend_progeny = TaskPrototypeProgeny.objects.create(parent=top_prototype, child=second_level_deadend, priority=3)
    
    #Two children of the second-level task.
    third_level_a = TaskPrototype.objects.create(name="Third Level task A", weight=10, type=test_case.verb, creator=test_case.user)
    third_level_b = TaskPrototype.objects.create(name="Third Level task B", weight=10, type=test_case.verb, creator=test_case.user)
    
    #...and again, their progeny.        
    second_progeny_a = TaskPrototypeProgeny.objects.create(parent=second_level, child=third_level_a, priority=1)
    second_progeny_b = TaskPrototypeProgeny.objects.create(parent=second_level, child=third_level_b, priority=2)        
    
    test_case.task_tree = top_prototype.instantiate(creator=test_case.user) #Don't forget - the instantiate() method returns a Task
    
    return test_case.task_tree

class TestTaskGenerator(TestCase):
    def setUp(self):
        make_task_tree(self)
        
    def testDoLanding(self):
        logged_in = self.client.login(username='test_user', password='test_password')
        self.assertTrue(logged_in, "The test user did not login successfully.")
        response = self.client.get('/do/')
        self.assertEqual(response.status_code, 200)
            
    def test_that_top_level_task_is_a_Task(self):
        '''
        Creates task tree out of a TaskPrototype family.  Has three levels of progeny.
        '''
        self.assertIsInstance(self.task_tree, Task)
    
    def test_that_top_task_has_exactly_two_children(self):
        '''
        As you can see above, we created the top-level task to have two children (one of which is a "dead-end")
        '''
        self.assertEqual(self.task_tree.children.count(), 2, "The top-level task did not have exactly two children, as we expected it to.")        
        
    def test_verb(self):
        self.assertIsInstance(self.verb, Verb)
        self.assertIsInstance(self.verb.get_open_tasks()[0], Task)
    
    def test_that_task_initial_status_is_zero(self):
        self.assertEqual(self.task_tree.status, 0)
    
    @expectedFailure 
    def testTaskForm(self):
        self.fail('AccessRequirements are not yet modeled in the test.  boo.') #Comment out to see the error / traceback.
        
        #task_form = TaskForm
        #Assert that the proper fields exist on TaskForm
        new_task_post_dict = {
                              'lookup_name': 'test_task',
                              'type': '1', #type is a PK integer for verb; we created it in setup
                              }
        self.client.login(username='test_user', password='test_password')
        response = self.client.post('/do/task_form_handler', new_task_post_dict)
        self.assertEqual(response.status_code, 200, "The response to the form submission was not a 200.")
    
    def test_that_after_owning_a_task_that_in_fact_the_new_owner_owns_the_task(self):
        ownership = self.task_tree.ownership.create(owner=self.user)
        self.assertIn(ownership, self.task_tree.ownership.all(), "The ownership object did not appear in the ownership objects listed for the task.")
        self.assertIn(self.user, self.task_tree.owners(), "The .owners() method did not list the new owner.")
        return self.task_tree
        
    
    @expectedFailure
    def testTaskFormSubmit(self):
        #Assert several rounds of validation errors
        self.fail()
    
    @expectedFailure
    def testPrototypeEvolutionSubmit(self):
        #Assert that someone of insuffient permissions is unable to complete the submission
        self.fail()
        
    def tearDown(self):
        self.user.delete()
        self.verb.delete()
        self.task_tree.delete()
        
class NewDoTests(TestCase):
    
    @expectedFailure    
    def test_(self):
        self.fail()