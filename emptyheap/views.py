# -*- coding: utf 8 -*-

from django.http import HttpResponseRedirect, HttpResponseNotAllowed, \
   HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from tagging.models import Tag, TaggedItem

from emptyheap.models import Question, Answer, QuestionVote, AnswerVote
from emptyheap.forms import QuestionForm, AnswerForm, VoteForm
from emptyheap import constants, strings

def question_detail(request, question_id):
    """
    Displays a question's detail, comments and such
    """
    question = get_object_or_404(Question, pk=question_id)

    ordering = '-votes_result'
    if 'order_by' in request.REQUEST:
        order_by = request.REQUEST['order_by']
        if order_by in ('date'):
            ordering = 'added_on'

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


@login_required
@require_http_methods(['POST'])
def answer_vote(request, question_id, answer_id):
    """
    This endpoint should be reached via POST to vote on a specific answer
    There is only one vote allowed per user/answer
    if the user hasn't voted on the anwer yet, then set it. If the user has
    alerady voted on the answer, either remove the vote if it has the same
    value, otherwise change the vote's value
    """
    answer = get_object_or_404(Answer, question__id=question_id, id=answer_id)
    if not 'direction' in request.POST:
        return HttpResponseBadRequest()

    form = VoteForm(request.POST)
    if form.is_valid():
        vote = form.process_vote(answer, request.user, AnswerVote)
        answer.save() # do this to update counts
        request.user.message_set.create(message=strings.VOTE_CASTED)
    else:
        return HttpResponseBadRequest()

    return HttpResponseRedirect(answer.question.get_absolute_url())


