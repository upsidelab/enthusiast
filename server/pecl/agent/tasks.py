from celery import shared_task
from agent.services import ConversationManager

@shared_task()
def answer_question_task(conversation_id,
                         embedding_model_name,
                         embedding_dimensions_value,
                         user_name,
                         system_name,
                         question_message):
    manager = ConversationManager()
    question = manager.answer_question(conversation_id,
                               embedding_model_name,
                               embedding_dimensions_value,
                               user_name,
                               system_name,
                               question_message)

    return {'conversation_id': question.conversation.id,
            'query_message': question.question,
            'answer': question.answer}
