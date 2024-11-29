from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework import status

from unittest.mock import patch

from account.models import CustomUser
from agent.models import EmbeddingModel, EmbeddingDimension
from ecl.models import DataSet


class GetAnswerAPITestCase(APITestCase):
    def configureUser(self):
        self.test_user = CustomUser.objects.create_user(email='dale.cooper@example.com',
                                              password='OwlsAreNotWhatTheySeem',
                                              first_name='Dale',
                                              last_name='Cooper')
        self.api_token = Token.objects.create(user=self.test_user)

    def setUp(self):
        self.configureUser()
        self.data_set = DataSet(name='The Owner')
        self.data_set.save()
        self.model = EmbeddingModel(name='text-embedding-3-small')
        self.model.save()
        self.dimensions = EmbeddingDimension(dimension=3)
        self.dimensions.save()

    @patch('agent.core.Agent.process_user_request')  # Mock the agent
    def test_ask_api_with_question_only(self, mock_agent):
        """This test verifies api when only question is asked, there is no conversation id attribute provided.
        In this case engine should create a new conversation and answer the question
        """

        mock_agent.return_value = {"output": "This is a very smart answer"}

        # Define the URL endpoint
        url = '/api/ask/'
        question_message = 'What is the best product in your portfolio?'

        # Define the input payload (this will crete a new conversation)
        data = {
            'question_message': question_message
        }

        # Send a POST request to the API
        response = self.client.post(url, data, format='json', headers={'Authorization': f'Token {self.api_token}'})

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response contains the correct structure and data
        self.assertEqual(response.data['query_message'], question_message)
        self.assertTrue('answer' in response.data)
