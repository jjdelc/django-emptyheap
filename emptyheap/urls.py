# -*- coding: utf 8 -*-
from django.conf.urls.defaults import url, patterns
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template

from tagging.models import Tag

from emptyheap import views
from emptyheap.models import Question

urlpatterns = patterns('',
    url(r'^$',
        object_list,
        {'queryset': Question.objects.get_top_questions()},
        name='eh_index'),

    url(r'^questions/$',
        object_list,
        {'queryset': Question.objects.all()},
        name='eh_questions'),

    url(r'^tags/$',
        direct_to_template, {
        'template': 'emptyheap/tag_list.html',
        'extra_context': {'tags': Tag.objects.cloud_for_model(Question, steps=5)}},
        name='eh_tags'),

    url(r'^tags/(?P<tag_name>[-\w]+)/$',
        views.tag_detail,
        name='eh_tag_detail'),

    url(r'^unanswered/$',
        object_list,
        {'queryset': Question.objects.unanswered()},
        name='eh_unanswered'),

    url(r'^ask/$',
        views.ask,
        name='eh_ask'),

    url(r'^questions/(?P<question_id>\d+)/',
        views.question_detail,
        name='eh_question_detail'),
)
