from django.shortcuts import render
from django.http import JsonResponse
from json import JSONEncoder
from django.views.decorators.csrf import csrf_exempt
from web.models import User, Token, Expense, Income, Passwordresetcodes
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password
from postmark import PMMail
from django.conf import settings
import requests
import random
import time
from django.utils.crypto import get_random_string
from django.db.models import Sum, Count
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from .utils import grecaptcha_verify, RateLimited
from django.core import serializers
from django.contrib.auth.decorators import login_required

# Create your views here.
def login(request):
    if 'username' in request.POST and 'password' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        this_user = get_object_or_404(User, username=username)
        if check_password(password, this_user.password):
            this_token = get_object_or_404(Token, user=this_user)
            token = this_token.token

            # Save user ID in the session
            request.session['user_id'] = this_user.id

            # Fetch user expenses and incomes
            expenses = Expense.objects.filter(user=this_user)
            incomes = Income.objects.filter(user=this_user)

            # total
            total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
            total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
            context = {
                'result': 'ok',
                'token': token,
                'expenses': expenses,
                'incomes': incomes,
                'total_expense': total_expense,
                'total_income': total_income
            }
            print("HHHHHHHHHHHHHHHHHHHHHHHHHHHH",this_user)
            return render(request, 'dashboard.html', context)
        else:
            context = {'result': 'error'}
            return JsonResponse(context, encoder=JSONEncoder)
    else:
        context = {'message': ''}
        return render(request, 'login.html', context)

@csrf_exempt
def news(request):
    news = News.objects.all().order_by('-date')[:11]
    news_serialized = serializers.serialize("json", news)
    return JsonResponse(news_serialized, encoder=JSONEncoder, safe=False)

random_str = lambda N: ''.join(
    random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))

def register(request):
    if 'requestcode' in request.POST:
    # if request.POST.has_key(
    #         'requestcode'):  # form is filled. if not spam, generate code and save in db, wait for email confirmation, return message
        # is this spam? check reCaptcha

        # captcha
        # if not grecaptcha_verify(request):  # captcha was not correct
        #     context = {
        #         'message': 'کپچای گوگل درست وارد نشده بود. شاید ربات هستید؟ کد یا کلیک یا تشخیص عکس زیر فرم را درست پر کنید. ببخشید که فرم به شکل اولیه برنگشته!'}  # TODO: forgot password
        #     return render(request, 'register.html', context)

        # duplicate email
        if User.objects.filter(email=request.POST['email']).exists():
            context = {
                'message': 'متاسفانه این ایمیل قبلا استفاده شده است. در صورتی که این ایمیل شما است، از صفحه ورود گزینه فراموشی پسورد رو انتخاب کنین. ببخشید که فرم ذخیره نشده. درست می شه'}  # TODO: forgot password
            # TODO: keep the form data
            return render(request, 'register.html', context)
        # if user does not exists
        if not User.objects.filter(username=request.POST['username']).exists():
            code = get_random_string(length=32)
            now = datetime.now()
            email = request.POST['email']
            password = make_password(request.POST['password'])
            username = request.POST['username']
            temporarycode = Passwordresetcodes(
                email=email, time=now, code=code, username=username, password=password)
            temporarycode.save()
            #message = PMMail(api_key=settings.POSTMARK_API_TOKEN,
            #                 subject="فعالسازی اکانت بستون",
            #                 sender="amini@gmail.com",
            #                 to=email,
            #                 text_body=" برای فعال کردن اکانت بستون خود روی لینک روبرو کلیک کنید: {}?code={}".format(
            #                     request.build_absolute_uri('/accounts/register/'), code),
            #                 tag="account request")
            #message.send()
            message = 'ایمیلی حاوی لینک فعال سازی اکانت به شما فرستاده شده، لطفا پس از چک کردن ایمیل، روی لینک کلیک کنید.'
            message = 'قدیم ها ایمیل فعال سازی می فرستادیم ولی الان شرکتش ما رو تحریم کرده (: پس راحت و بی دردسر'
            body = " برای فعال کردن اکانت بستون خود روی لینک روبرو کلیک کنید: <a href=\"{}?code={}\">لینک رو به رو</a> ".format(request.build_absolute_uri('/accounts/register/'), code)
            message = message + body
            context = {
                'message': message }
            return render(request, 'index.html', context)
        else:
            context = {
                'message': 'متاسفانه این نام کاربری قبلا استفاده شده است. از نام کاربری دیگری استفاده کنید. ببخشید که فرم ذخیره نشده. درست می شه'}  # TODO: forgot password
            # TODO: keep the form data
            return render(request, 'register.html', context)
    elif 'code' in request.GET:  # user clicked on code
        # elif request.GET.has_key('code'):  # user clicked on code
        code = request.GET['code']
        if Passwordresetcodes.objects.filter(
                code=code).exists():  # if code is in temporary db, read the data and create the user
            new_temp_user = Passwordresetcodes.objects.get(code=code)
            newuser = User.objects.create(username=new_temp_user.username, password=new_temp_user.password,
                                          email=new_temp_user.email)
            this_token = get_random_string(length=48)
            token = Token.objects.create(user=newuser, token=this_token)
            # delete the temporary activation code from db
            Passwordresetcodes.objects.filter(code=code).delete()
            context = {
                'message': 'اکانت شما ساخته شد. توکن شما {} است. آن را ذخیره کنید چون دیگر نمایش داده نخواهد شد! جدی!'.format(
                    this_token)}
            return render(request, 'index.html', context)
        else:
            context = {
                'message': 'این کد فعال سازی معتبر نیست. در صورت نیاز دوباره تلاش کنید'}
            return render(request, 'register.html', context)
    else:
        context = {'message': ''}
        return render(request, 'register.html', context)


# return username based on sent POST Token

@csrf_exempt
@require_POST
def whoami(request):
    if request.POST.has_key('token'):
        this_token = request.POST['token']  # TODO: Check if there is no `token`- done-please Check it
        # Check if there is a user with this token; will retun 404 instead.
        this_user = get_object_or_404(User, token__token=this_token)

        return JsonResponse({
            'user': this_user.username,
        }, encoder=JSONEncoder)  # return {'user':'USERNAME'}

    else:
        return JsonResponse({
            'message': 'لطفا token را نیز ارسال کنید .',
        }, encoder=JSONEncoder)  #


# return General Status of a user as Json (income,expense)

@csrf_exempt
@require_POST
def query_expense(request):
    this_token = request.POST['token']
    num = request.POST.get('num', 10)
    this_user = get_object_or_404(User, token__token=this_token)
    expense = Expense.objects.filter(user=this_user).order_by('-date')[:num]
    expense_serialized = serializers.serialize("json", expense)
    return JsonResponse(expense_serialized, encoder=JSONEncoder, safe=False)


@csrf_exempt
@require_POST
def query_income(request):
    this_token = request.POST['token']
    num = request.POST.get('num', 10)
    this_user = get_object_or_404(User, token__token=this_token)
    income = Income.objects.filter(user=this_user).order_by('-date')[:num]
    income_serialized = serializers.serialize("json", income)
    return JsonResponse(income_serialized, encoder=JSONEncoder, safe=False)

@csrf_exempt
@require_POST
def generalstat(request):
    #TODO: should get a valid duration (from - to), if not, use 1 month
    #TODO: is the token valid?
    this_token = request.POST['token']
    this_user = User.objects.filter(token__token = this_token).get()
    income = Income.objects.filter(user = this_user).aggregate(Count('amount'), Sum('amount'))
    expense = Expense.objects.filter(user = this_user).aggregate(Count('amount'), Sum('amount'))
    context = {}
    context['expense'] = expense
    context['income'] = income
    return JsonResponse(context, encoder=JSONEncoder)

def index(request):
    context = {}
    return render(request, 'index.html', context)


@csrf_exempt
# @require_POST
def submit_expense(request):
    """user submits an expense"""
    if request.method == 'POST':
        #TODO: validate data. user might be fake. token might be fake. amount might be ....
        # this_token = request.POST['token']
        # this_token =request.user.Token
        # this_user = User.objects.filter(token__token = this_token).get()
        user_id = request.session.get('user_id')
        this_user = get_object_or_404(User, id=user_id)
        # this_user = request.user
        print("HHHHHHHHHHHHHHHHHHHHHHHHHHHH",this_user)
        if 'date' not in request.POST:
            date = datetime.now()
        Expense.objects.create(user = this_user, amount = request.POST['amount'],
            text = request.POST['text'], date = request.POST['date'])
    context = {}
    return render(request, 'submit_expense.html', context)

    # print("I'm in submit expense")
    # print (request.POST)

    # return JsonResponse({
    #     'status' : 'ok'
    # }, encoder = JSONEncoder)


@csrf_exempt
@login_required
def submit_income(request):
    """user submits an income"""
    if request.method == 'POST':

        user_id = request.session.get('user_id')
        this_user = get_object_or_404(User, id=user_id)
        # this_user = request.user
        print('************************', this_user)
        #TODO: validate data. user might be fake. token might be fake. amount might be ....
        # this_token = request.POST['token']
        # this_user = User.objects.filter(token__token = this_token).get()
        if 'date' not in request.POST:
            date = datetime.now()
        Income.objects.create(user = this_user, amount = request.POST['amount'],
            text = request.POST['text'], date = request.POST['date'])

    context = {}
    return render(request, 'submit_income.html', context)
        # print("I'm in submit income")
        # print (request.POST)

        # return JsonResponse({
        #     'status' : 'ok'
        # }, encoder = JSONEncoder)
