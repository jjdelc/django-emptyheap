# -*- coding: utf 8 -*-

from django.http import HttpResponseRedirect
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required

from emptyheap.models import Entry

def index(request):
    """
    The index view will display top questions
    """
    return object_list(request, Entry.objects.questions('-votes_result'))

def questions(request):
    """
    Returns recent questions
    """
    return object_list(request, Entry.objects.questions())

def unanswered(request):
    """
    returns unanswered questions
    """
    return object_list(request, Entry.objects.unanswered())

def question_detail(request, question_id):
    """
    Displays a question's detail, comments and such
    """
    return direct_to_template(request, '')

def tags(request):
    """
    Displays all question tags
    """
    return object_list(request, Tag)

@login_required
def ask(request):
    """
    On GET:
        Displays the new question form
    on POST:
        Validate and add the new question, then show question's detail
    """
    return direct_to_template(request, '')
