# -*- coding: utf 8 -*-

from django.http import HttpResponseRedirect, HttpResponseNotAllowed, \
   HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from tagging.models import Tag, TaggedItem

from emptyheap.models import Question, Answer, Vote
from emptyheap.forms import QuestionForm, AnswerForm, VoteForm
from emptyheap import constants, strings

def question_detail(request, question_id):
    """
    Displays a question's detail, comments and such
    on post, will store a new answer
    """
    question = get_object_or_404(Question, pk=question_id)

    ordering_posibilities = {
        'oldest': 'added_on',
        'newest': '-added_on'
    }

    ordering = '-votes_result'
    if 'order_by' in request.REQUEST:
        order_by = request.REQUEST['order_by']
        if order_by in ordering_posibilities.keys():
            ordering = ordering_posibilities['order_by']

    form = AnswerForm()
    if request.method == 'POST':
        user = request.user
        if user.is_authenticated():  
            form = AnswerForm(request.POST)
            if form.is_valid():
                answer = form.save(question, user)
                question.save() # updates answer count
                user.message_set.create(message=strings.ANSWER_SAVED)
                return HttpResponseRedirect(question.get_absolute_url())
        else:
            # User is not authenticated but somehow submitted a POST request
            return HttpResponseNotAllowed(['GET'])

    return object_list(request, question.answers.order_by(ordering),
        template_name='emptyheap/question_detail.html', 
        extra_context={
        'object': question,
        'form': form,
    })


@login_required
def ask(request):
    """
    On GET:
        Displays the new question form
    on POST:
        Validate and add the new question, then show question's detail
    """
    form = QuestionForm()
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(request.user)
            request.user.message_set.create(message=strings.QUESTION_CREATED)
            return HttpResponseRedirect(question.get_absolute_url())

    return direct_to_template(request, 'emptyheap/ask.html', {
        'form': form
    })


def tag_detail(request, tag_name):
    """
    Displays all the questions tagged something
    """
    tag = get_object_or_404(Tag, name=tag_name)
    return object_list(request, TaggedItem.objects.get_by_model(Question, tag))


class ObjectVoteView(object):
    """
    Returns a view to vote on an object specified by object_model
    Object model should inherit from BaseVotedModel

    When configuring the URL for these views, the named groups should be
    named as the the lookup param used on the ORM

    """
    vote_model = Vote
    app_name = 'emptyheap'

    def __init__(self, object_model):
        """
        Sets which object will be voted on
        """
        self.object_model = object_model

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        return patterns('',
            url('^up/$', self.view, 
                {'direction': self.vote_model.UP}, 
                name='%s_upvote' % self.object_model.__name__.lower()),

            url('^down/$', self.view, 
                {'direction': self.vote_model.DOWN}, 
                name='%s_downvote' % self.object_model.__name__.lower())
        )

    def urls(self):
        return self.get_urls(), self.app_name, None

    urls = property(urls)

    def get_object(self, **kwargs):
        """
        This method should return the instance based on the values
        recieved from the urlconf

        by default it will lookup the named parameters as the 
        filter lookup params
        """
        return get_object_or_404(self.object_model, **kwargs)

    @login_required
    def view(self, request, direction, **kwargs):
        """
        This endpoint should be reached via POST to vote on a specific answer
        There is only one vote allowed per user/answer
        if the user hasn't voted on the anwer yet, then set it. If the user has
        alerady voted on the answer, either remove the vote if it has the same
        value, otherwise change the vote's value
        """
        object = self.get_object(**kwargs)

        form = VoteForm({ 'direction': direction })
        if form.is_valid():
            vote = form.process_vote(object, request.user)
            object.save() # do this to update counts
            request.user.message_set.create(message=strings.VOTE_CASTED)
        else:
            return HttpResponseBadRequest()

        return HttpResponseRedirect(object.get_absolute_url())


class ObjectCommentView(ObjectVoteView):
    """
    This view allows for an object to be commented
    It inherits from ObjectvoteView because it uses the same __init__ and get_object
    methods
    """

    @login_required
    def __call__(self, request, **kwargs):
        """
        This is the endpoint where to post the comment
        If the form doesn't validate will display the object and the 
        invalid form to be corrected
        """
        object = self.get_object

        form = CommentForm(form.REQUEST)
        if form.is_valid():
            comment = form.save(object, request.user)
            return HttpResponseRedirect(object.get_absolute_url())
        
        return direct_to_template(request, 'emptyheap/comment_form.html', {
            'object': object,
            'form': form,
        })
            

        object = self.get_object(**kwargs)
