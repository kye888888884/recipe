from django.shortcuts import render
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from .dialogflow import Dialogflow
from .models import Recipe, Ingredient, Food
from .gpt import GPT

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
    print("기준:", people, "명")

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
    # print(ingr_indexes)

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
                if main is not None and ingr_index in main_indexes:
                    recommend_recipes[recipe_id] += 100
                recommend_recipes[recipe_id] += 1
            else:
                recommend_recipes[recipe_id] = 1

    # 가장 많이 포함하는 레시피를 순으로 정렬
    recipe_vectors = []
    for recipe_id, recipe_count in recommend_recipes.items():
        recipe_vectors.append([recipe_id, recipe_count])
    recipe_vectors.sort(key=lambda x: x[1], reverse=True)
    # print(recipe_vectors)

    # 상위 top개의 레시피를 추천
    recipe_names = []
    for i in range(min(top, len(recipe_vectors))):
        recipe_id = recipe_vectors[i][0]
        recipe = Recipe.objects.filter(id=recipe_id)[0]
        recipe_names.append(recipe.name)

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

        print(data)

        dlf = Dialogflow('private_key.json', session_id=csrf)
        # 입력 전
        intent = data['prev_intent'][0]
        print("prev:", intent)
        data['prev_intent'] = data["intent"]

        # 입력 후
        output = dlf.input(msg)
        print("output:", output)
        intent = get_intent_index(dlf.get_intent())
        print("curr:", intent)

        # 재료 입력 인식
        if intent == "ingredient" or intent == "main_ingredient":
            context = dlf.get_parameters()
            context = list(set(context))
            if intent == "ingredient":
                data["ingredients"] = context
            else:
                data["main_ingredients"] = context
            print("재료:", context)

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
            
            recipe_context = get_recipe_context(inbun)
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