from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .models import Companies, RawDataSets, Contents
from .serializers import CompanySerializer, RawDataSetSerializer, ContentSerializer


def index(request):
    return HttpResponse("Hello, world. You're at The E-Cell welcome page.")


def user_detail(request):
    return JsonResponse({"status": "ok"})


def data_set_list(request):
    companies = Companies.objects.all()
    serializer = CompanySerializer(companies, many=True)
    return JsonResponse(serializer.data, safe=False)


def product_list(request, data_set_id):
    products = RawDataSets.objects.filter(company_code=data_set_id)
    serializer = RawDataSetSerializer(products, many=True)
    return JsonResponse(serializer.data, safe=False)


def content_list(request, data_set_id):
    contents = Contents.objects.filter(company_code=data_set_id)
    serializer = ContentSerializer(contents, many=True)
    return JsonResponse(serializer.data, safe=False)
