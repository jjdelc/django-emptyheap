# -*- coding: utf 8 -*-

from django import forms

from emptyheap.models import Question, Answer, Vote
from emptyheap import strings

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('title', 'body', 'tags', 'is_conversation')

    def save(self, user):
        self.instance.user = user
        return super(QuestionForm, self).save()


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('body',)

    def save(self, question, user):
        self.instance.question = question
        self.instance.user = user
        return super(AnswerForm, self).save()


class VoteForm(forms.Form):
    direction = forms.BooleanField(required=False)

    def process_vote(self, object, user):
        """
        Will process the vote on the object
        """
        direction = self.cleaned_data['direction']
        try:
            # Check if the user has already voted
            vote = object.votes.get(user=user)
            if vote.direction == direction:
                vote.delete()
            else:
                vote.direction = direction
                vote.save()
        except Vote.DoesNotExist:
            # The user hasn't voted, then create the vote
            vote = object.votes.create(
                direction=direction,
                user=user,
                object=object
            )

        return vote
            
class CommentForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea())

    def save(self, object, user):
        """
        Adds a new comment associated to the object
        """
        body = self.cleaned_data['body']

        comment = Comment.objects.create(
            object=object,
            user=user,
        )
        return comment


