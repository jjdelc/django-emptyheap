# -*- coding: utf 8 -*-

from django import forms

from emptyheap.models import Question, Answer, BaseVote

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('title', 'body', 'tags')

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
    direction = forms.CharField()

    def clean_direction(self):
        value = self.cleaned_data['direction']
        try:
            return ['down', 'up'].index(value.lower())
        except ValueError:
            raise forms.ValidationError(strings.INVALID_VOTE)


    def process_vote(self, object, user, vote_model):
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
        except vote_model.DoesNotExist:
            # The user hasn't voted, then create the vote
            vote = object.votes.create(
                direction=direction,
                user=user
            )

        return vote
            
