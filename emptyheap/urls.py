# -*- coding: utf 8 -*-
from django.conf.urls.defaults import url, patterns

from emptyheap import views

urlpatterns = patterns('',
    url(r'^/$',
        views.index,
        name='eh_index'),

    url(r'^questions/$',
        views.questions,
        name='eh_questions'),

    url(r'^tags/$',
        views.tags,
        name='eh_tags'),

    url(r'^unanswered/$',
        views.unanswered,
        name='eh_unanswered'),

    url(r'^categories/$',
        views.categories,
        name='eh_categories'),

    url(r'^categories/(P<category_slug>[-\w]+)/$',
        views.category_detail,
        name='eh_category_detail'),

    url(r'^ask/$',
        views.ask,
        name='eh_ask'),

    url(r'^questions/(?P<question_id>\d+)/',
        views.question_detail,
        name='eh_question_detail'),
)
