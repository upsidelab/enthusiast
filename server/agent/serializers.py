from rest_framework import serializers

from agent.models import Conversation, Message


class AskQuestionSerializer(serializers.Serializer):
    """A serializer to ask questions.

    Arguments:
        data_set_id:
            Integer, Provide an ID of a data set to be used
        system_name:
            Str, Name of a system user that is answering questions to be displayed on the Conversation page.
            You may skip this attribute.
        question_message:
            Str, A question message.
    """
    data_set_id = serializers.IntegerField(
        required=False,
        allow_null=False,
        error_messages={
            'null': 'Data Set ID cannot be blank'
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


class ConversationCreationSerializer(serializers.Serializer):
    data_set_id = serializers.IntegerField(
        required=False,
        allow_null=False,
        error_messages={
            'null': 'Data Set ID cannot be blank. Either skip this parameter, or provide a valid ID of a data set'
        }
    )


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
