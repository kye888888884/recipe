import os
import sys
import django
import datetime
import json
from text.lengths import Length

# sys.path.append('d:\python_project\myproject')  # 프로젝트의 절대경로
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant.settings') 	# settings.py가 있는곳
django.setup()

import pandas as pd
import sqlite3
from main.models import Book, Content, Picture

LINE_LEN = 580 # 한 줄의 픽셀 수
PAGE_LEN = 23 # 한 페이지의 줄 수
IMAGE_LEN = 6 # 이미지의 줄 수
PARA_GAP = 0.25 # 문단간 간격 (줄)
punc = ['.', ',', '?', '!', ')', ']', '"', "'"] # 문장부호

def save(id, file_path, title, author='', publisher='', category=1, description=''):
    database = "db.sqlite3"
    conn = sqlite3.connect(database)

    # 새로운 book 엔티티 만들기
    book = Book(title=title, author=author, publisher=publisher, publication_date=datetime.datetime.now().date(), category=category, description=description, id=id)
    book.save()

    # 새로운 content 엔티티 만들기
    with open(file_path, 'r', encoding='utf-8') as f:
        txt = f.read()
        ins_len = Length()
        line = ""
        line_len = 30
        line_num = 0
        line_num_stack = 0
        para_num = 0
        start_lines = [0]
        pages = []
        page = [0]
        paragraphs = [0]
        i = 0
        is_image = False
        skip = 0
        for t in txt:
            if skip > 0:
                i += 1
                skip -= 1
                continue
            line += t
            if line.startswith('%//'): # 페이지가 넘어갈 경우
                line = ""
                line_num = 0
                start_lines.append(line_num_stack)
                pages.append(page.copy())
                page = [i + 1]
                para_num = 0
                # skip = 10
            elif line.startswith('%>>') and not is_image: # 이미지일 경우
                is_image = True
                if (line_num + IMAGE_LEN) > PAGE_LEN: # 이미지가 페이지를 넘어갈 경우
                    line_num = IMAGE_LEN
                    pages.append(page.copy())
                    page = [i - 2]
                    line_num_stack += 1
                    start_lines.append(line_num_stack)
                else: # 이미지가 페이지를 넘어가지 않을 경우
                    # print(line_num_stack)
                    line_num += IMAGE_LEN
                line = ""
            else: # 글자일 경우
                cur_len = ins_len.get_length(t) # 글자의 픽셀 수

                line_len += cur_len # 소수점 4자리까지만 계산
                line_len = int(line_len * 10000) / 10000

                if t == '\n': # 글자가 줄넘김일 경우
                    is_image = False
                    line = ""
                    line_len = 16
                    page.append(i + 1)
                    line_num += 1
                    line_num_stack += 1
                    para_num += 1
                    paragraphs.append(line_num_stack)
                elif line_len > LINE_LEN: # 한 줄이 꽉찼을 경우
                    line = ""
                    line_num += 1
                    line_num_stack += 1
                    if t in punc: # 문장부호일 경우
                        line_len = 0
                        page.append(i + 1)
                    else: # 문장부호가 아닐 경우
                        line_len = cur_len
                        page.append(i)
            
            if line_num >= PAGE_LEN - para_num * PARA_GAP: # 한 페이지가 꽉찼을 경우
                line_num = 0
                start_lines.append(line_num_stack)
                pages.append(page.copy())
                page = [i]
                para_num = 0

            i += 1
        
        # 마지막 페이지 추가
        page.append(i)
        pages.append(page.copy())
        start_lines.append(line_num_stack)

        # print(pages)
        page = len(pages)

        print(start_lines)

        # 리스트를 JSON 형식으로 변환
        pages = str(pages).replace("'", '"')
            
        content = Content(book=book, content=txt, pages=pages, page=page, paragraphs=paragraphs, start_lines=start_lines)
        content.save()

    conn.close()

def clear(id):
    # Connect to (create) database.
    database = "db.sqlite3"
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute("DELETE FROM main_book WHERE id = ?", (id,))
    cur.execute("DELETE FROM main_content WHERE book_id = ?", (id,))
    # cur.execute("DELETE FROM main_picture")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # JSON 파일에서 파라미터 추출
    json_file = open('book_config.json', 'r', encoding='utf-8')
    json_data = json.load(json_file)
    json_file.close()
    clear(json_data['id'])
    save(
        json_data['id'],
        json_data['file_path'],
        json_data['title'],
        json_data['author'],
        json_data['publisher'], 
        json_data['category'], 
        json_data['description']
    )