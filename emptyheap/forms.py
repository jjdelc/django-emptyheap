# -*- coding: utf 8 -*-

from django import forms

from emptyheap.models import Question, Answer

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

