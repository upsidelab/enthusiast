from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from .models import DataSet, Product, Document
from .serializers import DataSetSerializer, DocumentSerializer, ProductSerializer


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


def embedding_view(request):
    if request.method == 'POST':
        data_set = DataSet.objects.all()
        for ds in data_set:
            ds.reload_all_embeddings()

    return render(request, 'ecl/embedding.html')
