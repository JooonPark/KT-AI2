import requests
import json
import os
import pymysql
import re
from selenium import webdriver
from datetime import datetime, timedelta, date
from flask import Flask, render_template
from flask import request , redirect ,abort , session , jsonify
from bs4 import BeautifulSoup
from selenium import webdriver

app = Flask(__name__, template_folder="views", static_folder="static")
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.secret_key = b'dfdfdfasdfasdfasdfasdf'

##################데이터베이스 - mysql 연결########################

db = pymysql.connect(
    user = 'root',
    passwd = 'qudtka99',
    host = 'localhost',
    db = 'exam',
    cursorclass = pymysql.cursors.DictCursor,
    charset = 'utf8'
    )

db1 = pymysql.connect(
    user = 'root',
    passwd = 'qudtka99',
    host = 'localhost',
    db = 'workshop1',
    cursorclass = pymysql.cursors.DictCursor,
    charset = 'utf8'
    )

##################################################################
#리스트 주소 만들기
def get_menu():
    cursor = db.cursor()
    cursor.execute("select id, title from topic")
    menu= [f"<li><a href='/meeting/{row['id']}'>{row['title']}</a></li>" for row in cursor.fetchall()]
    
    return "\n".join(menu)

def get_menu1():
    cursor = db.cursor()
    cursor.execute("select id, title from craw")
    menu1= [f"<li><a href='/crawling/{row['title']}'>{row['title']}</a></li>" for row in cursor.fetchall()]
    
    return "\n".join(menu1)

##################################################################
#메인 화면
@app.route("/main")
def index():
        
    if 'user' in session:
        title = 'Welcome ' + session['user']['name']
    else :
        title = 'Welcome '
        
    content = '네트워크 부문 업무 회의록 게시판'
    menu = get_menu()
    
    
    return render_template('main-joon.html',
                              title = "",
                              content = content,
                              id = "",
                              menu = menu)

##################################################################
#회의록 화면
@app.route("/meeting")
def meeting():

    menu = get_menu()
    

    return render_template('meeting-main.html',
                              menu = menu)

##################################################################
#크롤링 화면
@app.route("/crawling")
def crawling():
    
    menu1 = get_menu1()
    
    return render_template('crawling-main.html',
                              menu1 = menu1)

##############################################################
#회의록 리스트들 들어가기
@app.route("/meeting/<id>")
def make_title(id):
    cursor = db.cursor()
    cursor.execute(f"select * from topic where id='{id}'")
    topic = cursor.fetchone()
    
    if topic is None:
        abort(404)
    
    regex = re.compile("(\w+\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?)")
    re.findall(regex,topic['description'])
    excontent = re.sub(regex,"<a target='_blank' href=\g<1>>\g<1></a> " , topic['description'])
    
    
        
    
    
    return render_template('meeting-joon.html',
                              title = topic['title'],
                              content = excontent,
                              
                              id = topic['id'],
                              menu = get_menu())

##################################################################
#list 삭제하기
@app.route("/meeting/delete/<id>")
def delete(id):
    cursor = db.cursor()
    cursor.execute(f"delete from topic where id='{id}'")
    db.commit()
    
    return redirect("/meeting")

@app.route("/crawling/delete/<title>")
def delete1(title):
    cursor = db.cursor()
    cursor.execute(f"delete from craw where title='{title}'")
    db.commit()
    
    return redirect("/crawling")

########################################################################
#list 추가하기
@app.route("/meeting/create", methods=['GET','POST'])
def create_meeting():

    if request.method =='GET':
        return render_template('meeting-create.html',
                              message = '',
                              menu = get_menu())
    
    elif request.method == 'POST':
        cursor = db.cursor()
        sql = f"""
            insert into topic (title, description, created, author_id) values ('{request.form['title']}','{request.form['desc']}', '{datetime.now()}', '{session['user']['id']}')
                """
        
        cursor.execute(sql)
        db.commit()
                           
        return redirect('/meeting')
    
@app.route("/crawling/create", methods=['GET','POST'])
def create_craw():

    if request.method =='GET':
        return render_template('crawling-create.html',
                              message = '',
                              menu1 = get_menu1())
    
    elif request.method == 'POST':
        cursor = db.cursor()
        sql = f"""
            insert into craw (title, description, created, author_id) values ('{request.form['title']}','{request.form['title']}', '{datetime.now()}', '{session['user']['id']}')
                """
        
        cursor.execute(sql)
        db.commit()
                           
        return redirect('/crawling')
    

        
##########################################################################
#로그인 화면
@app.route("/", methods=['GET','POST'])
def login():
    message = ""
    if request.method == 'POST':
        cursor = db.cursor()
        cursor.execute(f"select id, name, profile, password from author where name = '{request.form['id']}'")
        user = cursor.fetchone()
        
        if user is None:
            message = "아이디 오류"
        else :
            cursor.execute(f"select id, name, profile, password from author where name = '{request.form['id']}' and password = SHA2('{request.form['pw']}',256)")
            user = cursor.fetchone()
            
            if user is None:
                message = "비밀번호 오류"
            else :
                session['user'] = user
                return redirect("/main")
    
    return render_template('login.html', 
                           message=message, 
                           menu=get_menu())

#######################################################################
#로그아웃
@app.route("/logout")
def logout():
    session.pop('user',None)
    
    return redirect("/")

######################################################################
#회원가입
@app.route("/signup" , methods = ['get','post'])
def signup():
    cursor = db.cursor()
    if request.method =='GET':
        return render_template('signup.html',
                              message = '',
                              menu = get_menu())  
    
    
    elif request.method == 'POST':
        sql = f"""insert into author (name, profile, password) values('{request.form['name']}','{request.form['profile']}',SHA2('{request.form['password']}',256))"""
        
        cursor.execute(sql)
        db.commit()
        
        return redirect('/')

##########################################################################
# #네이버 사진 크롤링 들어가기 셀레니움 이용x
# @app.route("/crawling/<word>")
# def crawler_naver(word):
#     def download_img_from_tag(tag, filename):
#         response = requests.get(tag['data-source'])
#         with open(filename, 'wb') as f:
#             f.write(response.content)
    
    
    
#     url = f'https://search.naver.com/search.naver'
#     query = {
#         "where" : "image",
#         "sm" : "tab_jum",
#         "query" : word
#     }
    
#     response = requests.get(url, params = query)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     tags = soup.select('img._img')
    
#     # tag를 던지면 이미지를 저장하고 이미지명을 반환하는 함수
#     filenames=[]
#     for i, tag in enumerate(tags):    
#         filename = f'static/search/{word}{i}.jpg'
#         download_img_from_tag(tag ,filename)
#         filenames.append(filename)


#     return render_template('crawling-joon.html', files = filenames)
    
    
############################################################################
#구글 사진 크롤링 셀레니움 이용
@app.route('/crawling/<title>')
def crawler_google(title):
    cursor = db.cursor()
    cursor.execute(f"select * from craw where title='{title}'")
    craw = cursor.fetchone()
    
    url = f'https://www.google.com/search?q={title}&tbm=isch'
   
    opts = webdriver.ChromeOptions()
    opts.add_argument('--headless')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('./chromedriver', options=opts)
    driver.implicitly_wait(3)
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tags = soup.select('img.rg_i')

    def download_jpeg_from_tag(tag, save_to):
        try:
            img_url = tag['src']
            img_str = img_url.replace('data:image/jpeg;base64,', '')
            import base64
            img_data = base64.b64decode(img_str)
            with open(save_to, 'wb') as f:
                f.write(img_data)
        except:
            return False
        else:
            return save_to

    filenames = []
    saved_cnt=0
    for tag in tags:
        save_to = f'static/search/{title}{saved_cnt+1}.jpg'
        if download_jpeg_from_tag(tag, save_to):
            filenames.append(save_to)
        saved_cnt += 1

    return render_template('crawling-joon.html',
                           files=filenames,
                           title=craw['title'],
                           menu1=get_menu1())

app.run(port=8000)    
