# 레시피 저장
import pandas as pd
import sqlite3

def save():
    # Connect to (create) database.
    # dic을 받아서 해당하는 카테고리의 데이터를 저장
    database = "db.sqlite3"
    conn = sqlite3.connect(database)

    # {'id': 'category_name'} 형식인 dic을 받아서 해당하는 카테고리의 데이터를 저장
    
    # for key, value in dic.items():
    #     # key, value를 df로 만들기
    #     df = pd.DataFrame({'id': [key], 'category_name': [value]})
    #     df.to_sql('news_categorylist', conn, if_exists='append', index=False)

    # csv 파일을 불러와 df로 만들어 저장
    df_recipe = pd.read_csv('data/레시피.csv')
    df_recipe.to_sql('main_recipe', conn, if_exists='append', index=False)

    df_ingredient = pd.read_csv('data/재료.csv')
    df_ingredient.to_sql('main_ingredient', conn, if_exists='append', index=False)

    df_food = pd.read_csv('data/식품.csv')
    df_food.to_sql('main_food', conn, if_exists='append', index=False)

    conn.close()



def clear():
    # Connect to (create) database.
    database = "db.sqlite3"
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute("DELETE FROM main_recipe")
    cur.execute("DELETE FROM main_ingredient")
    cur.execute("DELETE FROM main_food")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    clear()
    save()