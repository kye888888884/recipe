from django.shortcuts import render
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from .dialogflow import Dialogflow
from .models import Recipe, Ingredient, Food
from .gpt import GPT
from .apps import MainConfig
import base64
from ultralytics.engine.results import Results
import random
import os

intents = {
    "welcome": "Default Welcome Intent",
    "fallback": "Default Fallback Intent",
    "ingredient": "1_ingredient",
    "main_ingredient": "2_main_ingredient",
    "recommend_positive": "3_recipe_recommendation_positive",
    "recommend_negative": "3_recipe_recommendation_negative",
    "inbun": "4_inbun",
    "recipe_positive": "5_recipe_positive",
    "recipe_negative": "5_recipe_negative",
}

index_to_ingredient = {
    0: 'apple', 1: 'banana', 2: 'beef', 3: 'blueberries', 4: 'broccoli', 5: 'butter', 6: 'carrot', 7: 'cauliflower', 8: 'cheese', 9: 'chicken', 10: 'chocolate', 11: 'corn', 12: 'cream_cheese', 13: 'cucumber', 14: 'dates', 15: 'eggplant', 16: 'eggs', 17: 'ginger', 18: 'grapes', 19: 'green_beans', 20: 'green_bell_pepper', 21: 'green_chillies', 22: 'ground_beef', 23: 'heavy_cream', 24: 'kiwi', 25: 'lemon', 26: 'lettuce', 27: 'lime', 28: 'milk', 29: 'mineral_water', 30: 'mint', 31: 'mushrooms', 32: 'olives', 33: 'onion', 34: 'orange', 35: 'parsley', 36: 'peach', 37: 'peas', 38: 'pickles', 39: 'potato', 40: 'radish', 41: 'red_bell_pepper', 42: 'red_cabbage', 43: 'red_grapes', 44: 'red_onion', 45: 'salami', 46: 'sausage', 47: 'shrimp', 48: 'spinach', 49: 'spring_onion', 50: 'strawberries', 51: 'sweet_potato', 52: 'tangerine', 53: 'tomato', 54: 'tomato_paste', 55: 'yellow_bell_pepper', 56: 'yoghurt', 57: 'zucchini'
}

index_to_ingredient_kor = {
    0: '사과', 1: '바나나', 2: '소고기', 3: '블루베리', 4: '브로콜리', 5: '버터', 6: '당근', 7: '콜리플라워',
    8: '치즈', 9: '닭고기', 10: '초콜릿', 11: '옥수수', 12: '크림치즈', 13: '오이', 14: '대추', 15: '가지', 16: '계란',
    17: '생강', 18: '포도', 19: '콩', 20: '파프리카', 21: '청 고추', 22: '갈은 소고기', 23: '생크림', 24: '키위', 25: '레몬',
    26: '상추', 27: '라임', 28: '우유', 29: '미네랄 워터', 30: '민트', 31: '버섯', 32: '올리브', 33: '양파', 34: '오렌지',
    35: '파슬리', 36: '복숭아', 37: '콩', 38: '피클', 39: '감자', 40: '라디쉬', 41: '빨간파프리카', 42: '적양배추',
    43: '빨간포도', 44: '적양파', 45: '살라미', 46: '소시지', 47: '새우', 48: '시금치', 49: '파', 50: '딸기', 51: '고구마',
    52: '감귤', 53: '토마토', 54: '토마토 페이스트', 55: '노란파프리카', 56: '요거트', 57: '쥬크니'
}

TOP = 10

# my functions
def get_intent_index(intent):
    for key, value in intents.items():
        if value == intent:
            return key
    return "No intent"

def get_recipe_context(recipe_id: int):
    recipe = Recipe.objects.filter(id=recipe_id)[0]
    return recipe.context

def get_ingredients(recipe_id: int):
    ingredients = Ingredient.objects.filter(recipe_id=recipe_id)
    ingredient_names = []
    for ingredient in ingredients:
        food_id = ingredient.food_id
        food = Food.objects.filter(id=food_id)[0]
        ingredient_names.append(food.name)
    return ingredient_names

def get_amounts(recipe_id: int, user_amount=0):
    recipe = Recipe.objects.filter(id=recipe_id)[0]
    amounts = recipe.amounts
    amounts = amounts.replace("'", "")[1:-1].split(",")
    people = int(recipe.people)
    # print("기준:", people, "명")

    # 인분 계산 없을 때
    if user_amount == 0 or people == 0:
        return amounts, False
    
    is_num = False
    # 인분 계산 있을 때
    for i, amount in enumerate(amounts):
        # 숫자 부분과 단위 부분을 분리
        num = ""
        unit = ""
        for j, char in enumerate(amount):
            if char.isdigit():
                num += char
            else:
                unit = amount[j:]
                break
        # 숫자가 없을 때
        if len(num) == 0:
            continue
        # 숫자가 있을 때
        is_num = True
        num = int(num) * user_amount / people
        amounts[i] = str(num) + unit
    return amounts, is_num

def get_recipe_index(recipe: str):
    recipes = Recipe.objects.filter(name=recipe)
    if len(recipes) == 0:
        return -1
    else:
        return recipes[0].id

def get_ingredient_index(ingredient: str):
    food = Food.objects.filter(name=ingredient)
    if len(food) == 0:
        return -1
    else:
        return food[0].id

def search_recipe(ingredients, main=None, top=20):
    # 각 재료의 id를 찾음
    # print(ingredients)

    ingr_indexes = []
    for ingredient in ingredients:
        ingr_index = get_ingredient_index(ingredient)
        if ingr_index != -1:
            ingr_indexes.append(int(ingr_index))
    
    if main is not None:
        main_indexes = []
        for main_ingredient in main:
            main_index = get_ingredient_index(main_ingredient)
            if main_index != -1:
                main_indexes.append(int(main_index))

    # 재료가 없을 경우
    if len(ingr_indexes) == 0:
        return None

    # 재료가 있을 경우
    recommend_recipes = {}

    # 재료를 포함하는 레시피를 찾음
    for ingr_index in ingr_indexes:
        recipe_ingredients = Ingredient.objects.filter(food_id=ingr_index)
        if len(recipe_ingredients) == 0:
            continue
        for recipe_ingredient in recipe_ingredients:
            recipe_id = int(recipe_ingredient.recipe_id)
            if recipe_id in recommend_recipes:
                recommend_recipes[recipe_id] += 1
            else:
                recommend_recipes[recipe_id] = 1
    
    # 주재료일 경우 가중치를 더 높임
    if main is not None:
        for ingr_index in main_indexes:
            recipe_ingredients = Ingredient.objects.filter(food_id=ingr_index)
            if len(recipe_ingredients) == 0:
                continue
            for recipe_ingredient in recipe_ingredients:
                recipe_id = int(recipe_ingredient.recipe_id)
                if recipe_id in recommend_recipes:
                    recommend_recipes[recipe_id] += 100
                else:
                    recommend_recipes[recipe_id] = 100

    # 가장 많이 포함하는 레시피를 순으로 정렬
    recipe_vectors = []
    for recipe_id, recipe_count in recommend_recipes.items():
        recipe_vectors.append([recipe_id, recipe_count])
    recipe_vectors.sort(key=lambda x: x[1], reverse=True)
    # print(recipe_vectors)

    # 상위 top개의 레시피를 추천
    recipe_names = []
    for i in range(min(top, len(recipe_vectors))):
        recipe_id = int(recipe_vectors[i][0])
        # print(recipe_id)
        recipe = Recipe.objects.filter(id=recipe_id)
        # print(recipe.count())
        # print(type(recipe.first()))
        # print(len(recipe))

        # recipe = QuerySet()
        # recipe.first()
        try:
            recipe_names.append(recipe[0].name)
        except:
            print("error:",recipe_id)
            continue

    return recipe_names

# Create your views here.
def index(request):
    return render(request, 'main/index.html')

def chat(request):
    if request.method == "POST":
        params = request.POST
        csrf = params['csrf']
        msg = params['message']

        data = dict(params)
        del data['csrf']
        data['message'] = ""

        # print(data)

        dlf = Dialogflow('private_key.json', session_id=csrf)
        # 입력 전
        intent = data['prev_intent'][0]
        # print("prev:", intent)
        data['prev_intent'] = data["intent"]

        # 입력 후
        output = dlf.input(msg)
        # print("output:", output)
        intent = get_intent_index(dlf.get_intent())
        # print("curr:", intent)

        # 재료 입력 인식
        if intent == "ingredient" or intent == "main_ingredient":
            context = dlf.get_parameters()
            context = list(set(context))
            if intent == "ingredient":
                data["ingredients"] = context
            else:
                data["main_ingredients"] = context
            # print("재료:", context)

            result = []
            # 재료가 없을 경우
            if len(context) == 0:
                output = "올바른 재료를 입력해주세요."
            # 재료가 있을 경우
            else:
                if intent == "ingredient":
                    result = search_recipe(context, top=TOP)
                elif intent == "main_ingredient":
                    ingredients = data["ingredients"][0].split(",")
                    result = search_recipe(ingredients, main=context, top=TOP)
                if result is None:
                    output = "올바른 재료를 입력해주세요."
                elif len(result) == 0:
                    output = "아쉽게도 해당하는 레시피가 없습니다."
                else:
                    output += "@@"
                    for i, recipe in enumerate(result):
                        output += f"{i+1}. {recipe}" + "@"
                    output += "@마음에 드는 레시피의 번호를 입력해주세요!"
                    if intent == "ingredient":
                        output += "@꼭 들어가야 하는 재료가 있다면 재료를 다시 입력해주세요."
            
            data["message"] = output
            data["intent"] = intent
            data["recommended_recipes"] = result
            return JsonResponse(data, safe=False)
            
            # print(context)
        
        # 추천 레시피 선택 인식
        elif intent == "recommend_positive":
            context = dlf.get_parameters()
            recipe_index = int(list(context)[0]) - 1
            user_recipes = data["recommended_recipes"][0].split(",")
            # print("레시피:", user_recipes)
            # print("선택:", recipe_index)
            if recipe_index < 0 or recipe_index >= TOP:
                output = "올바른 레시피 번호를 입력해주세요."
            else:
                recipe = user_recipes[recipe_index]
                output = f"{recipe_index + 1}번({recipe})의 레시피를 보여드릴게요!@" + output
            
            data["message"] = output
            data["intent"] = intent
            data["recipe"] = recipe
            data["recipe_id"] = get_recipe_index(recipe)
            return JsonResponse(data, safe=False)
        
        elif intent == "inbun":
            inbun = dlf.get_parameters()
            recipe_id = data["recipe_id"][0]
            # print("레시피:", recipe_id)
            # print("인분:", inbun)
            
            recipe_context = get_recipe_context(recipe_id)
            # print("레시피:", recipe_context)
            # data = recipe_context + "@"

            ingredients = get_ingredients(recipe_id)
            # print("재료:", str(ingredients))
            amounts, is_calculated = get_amounts(recipe_id, int(inbun))
            ingredients_text = ""
            for i, ingredient in enumerate(ingredients):
                ingredients_text += f"{ingredient} {amounts[i]} \n"
            # print(ingredients_text)
            recipe_context = "재료 목록: \n" + ingredients_text + recipe_context

            output = f"{data['recommended_recipes']}"
            if is_calculated:
                output += f"({inbun}인분 기준)"
            output += "@@"

            gpt = GPT()
            data = StreamingHttpResponse(gpt.chat(recipe_context), content_type="text/event-stream")
            data['X-Accel-Buffering'] = 'no'  # Disable buffering in nginx
            data['Cache-Control'] = 'no-cache'  # Ensure clients don't cache the data
            data['inbun'] = inbun
            # chat = gpt.chat(recipe_context).replace("\n", "@")
            # data += chat
            
            return data

        else:
            data["message"] = output
            data["intent"] = intent

        return JsonResponse(data, safe=False)

def upload(request):
    if request.method == "POST":
        id = random.randint(0, 1000)
        img = request.POST.get('image')
        # base64 디코딩
        # print(img)
        img = base64.b64decode(img)
        # 이미지 저장하기
        with open(f'images/img{id}.jpg', 'wb') as f:
            f.write(img)
        
        # 이미지 분석
        model = MainConfig.model
        results = model.inference(f'images/img{id}.jpg')

        names = []
        # print("type:", type(results))
        for result in results:
            index = int(result.boxes.cls.tolist()[0])
            names.append(index_to_ingredient_kor[index])
        
        names = list(set(names))
        # print("names:", names)

        # 이미지 삭제
        os.remove(f'images/img{id}.jpg')

        return JsonResponse({"message": "success", "names": names}, safe=False)