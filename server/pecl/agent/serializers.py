from rest_framework import serializers

from agent.models import Conversation, Message
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


class MessageFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['rating', 'feedback']
        extra_kwargs = {
            'rating': {'required': True},
        }


class MessagesSerializer(serializers.ModelSerializer):
    # Serializer to get list of messages exchanged during a given conversation.
    class Meta:
        model = Message
        fields = ['id', 'text', 'role']

class ConversationContentSerializer(ConversationSerializer):
    # This serializer returns conversation details extended with history.
    history = MessagesSerializer(many=True)

    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['history']
