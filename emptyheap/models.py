# -*- coding: utf 8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify

from markdown import markdown
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
        abstract = True

class BaseVotedModel(models.Model):
    """
    Inherit from this model so your model can be voted up and down
    """
    up_votes = models.PositiveIntegerField(strings.UP_VOTE, default=0)
    down_votes = models.PositiveIntegerField(strings.DOWN_VOTE, default=0)
    votes_result = models.IntegerField(strings.VOTE_RESULT, default=0)
    votes = generic.GenericRelation('Vote')

    class Meta:
        abstract = True

    def total_votes(self):
        return self.up_votes + self.down_votes

    def update_votes(self, commit=True):
        """
        Updates votes counts
        if commit is set to True will save the questions
        """
        self.up_votes = self.votes.up().count()
        self.down_votes = self.votes.down().count()
        self.votes_result = self.up_votes - self.down_votes

        if commit:
            super(self.__class__, self).save(*args, **kwargs)


class Reputation(models.Model):
    """
    Represents an extension of auth's user in order to store other
    properties
    """
    user = models.OneToOneField(User)
    total_votes = models.PositiveIntegerField(default=0)


class Category(models.Model):
    """ Represnts a category of questions, like a subforum """


class QuestionManager(models.Manager):
    def get_top_questions(self):
        """
        Fetches all the parent entrys
        """
        return self.all().order_by('-votes_result')

    def unanswered(self, order_by='-added_on'):
        """
        returns unanswered questions, 0 answers
        """
        return self.filter(answers_count=0).order_by(order_by)


class Question(BaseModel, BaseVotedModel):
    """
    Represents a question 
    """
    BEST_ANSWER = 0
    CONVERSATION = 1
    TYPES = (
        (BEST_ANSWER, strings.BEST_ANSWER),
        (CONVERSATION, strings.CONVERSATION)
    )
    
    type = models.PositiveSmallIntegerField(choices=TYPES, default=BEST_ANSWER)

    title = models.CharField(strings.QUESTION, max_length=128)
    body = models.TextField(strings.BODY)
    body_html = models.TextField()

    selected_response = models.ForeignKey('Answer', null=True, 
        related_name='is_selected_respnse_for')
    answers_count = models.PositiveIntegerField(strings.ANSWER_COUNT, default=0)

    favorite_by = models.ManyToManyField(User, related_name='favorite_questions')
    tags = TagField()

    objects = QuestionManager()

    is_conversation = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_base_url(self):
        return ('eh_question_detail', (), {
            'question_id': self.id
        })

    def get_absolute_url(self):
        return '%s%s/' % (self.get_base_url(), slugify(self.title))

    def update_answer_count(self, commit=False):
        """
        Updates the number of answers
        if commit is set to True will save the Question
        """
        self.answers_count = self.answers.count()

        if commit:
            super(Question, self).save(*args, **kwargs)
        
    def save(self, *args, **kwargs):
        """
        Save Marked up version of the question
        Also update answer count and votes
        """
        if not self.id:
            super(Question, self).save(*args, **kwargs)

        self.body_html = markdown(self.body)
        self.update_votes(commit=False)
        self.update_answer_count(commit=False)
        super(Question, self).save(*args, **kwargs)


class Answer(BaseModel, BaseVotedModel):
    """
    Represents an answer to a question
    """
    question = models.ForeignKey(Question, related_name='answers')
    body = models.TextField(strings.BODY)
    body_html = models.TextField()

    def __unicode__(self):
        return 'Answer to question "%s" by %s' % (self.question, self.user)

    def get_absolute_url(self):
        return '%s#answer-%s' % (self.question.get_absolute_url(), self.id)

    def save(self, *args, **kwargs):
        self.body_html = markdown(self.body)
        self.update_votes(commit=False)
        super(Answer, self).save(*args, **kwargs)


class Comment(BaseModel):
    """
    Represents a comment made on a entry by a user
    """
    body = models.TextField()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey()


class VoteManager(models.Manager):
    def up(self):
        """ Return up votes """
        return self.filter(direction=self.model.UP)

    def down(self):
        """ Return up votes """
        return self.filter(direction=self.model.DOWN)


class Vote(BaseModel):
    """
    Represents an up or downvote made on a entry by a user
    There can only be one vote per user/question
    """
    UP = True
    DOWN = False
    DIRECTIONS = (
        (UP, strings.UP_VOTE),
        (DOWN, strings.DOWN_VOTE),
    )
    direction = models.BooleanField(choices=DIRECTIONS)
    objects = VoteManager()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey()


