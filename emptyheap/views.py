# -*- coding: utf 8 -*-

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required

from tagging.models import Tag, TaggedItem

from emptyheap.models import Question, Answer
from emptyheap.forms import QuestionForm, AnswerForm
from emptyheap import constants, strings

def question_detail(request, question_id):
    """
    Displays a question's detail, comments and such
    """
    question = get_object_or_404(Question, pk=question_id)

    form = AnswerForm()
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(question, request.user)
            request.user.message_set.create(message=strings.ANSWER_SAVED)
            return HttpResponseRedirect(question.get_absolute_url())

    return direct_to_template(request, 'emptyheap/question_detail.html', {
        'object': question,
        'answers': question.answers.all(),
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
