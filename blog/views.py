from django.shortcuts import render,HttpResponse,redirect
from django.db.models import Count,Avg,Max
from django.contrib import auth
from blog.models import ArticleUpDown,Comment
from django.db.models import F
from django.db import transaction
import json
from django.http import JsonResponse
# Create your views here.
from blog.models import Article,UserInfo,Tag,Category,Article2Tag

from b_blog import settings
import os
from PIL import ImageDraw,Image,ImageFilter,ImageFont
import random

def login(request):

    if request.method == 'POST':
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        cod = request.POST.get('code')
        if cod.upper() !=  request.session['code'].upper():
            return render(request,'login.html',{'msg':'验证码错误'})
        user = auth.authenticate(username=user, password=pwd)
        if user:
            auth.login(request, user)
            return redirect('/index/')

        return render(request,'login.html',{'msg':'账号或密码错误'})
    return render(request,'login.html')


def index(request):
    # print(request.POST)
    article = Article.objects.all()
    return render(request,'index.html',{'article':article})


def logout(request):
    auth.logout(request)
    return redirect('/index/')


def homesite(request, username, **kwargs):
    user = UserInfo.objects.filter(username= username).first()

    if not user:
        return HttpResponse('404')
    blog = user.blog
    articles = Article.objects.filter(user__username=username)
    tag = Tag.objects.filter(blog=blog).annotate(c=Count('article__title')).values('c', 'title','pk')
    category = Category.objects.filter(blog=blog).annotate(c=Count('article__title')).values('c', 'title','pk')

    date_list = Article.objects.filter(user=user).extra(select={"date": "strftime('%%Y/%%m',create_time)"}).values(
        'date').annotate(c=Count('title')).values('c', 'date')
    if not kwargs:

        return render(request,'homesite.html',{'articles':articles,'user':user,'tag':tag,'category':category,'date_list':date_list})
    else:
        # print(kwargs)
        if kwargs.get('kind')=='tag':
            article = Article.objects.filter(user__username=username).filter(article2tag__tag_id=kwargs.get('id'))
            if not article:
                return HttpResponse('404')
            return render(request,'abc.html',locals())
        elif kwargs.get('kind') == 'article':
            article = Article.objects.filter(user__username=username).filter(pk=kwargs.get('id')).first()
            comment_list = Comment.objects.filter(article=article)
            return render(request,'art.html',locals())
        else:
            article = Article.objects.filter(user__username=username).filter(category_id=kwargs.get('id'))
            return render(request,'abc.html',locals())


def check(request):
    id = request.POST.get('art_id')
    is_up = request.POST.get('is_up')
    is_up = json.loads(is_up)
    user_id = request.user.pk
    response = {'state': True,'msg':None}
    obj = ArticleUpDown.objects.filter(user_id=user_id,article_id=id).first()

    if obj:
        response['state']= False
        response['msg']=obj.is_up
    else:
        with transaction.atomic():
            obj1= ArticleUpDown.objects.create(user_id=user_id,article_id=id,is_up=is_up)
            if is_up:
                Article.objects.filter(pk=id).update(up_count=F('up_count')+1)
            else:
                Article.objects.filter(pk=id).update(down_count=F('down_count')+1)
    return JsonResponse(response)

def comment(request):

    # 获取数据

    user_id=request.user.pk
    article_id=request.POST.get("article_id")
    content=request.POST.get("content")
    pid=request.POST.get("pid")
    # 生成评论对象
    with transaction.atomic():
        comment=Comment.objects.create(user_id=user_id,article_id=article_id,content=content,parent_comment_id=pid)
        Article.objects.filter(pk=article_id).update(comment_count=F("comment_count")+1)

    response={"state":True}
    response["timer"]=comment.create_time.strftime("%Y-%m-%d %X")
    response["content"]=comment.content
    response["user"]=request.user.username

    return JsonResponse(response)

def backend(request):
    user=request.user
    article_list=Article.objects.filter(user=user)
    return render(request,"backend/backend.html",locals())

def add_article(request):
    if request.method=="POST":

        title=request.POST.get("title")
        content=request.POST.get("content")
        user=request.user
        cate_pk=request.POST.get("cate")
        tags_pk_list=request.POST.getlist("tags")

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")
        # 文章过滤：
        for tag in soup.find_all():
            # print(tag.name)
            if tag.name in ["script",]:
                tag.decompose()

        # 切片文章文本
        desc=soup.text[0:150]

        article_obj=Article.objects.create(title=title,content=str(soup),user=user,category_id=cate_pk,desc=desc)

        for tag_pk in tags_pk_list:
            Article2Tag.objects.create(article_id=article_obj.pk,tag_id=tag_pk)

        return redirect("/backend/")


    else:

        blog=request.user.blog
        cate_list=Category.objects.filter(blog=blog)
        tags=Tag.objects.filter(blog=blog)
        return render(request,"backend/add_article.html",locals())

def upload(request):
    print(request.FILES)
    obj=request.FILES.get("upload_img")
    name=obj.name

    path=os.path.join(settings.BASE_DIR,"static","upload",name)
    with open(path,"wb") as f:
        for line in obj:
            f.write(line)

    import json

    res={
        "error":0,
        "url":"/static/upload/"+name
    }

    return HttpResponse(json.dumps(res))


def delete(request, id):
    Article.objects.filter(pk=id).delete()
    return redirect('/backend/')


def change(request, id):
    return HttpResponse('ok')


def code(request):
    img, s = draw1()
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    request.session['code'] = s
    from io import BytesIO
    steam = BytesIO()
    img.save(steam,'png')
    return HttpResponse(steam.getvalue())


def draw1():
    s = ''

    def create_char():
        return chr(random.randint(65, 90))

    def create_color():
        return (random.randint(0, 255), random.randint(10, 255), random.randint(64, 255))

    img = Image.new(mode="RGB", size=(120, 30), color=(255, 255, 255))  # 图大小，bgc
    draw = ImageDraw.Draw(img, mode='RGB')
    font = ImageFont.truetype('kumo.ttf', 28)  # 文件 字体大小
    for i in range(5):
        char = create_char()
        s += str(char)
        h = random.randint(0, 4)
        draw.text([i * 120 / 5, h], char, font=font, fill=create_color())

    # 干扰点
    for i in range(20):
        draw.point([random.randint(0, 120), random.randint(0, 30)], fill=create_color())

    # 干扰⚪
    for i in range(20):
        draw.point([random.randint(0, 120), random.randint(0, 30)], fill=create_color())
        x = random.randint(0, 120)
        y = random.randint(0, 30)
        draw.arc((x, y, x + 5, y + 5), 0, 90, fill=create_color())

    # 干扰线
    for i in range(5):
        x1 = random.randint(0, 120)
        y1 = random.randint(0, 30)
        x2 = random.randint(0, 120)
        y2 = random.randint(0, 30)
        draw.line((x1, y1, x2, y2), fill=create_color())
    return img,s