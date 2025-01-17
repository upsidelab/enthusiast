from celery import shared_task
from agent.services import ConversationManager


@shared_task(bind=True, max_retries=3)
def answer_question_task(self,
                         conversation_id,
                         data_set_id,
                         user_id,
                         question_message):
    manager = ConversationManager()
    try:
        answer = manager.answer_question(conversation_id,
                                         data_set_id,
                                         user_id,
                                         question_message)

        return {'conversation_id': conversation_id,
                'message_id': answer.id}
    except Exception as e:
        manager.record_error(conversation_id, user_id, data_set_id, e)
        self.retry(countdown=1)
