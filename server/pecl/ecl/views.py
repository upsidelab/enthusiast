from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import DataSet, Product, Document
from .serializers import DataSetSerializer, DocumentSerializer, ProductSerializer


def index(request):
    return HttpResponse("Hello, world. You're at The E-Cell welcome page.")


class DataSetListView(ListAPIView):
    queryset = DataSet.objects.all()
    serializer_class = DataSetSerializer
    permission_classes = [IsAuthenticated]


class ProductListView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(company_code=self.kwargs['data_set_id'])


class DocumentListView(ListAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(data_set_id=self.kwargs['data_set_id'])


def embedding_view(request):
    if request.method == 'POST':
        data_set = DataSet.objects.all()
        for ds in data_set:
            ds.reload_all_embeddings()

    return render(request, 'ecl/embedding.html')
