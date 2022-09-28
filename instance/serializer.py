from instance.models import *
import knowledgebase.models as knowledgebase
from rest_framework import serializers


class QuestionSubSectionSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = QuestionSubSection
        fields = ('id', 'section', 'name', 'business')


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'text', 'is_active', 'subsection', 'ordinal')


class QuestionsAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswerChoice
        fields = ('id', 'text', 'question', 'ordinal')


class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = ('id', 'name')


class QuestionConfigSerializer(serializers.ModelSerializer):
    question_type = QuestionTypeSerializer(read_only=True)

    class Meta:
        model = QuestionConfig
        fields = ('id', 'question', 'question_type', 'required', 'depends_on_question', 'show_when_the_answer_is')