from rest_framework import serializers

from agent.models import Conversation, Question
from ecl.models import EmbeddingModel, EmbeddingDimension


class AskQuestionSerializer(serializers.Serializer):
    """A serializer to ask questions.

    Arguments:
        conversation_id:
            Integer, To continue an existing conversation provide ID, if you skip this attribute,
            we will create a new conversation.
        embedding_model_name:
            Str, You may provide a desired model name for a new conversation, if you skip this param we will use
            default model.
        embedding_dimensions:
            Integer, You may provide a desired embedding vector length for a new conversation, if you skip this
            attribute, we will use default embedding vector length.
        system_name:
            Str, Name of a system user that is answering questions to be displayed on the Conversation page.
            You may skip this attribute.
        question_message:
            Str, A question message.
    """
    conversation_id = serializers.IntegerField(
        required=False,
        allow_null=False,
        error_messages={
            'null': 'Conversation ID cannot be blank. Either skip this parameter (a new conversation will be created), or provide a valid ID of an existing conversation'
        }
    )
    embedding_model_name = serializers.CharField(
        required=False,
        allow_blank=False,
        error_messages={
            'blank': 'Embedding model name cannot be blank.'
        }
    )
    embedding_dimensions = serializers.IntegerField(
        required=False,
        allow_null=False,
        error_messages={
            'null': 'Embedding dimensions value cannot be blank. Either skip this parameter (a default dimension will be used), or provide a valid number greater that zero'
        }
    )

    system_name = serializers.CharField(
        required=False,
        default='APISystem',
        allow_blank=False,
        error_messages={
            'blank': 'System name cannot be blank. Provide valid user name or skip this param (default value will be used)'
        }
    )
    question_message = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'blank': 'Query message cannot be blank.'
        }
    )

    def validate_conversation_id(self, value):
        if not Conversation.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'Conversation with the given ID ({value}) does not exist. Either skip this parameter (a new conversation will be created), or provide a valid ID of an existing conversation')
        return value

    def validate_embedding_model_name(self, value):
        if not EmbeddingModel.objects.filter(name=value).exists():
            raise serializers.ValidationError(f'Embedding model ({value}) does not exist. Either skip this parameter (default model will be used), or provide a valid name')
        return value

    def validate_embedding_dimensions(self, value):
        if not EmbeddingDimension.objects.filter(dimension=value).exists():
            raise serializers.ValidationError(f'Embeddings with provided dimensions {value} are not collected. Either skip this parameter (default value will be used), or provide a valid one')
        if value <=0:
            raise serializers.ValidationError(f'Provided embedding dimension value ({value}) is not correct. Value of embedding dimension has to be an Integer greater than zero.')
        return value


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'started_at']


class MessagesSerializer(serializers.ModelSerializer):
    """Serializer to get list of messages exchanged during a given conversation.

        Arguments:
        conversation_id:
            Integer, obligatory, provide this argument to get messages exchanged during one conversation provide.
        min_message_id:
            Integer, to get messages starting at a given point of a conversation.
    """
    class Meta:
        model = Question
        fields = ['id', 'question', 'answer']

    def to_representation(self, instance):
        # A Question contains two messages: question itself followed by an answer.
        return [
            {'id': instance.id, 'role': 'user', 'text': instance.question},
            {'id': instance.id, 'role': 'agent', 'text': instance.answer}
        ]

class ConversationContentSerializer(ConversationSerializer):
    # This serializer returns conversation extended with history.
    history = MessagesSerializer(many=True)

    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['history']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        flattened_history = []
        for message in data.get('history', []):
            flattened_history.extend(message)

        data['history'] = flattened_history

        return data
