from celery import shared_task
from agent.services import ConversationManager


@shared_task()
def answer_question_task(conversation_id,
                         data_set_id,
                         embedding_model_name,
                         embedding_dimensions_value,
                         user_id,
                         system_name,
                         question_message):
    manager = ConversationManager()
    answer = manager.answer_question(conversation_id,
                                     data_set_id,
                                     embedding_model_name,
                                     embedding_dimensions_value,
                                     user_id,
                                     system_name,
                                     question_message)

    return {'conversation_id': conversation_id,
            'message_id': answer.id}
