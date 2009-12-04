# -*- coding: utf 8 -*-

from django.db import models
from django.contrib.auth.models import User

from tagging.fields import TagField

from emptyheap import strings, constants

class BaseModel(models.Model):
    """
    Abstract class with some base attributes
    """
    user = models.ForeignKey(User)
    added_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-added_on',)

class HeapProfile(models.Model):
    """
    Represents an extension of auth's user in order to store other
    properties
    """
    user = models.OneToOneField(User)
    total_votes = models.PositiveIntegerField(default=0)


class Message(BaseModel):
    """
    Represents a question or answer
    A question does not have a parent message, an answer does
    """
    message = models.ForeignKey(Message, null=True)
    title = models.CharField(strings.MESSAGE, max_length=128)
    body = models.TextField(strings.BODY)
    body_html = models.TextField()
    up_votes = models.PositiveIntegerField(strings.UP_VOTE, default=0)
    down_votes = models.PositiveIntegerField(strings.DOWN_VOTE, default=0)
    selecter_response = models.BooleanField(default=False)
    tags = TagField()

class Comment(BaseModel):
    """
    Represents a comment made on a message by a user
    """
    message = models.ForeignKey(Message)
    body = models.TextField()
    is_awesome = models.BooleanField(default=False)

class Vote(BaseModel):
    """
    Represents an up or downvote made on a message by a user
    There can only be one vote per user/message
    """
    UP = 1
    DOWN = -1
    DIRECTIONS = (
        (UP, strings.UP_VOTE),
        (DOWN, strings.DOWN_VOTE),
    )
    message = models.ForeignKey(Message)
    direction = models.SmallIntegerField(choices=DIRECTIONS)

