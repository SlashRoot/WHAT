from django.db import models
from taggit.managers import TaggableManager
from taggit.models import Tag
from django.template.defaultfilters import slugify

class Page(models.Model):
    created = models.DateField(auto_now_add=True)
    creator = models.ForeignKey('auth.User')
    title = models.CharField(max_length=200)    
    published = models.BooleanField()
    
    tags = TaggableManager()
    
    def __unicode__(self):
        return self.title;

class ContentBlock(models.Model):
    headline = models.CharField(max_length=200, blank=True, null=True)
    subhead = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    created = models.DateField(auto_now_add=True)
    creator = models.ForeignKey('auth.User')
    published = models.BooleanField()
    
    tags = TaggableManager(blank=True)
    
    def __unicode__(self):
        return self.headline
    
    def get_absolute_url(self):
        if Tag.objects.get(name="blog") in self.tags.all() and Tag.objects.get(name="public") in self.tags.all():  
            return '/blog/%s/' % self.slug
        
    def save(self, *args, **kwargs):
        if not self.slug:
            if self.headline:
                slug = slugify(self.headline)
            elif self.subhead:
                slug = slugify(self.subhead)
            else:
                slug = slugify(self.content)            
            self.slug = slug[:50]        
        super(ContentBlock, self).save(*args, **kwargs)
    
class QandA(models.Model):
    '''
    A series of questions.
    '''    
    name = models.CharField(max_length=50)
    questions = models.ManyToManyField('cms.Question', through='cms.QuestionOnForm')
    
    class Meta:
        verbose_name = "Question-and-Answer Form"
        verbose_name_plural = "Question-and-Answer Forms"
    
    
    def __unicode__(self):
        return u'%s' % (self.name)
    
    def get_absolute_url(self):
        return "/cms/q_and_a/%s" % (self.id) 
    

ANSWER_TYPES = (
                (0, 'Boolean'),
                (1, 'Text'),
                (2, 'Choices'), #Not implemented yet.
                (3, 'Relationship'), #Ditto.
                )

class Question(models.Model):
    name = models.CharField(max_length=80, unique=True)
    answer_type = models.IntegerField(choices=ANSWER_TYPES)
    
    def __unicode__(self):
        return self.name


class QuestionOnForm(models.Model):
    '''
    The presence of a particular Question in a particular QandA
    '''
    form = models.ForeignKey('cms.QandA')
    question = models.ForeignKey('cms.Question')
    required = models.BooleanField()
    
    def __unicode__(self):
        return "%s <=- %s" % (self.form.name, self.question.name) 
    
class Answer(models.Model):
    '''
    parent class for various types of answers.
    '''
    creator = models.ForeignKey('auth.User')
    created = models.DateTimeField(auto_now_add = True)
    application = models.ForeignKey('cms.QandA', related_name='answers')
    question = models.ForeignKey('cms.Question', related_name='answers')
    
    def __unicode__(self):
        return "%s to %s on %s" % (self.creator, self.question.name, self.application.name)
    
    def answer(self):
        try:
            return self.textanswer.answer
        except TextAnswer.DoesNotExist:
            pass
        
        try:
            return self.booleananswer.answer
        except BooleanAnswer.DoesNot.Exist:
            pass
        
class BooleanAnswer(Answer):
    answer = models.BooleanField()

class TextAnswer(Answer):
    answer = models.TextField()
    
#TODO: Implement choice and relationship answer classes