# -*- coding: utf-8 -*-

from django import template
from emptyheap.models import Vote

register = template.Library()

@register.filter
def has_downvote(object, user):
    return object.votes.filter(user=user, direction=Vote.DOWN).count() > 0

@register.filter
def has_upvote(object, user):
    return object.votes.filter(user=user, direction=Vote.UP).count() > 0

