from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

from cms.models import QandA, Answer, Page, ContentBlock
from cms.forms import BlogPostForm
from django.contrib.auth.decorators import login_required
from utility.models import FixedObject




AUTO_TASK_CREATOR = FixedObject.objects.get(name="User__auto_task_creator")

@login_required
def edit_content_block(request):
    
    cust = {'auto_resize': True,
        'rows':15,
        'cols':65, 
        }
    
    if request.POST:
        form = BlogPostForm(request.POST)
        if form.is_valid():
            form.instance.creator = request.user
            form.save()
        else:
            form.fields['content'].widget.attrs = cust
            
            
    else:

    
        form = BlogPostForm()
        form.fields['content'].widget.attrs = cust
    
    return render(request, 'forms/utility_form.html', locals())
    

def q_and_a_form(request, q_and_a_id):
    
    if "completed" in request.GET:
        pass
    
    if request.user.is_authenticated():
        applicant = request.user
    else:
        applicant = AUTO_TASK_CREATOR
    
    q_and_a = QandA.objects.get(id=q_and_a_id)
    
    questions = q_and_a.questions.order_by('id')
        
    #TODO: Get this fucking thing using the regular forms API.
    if request.POST:
        
        incomplete = False #A flag to figure out whether the form is complete
        completed_answers = {} #A dict that we'll populate in a bit here.
        
        for question in questions: #We know that the various questions will be named "question_<n>" in request.POST, where n is the id of the question.  Let's start making our own dict of the answers and deal with something being blank.            
            answer_text = request.POST['question_' + str(question.id)]
            if answer_text:
                question.answer_text = answer_text
            else:
                incomplete = True
            
        if incomplete:
            return render(request, 'main/q_and_a.html', locals())
        else: #The form is not incomplete; let's save everything.
            for question in questions:
                Answer.objects.create(application = q_and_a, question = question, answer = question.answer_text, creator=applicant)
            return render(request, 'cms/q_and_a_thankyou.html', locals())
        
    return render(request, 'main/q_and_a.html', locals())

def blog(request, headline_slug=None):
    
    if headline_slug:  # If we have a headline slug, we know that we're looking for an individual blog post.
        blog_post = get_object_or_404(ContentBlock, slug=headline_slug)
        return render(request, 'cms/blog/blog_single_post.html', locals())
    else:  # If we don't have a headline slug, we're just headed to the front page of the bloody blog.
        blog_blocks = ContentBlock.objects.filter(published=True, tags__name__in=["public","blog"]).order_by('-created').distinct()    
        return render(request,'cms/blog/blog_front_page.html', locals())