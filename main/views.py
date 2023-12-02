from django.shortcuts import render
from django.http import JsonResponse
from .dialogflow import Intent

# Create your views here.
def index(request):
    return render(request, 'main/index.html')

def chat(request):
    if request.method == "POST":
        params = request.POST
        # data = params['message']

        intent = Intent('private_key.json')
        data = intent.input(params['message'])
        print(data)
        return JsonResponse({"message": data} , safe=False)