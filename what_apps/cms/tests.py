from utility.tests import WHATTestCase
from unittest import expectedFailure
from cms.models import Question, QandA, QuestionOnForm, BooleanAnswer, ContentBlock
from utility.tests import test_user_factory


import do.config

class Blogging(WHATTestCase):
    
    success_urls = ['/blog/']
    login_required_urls = ['/cms/edit_content_block/']
    
    def setUp(self):
        do.config.set_up()
        self.users = test_user_factory(1)

    def test_blog_editor_200_logged_in(self):
        self.client.login(username=self.users[0].username, password='password')
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
    
    def test_blog_submission_creates_blog_object(self):
        self.assertEqual(ContentBlock.objects.count(), 0)
        self.client.login(username=self.users[0].username, password='password')
        post_response = self.client.post('/cms/edit_content_block/', {'headline': 'My really awesome blog post.', 'content':'yep, this is the post.', 'published':True, 'tags': 'public,blog'})
        self.assertEqual(post_response.status_code, 200)
        
        self.assertEqual(ContentBlock.objects.count(), 1)
        
        return ContentBlock.objects.all()[0]
    
    def test_submitted_blog_appears_on_blog_page(self):
        blog_post = self.test_blog_submission_creates_blog_object()
        blog_front_page_response = self.client.get('/blog/')
        self.assertTrue(blog_post.content in blog_front_page_response.content)
        
    def test_submitted_blog_appears_on_permalink_page(self):
        blog_post = self.test_blog_submission_creates_blog_object()
        blog_url = blog_post.get_absolute_url()
        response = self.assertPageLoadSuccess(blog_url)
        
        self.assertTrue(blog_post.content in response.content)
        
    def test_bad_blog_title_404(self):
        self.assertStatusCode('/blog/this-post-definitely-does-not-exist/', 404)
        
    def test_for_two_blog_posts_that_the_content_of_one_does_not_appear_on_the_permalink_of_the_other(self):
        first_blog_post = self.test_blog_submission_creates_blog_object() 
        self.client.login(username=self.users[0].username, password='password')
        
        second_headline = 'A second post - nothing to do with the first.'
        post_response = self.client.post('/cms/edit_content_block/', {'headline':  second_headline, 'content':'Some other post for sure.', 'published':True, 'tags': 'public,blog'})
        second_blog_post = ContentBlock.objects.get(headline=second_headline)
        
        first_blog_post_permalink_response = self.assertPageLoadSuccess(first_blog_post.get_absolute_url())
        
        self.assertTrue(first_blog_post.content in first_blog_post_permalink_response.content)
        self.assertFalse(second_blog_post.content in first_blog_post_permalink_response.content)

        
    @expectedFailure
    def test_blog_permalink_url_raises_200(self):
        self.fail()
        
    @expectedFailure
    def test_blog_permalink_displays_proper_entry(self):
        self.fail()
        
class QuestionMakingTest(WHATTestCase):
    
    def test_new_question_with_boolean_answer(self):
        question = Question.objects.create(name='what have i just named this question', answer_type=0)
        self.assertTrue(question)
        return question
    
    def test_that_q_and_a_can_contain_boolean_question(self):
        q_and_a = QandA.objects.create(name='the name for the question form')
        question = self.test_new_question_with_boolean_answer() #Get a question object by running the test above.
        QuestionOnForm.objects.create(question=question, form=q_and_a, required=True) #Through model - puts our question on the q_and_a.
        self.assertEqual(q_and_a.questions.count(), 1) #That in fact, the question is on our q_and_a
        return q_and_a, question
                         
    def test_boolean_answer(self):
        user = test_user_factory(1)[0]
        q_and_a, question = self.test_that_q_and_a_can_contain_boolean_question() #Grab a q_and_a and a question from the test above.
        answer = BooleanAnswer.objects.create(creator=user, question=question, application=q_and_a, answer=False)
        self.assertFalse(q_and_a.answers.all()[0].answer())
        
        
    @expectedFailure
    def test_new_question_with_text_answer(self):
        self.fail()
    
    @expectedFailure    
    def test_template_has_question_name(self):
        self.client.get('/cms/form/')
        
        self.fail()
        