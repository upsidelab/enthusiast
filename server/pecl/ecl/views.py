from datetime import datetime

from django.db.models import Model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from .models import DataSet, Product, Document, Conversation, Question, EmbeddingModel, EmbeddingDimension
from .serializers import DataSetSerializer, ProductSerializer, DocumentSerializer


def index(request):
    return HttpResponse("Hello, world. You're at The E-Cell welcome page.")


def user_detail(request):
    return JsonResponse({"status": "ok"})


def data_set_list(request):
    data_set = DataSet.objects.all()
    serializer = DataSetSerializer(data_set, many=True)
    return JsonResponse(serializer.data, safe=False)


def product_list(request, data_set_id):
    products = Product.objects.filter(company_code=data_set_id)
    serializer = ProductSerializer(products, many=True)
    return JsonResponse(serializer.data, safe=False)


def document_list(request, data_set_id):
    document = Document.objects.filter(company_id=data_set_id)
    serializer = DocumentSerializer(document, many=True)
    return JsonResponse(serializer.data, safe=False)


def conversation_view(request, conversation_id=None, embedding_model=None):
    # Populate context.
    available_models = []
    for m in EmbeddingModel.objects.all():
        available_models.append(m)
    available_dimensions = []
    for d in EmbeddingDimension.objects.all():
        available_dimensions.append(d)

    # Initialize a conversation.
    if conversation_id:
        conversation = Conversation.objects.get(id=conversation_id)
    else:
        # Get params for a new conversations
        embedding_dimensions = embedding_model = None
        if request.method == 'POST':
            selected_model_id = request.POST.get('selected_model')
            if selected_model_id:
                embedding_model = EmbeddingModel.objects.get(id=selected_model_id)
            selected_dimensions_id = request.POST.get('selected_dimensions')
            if selected_dimensions_id:
                embedding_dimensions =  EmbeddingDimension.objects.get(id=selected_dimensions_id).dimension

        # Load default model and dimensions if not defined in params.
        if not embedding_model:
            embedding_model = EmbeddingModel.objects.first()
        if not embedding_dimensions:
            embedding_dimensions = EmbeddingDimension.objects.first().dimension

        # Start a new conversation.
        conversation = Conversation(started_at=datetime.now(),
                                    model=embedding_model,
                                    dimensions=embedding_dimensions,
                                    user_name="User",
                                    system_name="System")
        conversation.save()
        return redirect('conversation', conversation_id=conversation.id)

    conversation_history = conversation.get_history()

    if request.method == 'POST':
        user_message = request.POST.get('user_message')
        question = Question(conversation=conversation,
                            asked_at=datetime.now(),
                            question=user_message)
        question.save()  # Save it now to allow adding child entities (connected by foreign key).
        question.get_answer()
        question.save()

        # Extend history with current question-answer pair.
        conversation_history += question.get_qa_str()

        return redirect('conversation', conversation_id=conversation.id)

    context = {
        'conversation_id': conversation.id,
        'embedding_model': conversation.model.name,
        'embedding_dimensions': conversation.dimensions,
        'user_name': conversation.user_name,
        'system_name': conversation.system_name,
        'started_at': conversation.started_at,
        'available_models': available_models,
        'available_dimensions': available_dimensions,
        'conversation_history': conversation_history,
    }
    return render(request, 'ecl/conversation.html', context)

def embedding_view(request):
    if request.method == 'POST':
        data_set = DataSet.objects.all()
        for ds in data_set:
            ds.reload_all_embeddings()

    return render(request, 'ecl/embedding.html')