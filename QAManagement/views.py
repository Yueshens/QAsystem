import datetime
import random
import time
from zhipuai import ZhipuAI
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.db.models import Count
from django.http import HttpResponseRedirect, JsonResponse
import json

from urllib.parse import urlencode

from .models import User,QuestionCount,NewUser
import time
from .withweb import Withweb
from .withweb_all import Withweb_all
import os
from apscheduler.schedulers.background import BackgroundScheduler
from django.db import connection
import urllib
import requests
# Create your views here.

# 引入两个算法程序
from QAManagement.webextract import hauwei_extractor,moban_extractor
import sre_constants
from QAManagement.ques_generate import QG_paragraph,QA_save
from QAManagement.question_generalization.temporary_generate import Temporary
# 时间工具类
from QAManagement.ques_generate import GetTimeBeforeToday
# import logging

import operator as op

# 引入数据库类
from .models import UserMining





# logger = logging.getLogger(__name__)

# 设置一个全局变量，这个是es的表
myindex = 'qa_test'
# qa_init qa_initial
# qa_sys
# qs_store
# qa_real
# 选择的文件列表
file_list = []
# 生成的QA对列表
result_list = []



def index(request):
    #return HttpResponse("HelloWorld")
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']

    # 存入日志
    # logger.info('访问者IP：' + ip)

    return render(request,"index.html")
def QAManagement(request):
    return render(request,"QAManagement.html")
def QAManage(request):
    # qa_results = []
    # data_json = {}
    # withweb = Withweb()
    # result = withweb.searchall(myindex)
    # for i in range(len(result)):
    #     qa_result = {}
    #     qa_result['id'] = result[i]['_id']
    #     qa_result['question'] = result[i]['_source']['question']
    #     qa_result['answer'] = result[i]['_source']['answer']
    #     qa_result['link'] = result[i]['_source']['link']
    #     qa_result['subject'] = result[i]['_source']['subject']
    #
    #     qa_results.append(qa_result)
    #
    # data_json['datas'] = qa_results
    # data_json['total'] = len(qa_results)
    #
    # #return HttpResponse(json.dumps(data_json))
    # return render(request,"QAManage.html",{'data_json':data_json})
    return render(request, "QAManage.html")
def Regsiter(request):
    return render(request,"register.html")
def Login(request):
    return render(request,"firstPage.html")
def Task(request):
    return render(request,"Taskscheduling.html")
def userMining(request):
    return render(request,"userMining.html")
def userPage(request):
    # if 'HTTP_X_FORWARDED_FOR' in request.META:
    #     ip = request.META['HTTP_X_FORWARDED_FOR']
    # else:
    #     ip = request.META['REMOTE_ADDR']
    # 设置session保存上一轮的question
    request.session['question'] = ''
    # 存入日志
    # logger.info('访问者IP：' + ip)

    return render(request,"UserPage.html")
def upload(request):
    if request.method == 'POST':
        #file_obj = request.FILES.get('fileupload')
        file_obj = request.FILES['file']
        # 这里一开始写反了
        BASE_DIR = os.path.abspath(os.path.dirname(__file__))


        f = open(os.path.join(BASE_DIR, 'static', 'document', file_obj.name), 'wb+')

        # 存入日志
        # logger.info(file_obj.name)
        # print(file_obj,type(file_obj))
        for chunk in file_obj.chunks():
            f.write(chunk)
        f.close()
        success={'success':'OK'}
        return HttpResponse(json.dumps(success),content_type="application/json")

def search_all(request):
    if request.method == 'POST':
        offset = request.POST.get("pageSize")
        limit = request.POST.get("pageIndex")
        qa_results = []
        data_json = {}
        withweb_all = Withweb_all()
        result = withweb_all.searchall(myindex)
        for i in range(len(result)):
            qa_result = {}
            qa_result['id'] = result[i]['_id']
            qa_result['question'] = result[i]['_source']['question']
            qa_result['answer'] = result[i]['_source']['answer']
            qa_result['link'] = result[i]['_source']['link']
            qa_result['subject'] = result[i]['_source']['subject']

            qa_results.append(qa_result)

        data_json['rows'] = qa_results[(int(limit)-1)*int(offset):int(limit)*int(offset)]
        data_json['total'] = len(qa_results)


        return HttpResponse(json.dumps(data_json))
    else:
        return HttpResponse("add wrong")

def Add(request):
    if request.method == 'POST':
        jsondata = request.POST.get("jsondata")
        received_json_data = json.loads(jsondata)
        id = received_json_data['ID']
        question = received_json_data['Question']
        answer = received_json_data['Answer']
        link = received_json_data['Link']
        subject = received_json_data['Subject']

        sim_ques1 = ''
        sim_ques2 = ''
        # 存入日志
        # logger.info(received_json_data)

        withweb_all = Withweb_all()
        result = withweb_all.webinsert(myindex,question,question,answer,link,subject,id,sim_ques1,sim_ques2)

        # print(result)
        return HttpResponse("add ok")
    else:
        return HttpResponse("add wrong")

def modify(request):
    if request.method == 'POST':
        jsonchangeddata = request.POST.get("jsondata")
        received_json_changed_data = json.loads(jsonchangeddata)
        id = received_json_changed_data['ID']
        question = received_json_changed_data['Question']
        answer = received_json_changed_data['Answer']
        link = received_json_changed_data['Link']
        subject = received_json_changed_data['Subject']

        sim_ques1 = ''
        sim_ques2 = ''

        # 存入日志
        # logger.info(received_json_changed_data)

        #print(id,question,answer,link,subject)
        withweb_all = Withweb_all()

        withweb_all.update(myindex,question,answer,link,subject,id,sim_ques1,sim_ques2,0,0)

        return HttpResponse("modify ok")
    else:
        return HttpResponse("modify wrong")

def search(request):
    if request.method=='POST':
        search_id = request.POST.get("search_id")
        search_question = request.POST.get("search_question")
        qa_results = []
        data_json = {}
        withweb_all = Withweb_all()

        if search_question !='':
            print('标题为不空')

        if search_id != '' and search_question == '':
            result = withweb_all.search_by_id(myindex, search_id)

        elif search_question != '':
            result = withweb_all.search_by_question(myindex, search_question)
            print(result)

        for i in range(len(result)):
            qa_result = {}
            qa_result['id'] = result[i]['_id']
            qa_result['question'] = result[i]['_source']['question']
            qa_result['answer'] = result[i]['_source']['answer']
            qa_result['link'] = result[i]['_source']['link']
            qa_result['subject'] = result[i]['_source']['subject']

            qa_results.append(qa_result)

        data_json['rows'] = qa_results
        data_json['total'] = len(qa_results)

        # 存入日志
        # logger.info(data_json)

        return HttpResponse(json.dumps(data_json))


def delete(request):
    if request.method=='POST':
        delKey = request.POST.get("del_key")
        json_key = json.loads(delKey)
        withweb_all = Withweb_all()
        for key in json_key:
            withweb_all.single_delete(myindex, key)

        return HttpResponse("del OK")
    else:
        return HttpResponse("del error")

def userQuestion(request):
    if request.method=='POST':
        user_question = request.POST.get("userQuestion")


        # 获取本地时间
        Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        #print(Time)
        uq = {'userquestion':user_question,'question_time':Time}

        # 存入日志
        # logger.info(uq)
        User.objects.create(**uq)
        return HttpResponse("数据库保存成功")

# def Associate(request):
#     if request.method=='POST':
#         userimagine = request.POST.get("userImagine")
#         imgAnswer1 = "Imgine1"
#         imgAnswer2 = "Imgine2"
#         imgAnswer3 = "Imgine3"
#         imgAnswer4 = "Imgine4"
#         imgAnswer5 = "Imgine5"
#         return HttpResponse(json.dumps({
#             'imgA1':imgAnswer1,
#             'imgA2':imgAnswer2,
#             'imgA3':imgAnswer3,
#             'imgA4':imgAnswer4,
#             'imgA5':imgAnswer5
#         }))
#     else:
#         return HttpResponse("imagine false")

# def usermayask(request):
#     if request.method=='POST':
#         mayask1 = "ask1"
#         mayask2 = "ask2"
#         mayask3 = "ask3"
#         mayask4 = "ask4"
#         mayask5 = "ask5"
#         return HttpResponse(json.dumps({
#         'mayask1':mayask1,
#         "mayask2":mayask2,
#         "mayask3":mayask3,
#         "mayask4":mayask4,
#         "mayask5":mayask5
#     }))
#     else:
#         return HttpResponse("mayask false")

# 这个是用户的补完查询，当用户开始输入字的时候，调用补完查询
# 返回查询的准确问题
def completion_search(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']

    if request.method == 'POST':
        user_question = request.POST.get("completion_Question")
        #print(user_question)
        withweb = Withweb(ip)
        ques_before = request.session.get('question', default='')
        questions = withweb.buwan_search(myindex,user_question,ques_before)
        #print(questions)
        # 答案字典
        ques_dict = {}
        if questions != None:# 答案不为空
            for i in range(len(questions)):
                ques_dict['question' + str(i)] = questions[i]
            result_json = json.dumps(ques_dict)
        #return HttpResponse(result_json)
        else:
            result_json = json.dumps({
                'result1': ''
            })
        #return HttpResponse("imagine false")
        # 存入日志
        # for value in ques_dict.values():
        #     logger.info('补全查询输入问题：' + user_question + '|||' + '补全查询返回结果：' + value)
        return HttpResponse(result_json)



userin = "提问"

def Changing_intent(request):

    if request.method == 'POST':
            global userin
            # 解析请求体中的JSON数据
            data = json.loads(request.body.decode('utf-8'))
            # 获取传递过来的参数值
            new_param_value = data.get('param')
            userin = new_param_value
            print(userin)
            return HttpResponse("意图已更新")


# 用户点击的发送按钮的查询
# 返回的结果分为两种，第一种是当某一个答案的评分超过其他几个答案的评分，那么就返回一个
# 如果评分相同，那么就返回五个
def enter_search(request):
    global userin

    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']

    isclear = 4
    result_json = json.dumps({
        "isclear": isclear,
        "answer": "QAQ 小Q没明白您的意思,您可以尝试使用GLM Chat来进行解答",
        "userintent": userin
    })
    if request.method == 'POST':
        user_question = request.POST.get("enter_Question")
        print(user_question)
        # headers = {
        #     # Request headers
        #     'Ocp-Apim-Subscription-Key': '3d5f8b1b8a5f4adeaf0a5646fd2634c1',
        # }
        #
        # params = urllib.parse.urlencode({
        #     # Query parameter
        #     'q': user_question,
        #     # Optional request parameters, set to default values
        #     'timezoneOffset': '0',
        #     'verbose': 'true',
        # })
        # r = requests.get(
        #     'https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/5f7d357a-7c28-4891-b4dc-d810f8b564ef',
        #     headers=headers, params=params)
        # res = r.json()
        # maxscore = 0
        # for intent in res["intents"]:
        #     if (intent["score"] >= maxscore):
        #         maxscore = intent["score"]
        #         userintent = intent["intent"]
        userintent = userin
        if userintent == "闲聊":
            # 存入数据库中
            usermsg = {}
            usermsg['userip'] = ip
            usermsg['userquestion'] = request.POST.get("enter_Question")
            usermsg['usersub'] = '闲聊'
            usermsg['userattention'] = '闲聊'
            # usermsg['usercollect'] = usercollect
            # usermsg['userlike'] = random.randint(1,5)

            # 获取本地时间
            Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            usermsg['times'] = Time

            UserMining.objects.create(**usermsg)

            client = ZhipuAI(api_key="95219202fb04d73e99d52dd8ba71a582.WKLZ1g8XB6HaHatC")  # 请填写您自己的APIKey

            response = client.chat.asyncCompletions.create(
                model="glm-4",  # 填写需要调用的模型名称
                messages=[
                    {
                        "role": "user",
                        "content": request.POST.get("enter_Question")
                    }
                ],
            )
            task_id = response.id
            task_status = ''
            get_cnt = 0
            result_response = None

            while task_status != 'SUCCESS' and task_status != 'FAILED' and get_cnt <= 40:
                result_response = client.chat.asyncCompletions.retrieve_completion_result(id=task_id)
                print(result_response)
                task_status = result_response.task_status
                time.sleep(2)
                get_cnt += 1


            # # # 将结果转为字符串
            # result_response = str(result_response)
            # # # 删除字符串中的单引号
            # # # result_response = result_response.replace("'", "\"")
            # # # 解析 JSON 字符串
            # # # res = json.loads("{" + result_response + "}")
            # res = json.loads(result_response)

            def async_completion_to_dict(completion):
                result_dict = {
                    "id": completion.id,
                    "request_id": completion.request_id,
                    "model": completion.model,
                    "task_status": completion.task_status,
                    "choices": [],
                    "usage": {
                        "prompt_tokens": completion.usage.prompt_tokens,
                        "completion_tokens": completion.usage.completion_tokens,
                        "total_tokens": completion.usage.total_tokens
                    }
                }

                for choice in completion.choices:
                    choice_dict = {
                        "index": choice.index,
                        "finish_reason": choice.finish_reason,
                        "message": {
                            "content": choice.message.content,
                            "role": choice.message.role,
                            "tool_calls": choice.message.tool_calls
                        }
                    }
                    result_dict["choices"].append(choice_dict)

                return result_dict

            # 转换为字典
            completion_dict = async_completion_to_dict(result_response)
            # 转换为 JSON 字符串
            res = json.dumps(completion_dict)

            res = json.loads(res)
            if res:
                # error_code = res["intent"]["code"]
                #error_code = res["code"]
                if res['task_status'] == "SUCCESS":
                    # 成功请求
                    print(res['choices'][0]['message']['content'])
                    # res["result"]["values"]
                    result_json = json.dumps(
                        {
                            "isclear": isclear,
                            "answer": res['choices'][0]['message']['content'],
                            "userintent":userintent
                        })
                else:
                    print("%s" % (res['task_status']))
                    result_json = json.dumps(
                        {
                            "isclear": isclear,
                            "answer": "对不起，小Q出现了一点问题QAQ",
                            "userintent": userintent
                        })
            else:
                # print"request api error"
                result_json = json.dumps(
                    {
                        "isclear": isclear,
                        "answer": "error",
                        "userintent": userintent
                    })

        elif userintent == "提问":
            # user_question = request.POST.get("enter_Question")

            # print(user_question)
            withweb = Withweb(ip)

            # from QAManagement.ques_generate.saveines_test import save_test
            # save_test()


            ques_before = request.session.get('question', default='')
            # user_like = random.randint(1,5)
            # 获取本地时间
            Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            accurate_result = withweb.accurate_search(myindex, user_question,'k1_test','k2_test','提问',0.0,Time)


            if accurate_result != None:
                print(accurate_result)
                result_json = json.dumps({
                    'isclear': 1,
                    'answer': accurate_result,
                    "userintent": userintent
                })
                # return accurate_result
            else:
                ques_before = request.session.get('question', default='')
                # user_like = random.randint(1, 5)
                # 获取本地时间
                Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                result = withweb.enter_search(myindex, user_question,'k1_test','k2_test',ques_before,'提问',0.0,Time)
                # print(len(result))# 1-问题明确 2-问题模糊 3-问题极度模糊
                if len(result) == 5:  # 当用户问的不明确时，返回五个相似的问题
                    isclear = 2
                elif len(result) == 1:  # 当用户问题很明确的时候，返回一个明确的答案
                    isclear = 1
                ques_dict = {}
                if (isclear == 1):
                    question_time_today = datetime.date.today()
                    question_time_now = time.strftime(" %H:%M:%S")
                    Time = str(question_time_today) + question_time_now

                    uq = {'userquestion': user_question, 'question_time': Time}
                    User.objects.create(**uq)
                    # 设置session
                    request.session['question'] = user_question

                    result_json = json.dumps({
                        "isclear": isclear,
                        "answer": result[0],
                        "userintent": userintent
                    })
                elif (isclear == 2):
                    # 模糊问题
                    for i in range(len(result)):  # 这里返回的是五个相似的问题
                        ques_dict['question' + str(i)] = result[i]
                    ques_dict['isclear'] = 'isclear'
                    result_json = json.dumps(ques_dict)
                elif (isclear == 3):
                    result_json = json.dumps({
                        "isclear": isclear,
                        "answer": "对不起，匹配失败",
                        "userintent": userintent
                    })

        else:
            result_json = json.dumps({
                "isclear": isclear,
                "answer": "QAQ 小Q没明白您的意思,您可以尝试使用GLM Chat来进行解答",
                "userintent": userintent
            })

    # 这个地方会报异常AttributeError: 'AttributeError' object has no attribute 'errno' 很迷。。。
    # except Exception as e:
    #     print("[Errno {0}] {1}".format(e.errno, e.strerror))

    # if isclear == 2:
    #     for value in ques_dict.values():
    #         logger.info('点击发送按钮输入：' + user_question + "|||" + '返回相似问题：' + value)
    # else:# 存入日志
    #     logger.info('点击发送按钮输入：' + user_question + "|||" + '返回结果：' + json.loads(result_json)['answer'])
    return HttpResponse(result_json)

# 用户选择完问题的精确搜索
def accurate_search(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']

    if request.method == 'POST':
        user_question = request.POST.get("accurate_Question")
        # print('用户问题'+user_question)
        ques_before = request.session.get('question', default='')
        withweb = Withweb(ip)
        # user_like = random.randint(1, 5)
        # 获取本地时间
        Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        answer = withweb.accurate_search(myindex, user_question, 'k1_test', 'k2_test', '提问',0.0,
                                         Time)
        print(answer)
        # 设置session保存上一轮的question
        request.session['question'] = user_question
        # answer = withweb.accurate_search(myindex, user_question)
        #print(answer)
        # 存入日志
        # logger.info('精确搜索输入：' + user_question + '|||' + '回复答案：' + answer.strip())
        return HttpResponse(answer)

# 当用户提问完问题后，调用推荐提问
# 根据用户提出的问题，查询相似的问题，返回给用户
def further_search(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']

    if request.method == 'POST':
        user_question = request.POST.get("accurate_Question")
        withweb = Withweb(ip)
        ques_before = request.session.get('question', default='')
        questions = withweb.further_search(myindex, user_question,ques_before)
        #print(questions)
        ques_dict = {}
        if len(questions) > 0:  # 返回的推荐问题的数目不为空
            for i in range(len(questions)):
                ques_dict['question' + str(i)] = questions[i]
            result_json = json.dumps(ques_dict)
        else:
            result_json = ''

        # 存入日志

        # for value in ques_dict.values():
        #     logger.info('推荐问题输入：' + user_question + '|||' + '返回：' + value)
        return HttpResponse(result_json)

def usermayask(request):
    if request.method=='POST':
        questions_dict = {}
        questions = QuestionCount.objects.all()
        i = 0
        for question in questions:
            questions_dict['mayask'+ str(i)] = question.userquestion
            questions_dict['count' + str(i)] = question.questioncount
            i = i + 1
        return HttpResponse(json.dumps(questions_dict))

# 聊天系统 没有集成是个假的
# def chat(request):
#     if request.method=='POST':
#         question = request.POST.get("enter_Question")
#         if question == '你好':
#             result = "好啊，吃了么"
#         elif question == 'QAQ':
#             result = '怎么了'
#         elif question == '很差劲':
#             result = '很抱歉没有帮到您'
#         elif question == '很棒':
#             result = '很有幸为您带来了帮助'
#         return HttpResponse(result)

# 运行算法程序
def Doexe(request):
    if request.method == 'POST':
        # 选择的解析模版
        modelName = request.POST.get("modelname")

        myextract = hauwei_extractor.Extract()
        QA_generate = QG_paragraph.Paragraph()

        json_paths = []

        global file_list
        print(file_list)

        for onehtml in file_list:

            onehtml = onehtml.strip("\"")

            # 基础文件系统
            BASE_DIR = os.path.abspath(os.path.dirname(__file__))
            # HTML上传的地址
            file_dir = os.path.join(BASE_DIR, 'static', 'document')

            mylink = onehtml

            onehtml = os.path.join(file_dir,mylink)

            onehtml = open(onehtml, 'r', encoding="utf-8")

            # 导出的文件名为，原文件名，后缀为json
            onejson = mylink.replace('.html','.json')

            json_dir = os.path.join(BASE_DIR, 'static', 'json')

            jsonpath = os.path.join(json_dir, onejson)

            try:
                # 首先解析HTML文件，返回生成的json的文件名
                jsonname = myextract.inserthtml(onehtml, jsonpath, mylink)  ######此处写入的是变量

                if jsonpath != None:
                    json_paths.append(jsonname)
            except sre_constants.error:
                continue

        print('jsonpath:'+str(json_paths))

        # 然后运行QA对生成函数
        result = QA_generate.main(json_paths)

        # 存入日志
        # logger.info(result)
        global result_list
        result_list = result
        # print(result)
        num = len(result)

        # 只有生成了QA对的时候才能存入
        # if num > 0:
        #     # 存入数据库中
        #     saveines = QA_save.SaveInEs()
        #     for res in result:
        #         saveines.main(myindex,res)

        # if fileName == '华为云网页抽取模版':
        # time.sleep(60)

        result_json = json.dumps({
            "num": num,
            "qa": result,
        })

        # i = 1
        # while i <= 10:
        #     i += 1
        #     time.sleep(1)  # 休眠1秒

        return HttpResponse(result_json)
    else:
        return HttpResponse("失败")
#生成的QA对修改操作
def modifyQAres(request):
    if request.method=="POST":
        resultdict = {}
        saveines = QA_save.SaveInEs()
        #获取修改了的数据
        mres = request.POST.get("jsondata")
        mres = json.loads(mres)
        print(mres["泛化句子"]+"ssssss")
        resultdict["question"] = mres["问题"]
        resultdict["subject"] = mres["主题"]
        resultdict["answer"] = mres["答案"]
        resultdict["answer_link"] = mres["文件链接"]
        simdict = {}
        simwords = mres["泛化句子"].strip().split("  ")

        simdict["sim_ques1"] = simwords[0]
        simdict["sim_ques2"] = simwords[1]
        print(simdict["sim_ques1"]+"     "+simdict["sim_ques2"])
        resultdict["answer_fan"] = simdict
        print("QAreas"+str(resultdict))
        # 将修改了的数据存入数据库
        saveines.main(myindex, resultdict)

        return HttpResponse("保存修改数据成功")

    else:
        return HttpResponse("存入失败")
#生成的QA对存入数据库操作
def saveQA(request):
    if request.method == "POST":
        result_list = request.POST.get("jsondata")
        print('保存结果'+str(result_list))
        num = len(result_list)
        # 只有生成了QA对的时候才能存入
        if num > 0:
            # 存入数据库中
            saveines = QA_save.SaveInEs()
            for res in result_list:
                print(res)
                saveines.main(myindex,res)
            return HttpResponse("存入成功，存入的QA对个数为："+str(num))
        else:
            return HttpResponse("QA对个数为："+str(num))
    else:
        return HttpResponse("存入失败")
# 获取在服务器上的文件名
def getfilename(request):
    if request.method == "POST":
        BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        file_dir = os.path.join(BASE_DIR, 'static', 'document')
        print(file_dir)
        for root, dirs, files in os.walk(file_dir):
            # print(root) #当前目录路径
            # print(dirs) #当前路径下所有子目录
            fileName = files  # 当前路径下所有非目录子文件
        return HttpResponse(json.dumps({
            "filenum": fileName.__len__(),
            "filename": fileName
        }))
# 更改文件名
def filerename(request):
    if request.method == "POST":
        filerenameArray = request.POST.get("unablefile")
        filerenameArray = filerenameArray.strip(']')
        filerenameArray = filerenameArray.strip('[')
        fileArray = filerenameArray.split(',')
        print(fileArray)
        BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        file_dir = os.path.join(BASE_DIR, 'static', 'document')
        for root, dirs, files in os.walk(file_dir):
            # print(root) #当前目录路径
            # print(dirs) #当前路径下所有子目录
            fileName = files  # 当前路径下所有非目录子文件
        for unablefile in fileArray:
            unablefile = unablefile.strip('"')
            print(unablefile)
            for temp in fileName:
                print(temp)
                print(op.eq(temp, unablefile))
                if(op.eq(temp,unablefile)):
                    newname = '(已生成)'+ temp
                    os.rename(file_dir+"/"+temp,file_dir+"/"+newname)
        return HttpResponse("rename ok")

# 选择文件
def choose_file(request):
    if request.method == 'POST':

        # file_list = []
        fileName = request.POST.get("filename")

        global file_list

        file_list = []

        file_list = fileName.strip("[").strip("]").split(',')
        # print(file_list)
    return HttpResponse(json.dumps({
        "filenum": file_list.__len__(),
        "filename": file_list
    }))

# 显示生成的QA对页面
def show_result(request):
    global result_list
    temporary = Temporary()
    for res in result_list:
        res['generalization'] = []
        res['generalization'] = temporary.main(res['question'])

    # print(result_list)
    global file_list

    return render(request, "show_result.html", {"result_list":result_list,'length':len(file_list),'files':file_list})

# 创建模版来生成QA对
def create_model(request):
    if request.method == 'POST':
        data = request.POST.get("createdata")
        data = json.loads(data)
        begintitle = data["begintitle"]
        endtitle = data["endtitle"]
        littlebegintitle = data["littlebegintitle"]
        littleendtitle = data["littleendtitle"]
        tabbegin = data["tabbegin"]
        tabend = data["tabend"]
        imgbegin = data["imgbegin"]
        imgend = data["imgend"]
        topicalbegin = data["topicalbegin"]
        topicalend = data["topicalend"]
        description = data["description"]

        # print(data)

        myextract = moban_extractor.Extract(tabbegin,tabend,imgbegin,imgend,begintitle,endtitle,littlebegintitle,littleendtitle,topicalbegin,topicalend,description)

        QA_generate = QG_paragraph.Paragraph()

        json_paths = []

        global file_list
        print(file_list)

        for onehtml in file_list:

            onehtml = onehtml.strip("\"")

            # 基础文件系统
            BASE_DIR = os.path.abspath(os.path.dirname(__file__))
            # HTML上传的地址
            file_dir = os.path.join(BASE_DIR, 'static', 'document')

            mylink = onehtml

            onehtml = os.path.join(file_dir, onehtml)

            onehtml = open(onehtml, 'r', encoding="utf-8")

            # 导出的文件名为，原文件名，后缀为json
            onejson = mylink.replace('.html', '.json')

            json_dir = os.path.join(BASE_DIR, 'static', 'json')

            jsonpath = os.path.join(json_dir, onejson)

            try:
                # 首先解析HTML文件，返回生成的json的文件名
                jsonpath = myextract.inserthtml(onehtml, jsonpath, mylink)  # 此处写入的是变量

                if jsonpath != None:
                    json_paths.append(jsonpath)
            except sre_constants.error:
                continue

        print('jsonpath:' + str(json_paths))

        # 然后运行QA对生成函数
        result = QA_generate.main(json_paths)

        # 存入日志
        # logger.info(result)

        global result_list
        result_list = result
        # print(result)
        num = len(result)

        # 只有生成了QA对的时候才能存入
        if num > 0:
            # 存入数据库中
            saveines = QA_save.SaveInEs()
            for res in result:
                saveines.main(myindex,res)

        # if fileName == '华为云网页抽取模版':
        # time.sleep(60)

        result_json = json.dumps({
            "num": num,
            "qa": result,
        })

        return HttpResponse(result_json)
    else:
        return HttpResponse("失败")

import datetime
import random
from datetime import datetime, timedelta
# 在用户信息首页展示所有用户信息的页面
def search_users_all(request):
    if request.method == 'POST':
        offset = request.POST.get("pageSize")
        limit = request.POST.get("pageIndex")
        users = []
        data_json = {}
        result_c = UserMining.objects.all()

        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 4, 30)

        # for obj in result_c:
        #     obj.usercollect = random.choice(['Yes', 'No'])
        #     if obj.id % 3 == 0:
        #         obj.userip = '192.168.10.1'
        #         random_date = start_date + timedelta(
        #             days=random.randint(0, (end_date - start_date).days),
        #             hours=random.randint(0, 23),
        #             minutes=random.randint(0, 59),
        #             seconds=random.randint(0, 59)
        #         )
        #         obj.times = random_date
        #         obj.save()

        #     if obj.id % 4 == 0:
        #         obj.userip = '192.168.10.2'
        #         random_date = start_date + timedelta(
        #             days=random.randint(0, (end_date - start_date).days),
        #             hours=random.randint(0, 23),
        #             minutes=random.randint(0, 59),
        #             seconds=random.randint(0, 59)
        #         )
        #         obj.times = random_date
        #         obj.save()
        #     obj.save()

        result = UserMining.objects.all().order_by('times')
        for i in range(len(result)):
            user = {}
            user['userip'] = result[i].userip
            user['userquestion'] = result[i].userquestion
            user['usersub'] = result[i].usersub
            user['userattention'] = result[i].userattention
            user['usercollect'] = result[i].usercollect
            user['userlike'] = result[i].userlike
            user['times'] = result[i].times

            users.append(user)

        data_json['rows'] = users[(int(limit)-1)*int(offset):int(limit)*int(offset)]
        data_json['total'] = len(users)


        return HttpResponse(json.dumps(data_json))
    else:
        return HttpResponse("add wrong")
# 查询用户
def searchuser(request):
    if request.method=='POST':
        offset = request.POST.get("pageSize")
        limit = request.POST.get("pageIndex")
        search_id = request.POST.get("search_id")
        search_sub = request.POST.get("search_sub")
        users = []
        data_json = {}
        result = []

        if search_id != '' and search_sub == '':
            result = UserMining.objects.filter(userip=search_id).order_by('times')

        elif search_id != '' and search_sub != '':
            result = UserMining.objects.filter(userip=search_id).filter(usersub=search_sub).order_by('times')
        elif search_id == '' and search_sub != '':
            result = UserMining.objects.filter(usersub=search_sub).order_by('times')

        for i in range(len(result)):
            user = {}
            user['userip'] = result[i].userip
            user['userquestion'] = result[i].userquestion
            user['usersub'] = result[i].usersub
            user['userattention'] = result[i].userattention
            user['usercollect'] = result[i].usercollect
            user['userlike'] = result[i].userlike
            user['times'] = result[i].times

            users.append(user)

        data_json['rows'] = users[(int(limit) - 1) * int(offset):int(limit) * int(offset)]
        data_json['total'] = len(users)

        # 存入日志
        # logger.info(data_json)

        return HttpResponse(json.dumps(data_json))


# 展示单个用户的提问情况
def search_single_user(request):
    if request.method == 'POST':
        # 获取用户IP
        userip = request.POST.get("userip")
        offset = request.POST.get("pageSize")
        limit = request.POST.get("pageIndex")
        users = []
        data_json = {}
        # 按时间排序
        result = UserMining.objects.filter(userip=userip).order_by('times')
        for i in range(len(result)):
            user = {}
            user['userip'] = result[i].userip
            user['userquestion'] = result[i].userquestion
            user['usersub'] = result[i].usersub
            user['userattention'] = result[i].userattention
            user['userlike'] = result[i].userlike
            user['usercollect'] = result[i].usercollect
            user['times'] = result[i].times

            users.append(user)

        data_json['rows'] = users[(int(limit)-1)*int(offset):int(limit)*int(offset)]
        data_json['total'] = len(users)


        return HttpResponse(json.dumps(data_json))
    else:
        return HttpResponse("add wrong")


# 访问个人用户画像
def userGrah(request):
    if request.method == 'GET':
        userip = request.GET.get("userip")

        # print('ip:' + userip)

        # return HttpResponseRedirect('')

        # return render_to_response("userGrah.html")
        return render(request, "userGrah.html", {"userip": userip})

# 用户个人画像兴趣饼图
def usersub(request):
    # 这个是用来查询该用户查询主题的占比
    if request.method == 'POST':
        # 获取用户IP
        userip = request.POST.get("userip")
        data_json = []

        # 查询主题
        query = UserMining.objects.filter(userip=userip).values('usersub').annotate(count=Count('usersub')).values('usersub',
                                                                                                                   'count')
        subcount_list = list(query)
        # 对统计好出现次数的主题进行排序
        subcount_sort = sorted(subcount_list, key=lambda e: e.__getitem__('count'), reverse=True)

        for sub in subcount_sort:
            if sub['usersub'] != '闲聊':
                result = {}
                result['name'] = sub['usersub']
                result['value'] = int(sub['count'])

                data_json.append(result)
        if len(data_json) <= 5:
            return HttpResponse(json.dumps(data_json))
        else:
            return HttpResponse(json.dumps(data_json[:5]))

# 用户个人画像意向饼图
def userattention(request):
    if request.method == 'POST':
        # 获取用户IP
        userip = request.POST.get("userip")
        data_json = []

        # 查询意向
        query = UserMining.objects.filter(userip=userip).values('userattention').annotate(count=Count('userattention')).values('userattention','count')

        subattention_list = list(query)

        # print(subattention_list)
        for subattention in subattention_list:
            result = {}
            result['name'] = subattention['userattention']
            result['value'] = subattention['count']
            data_json.append(result)

        return HttpResponse(json.dumps(data_json))

# 用户提问时间分布表
def questionnum(request):
    gettime = GetTimeBeforeToday.GetTime()
    onedaybefore = str(gettime.get_days_before_today(1))
    oneweekbefore = str(gettime.get_weeks_before_tody(1))
    onemonthbefore = str(gettime.get_months_before_tody(1))

    if request.method == 'POST':
        # 时间类别（月，周，天）
        timetype = request.POST.get('Numtype')
        # 用户IP
        userip = request.POST.get('userip')
        # 如果是按周来分布的话
        time_array = time.localtime(time.time())
        today = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        if timetype == 'week':
            # 近一周
            # 按时间排序
            result = UserMining.objects.filter(userip=userip).order_by('times')
            # 返回数据
            data_json = {}
            # 每天的问题个数
            Mondaynum = 0
            Tuesdaynum = 0
            Wednesdaynum = 0
            Thursdaynum = 0
            Fridaynum = 0
            Saturdaynum = 0
            Sundaynum = 0
            weekday_list = ['周一','周二','周三','周四','周五','周六','周日']
            week_data = []
            for res in result:
                # 进行一周的时间比较，判断在一周内的时间
                # 时间的判断只需要进行字符串的大小比较即可，字符串通过ASCII码进行比较
                # 因为res.times本来就已经被排序过了，所以直接存入数组中即可
                if res.times > oneweekbefore:
                    # 获取这个时间是星期几
                    weekday = int(datetime.datetime.fromtimestamp(time.mktime(time.strptime(res.times, '%Y-%m-%d %H:%M:%S'))).weekday())
                    # 一周内每天的统计
                    if weekday == 0:
                        Mondaynum += 1
                    elif weekday == 1:
                        Tuesdaynum += 1
                    elif weekday == 2:
                        Wednesdaynum += 1
                    elif weekday == 3:
                        Thursdaynum += 1
                    elif weekday == 4:
                        Fridaynum += 1
                    elif weekday == 5:
                        Saturdaynum += 1
                    elif weekday == 6:
                        Sundaynum += 1

            for day in gettime.dateRange(oneweekbefore,today,n=1):
                weekday = int(datetime.datetime.fromtimestamp(
                    time.mktime(time.strptime(day, '%Y-%m-%d'))).weekday())
                data = {}
                data['date'] = day
                data['weekday'] = weekday_list[weekday]
                if weekday == 0:
                    data['num'] = Mondaynum
                elif weekday == 1:
                    data['num'] = Tuesdaynum
                elif weekday == 2:
                    data['num'] = Wednesdaynum
                elif weekday == 3:
                    data['num'] = Thursdaynum
                elif weekday == 4:
                    data['num'] = Fridaynum
                elif weekday == 5:
                    data['num'] = Saturdaynum
                elif weekday == 6:
                    data['num'] = Sundaynum

                week_data.append(data)
            # week_data 的格式 [{'date': '2018-08-16', 'weekday': '周四', 'num': 0},{}]
            # 传送过来的数据格式data
            # {“maxnum”：87，"minmun": 10, “datanum”：[["周一"，34]，["周二", 87]]}, 要传一个条数最大值与最小值好划分纵坐标
            # print(week_data)
            # 按照num排序，取出最大最小值
            week_data.sort(key=lambda k:list(k.values())[2],reverse=True)
            maxnum = week_data[0]['num']
            minnum = week_data[-1]['num']
            # 按时间排序
            week_data.sort(key=lambda k:list(k.values())[0],reverse=False)

            data_json['maxnum'] = maxnum
            data_json['minnum'] = minnum
            data_json['datanum'] = []
            data_json['date'] = []
            for i in week_data:
                datedata = []
                datedata.append(i['date'] + ' ' + i['weekday'])
                datedata.append(i['num'])
                data_json['datanum'].append(datedata)
                data_json['date'].append(i['date'] + ' ' + i['weekday'])

            print(data_json)

        elif timetype == 'month':
            # 返回数据集
            data_json = {}
            # 获取前一个月的时间，也就是30天
            result = UserMining.objects.filter(userip=userip).order_by('times')
            # 总共30天，五天一组，分为6组
            days_list = gettime.dateRange(onemonthbefore,today,n=5)
            days_num = [0, 0, 0, 0, 0, 0]

            for res in result:
                for i in range(len(days_list) -1 ):
                    if res.times > days_list[i] and res.times < days_list[i+1]:
                        # 计算问题次数
                        days_num[i] += 1
            data_json['datanum'] = []
            data_json['date'] = []
            for i in range(len(days_list) - 1):
                daydata = []
                daydata.append(days_list[i] + ' - ' + days_list[i+1])
                daydata.append(days_num[i])

                data_json['date'].append(days_list[i] + ' - ' + days_list[i+1])

                data_json['datanum'].append(daydata)

            # print(data_json)


        elif timetype == 'day':
            # {“datanum”：[["周一"，34]，["周二", 87]]}, 要传一个条数最大值与最小值好划分纵坐标
            data_json = {}
            # 近一天
            # 按时间排序
            result = UserMining.objects.filter(userip=userip).order_by('times')
            # 一天分为24小时，三小时为一组，共八组数据
            # 取出前一天按3小时分组的时间
            hours_list = gettime.hourRange(onedaybefore,today,n=3)
            hours_num = [0,0,0,0,0,0,0,0]
            for res in result:
                for i in range(len(hours_list) -1 ):
                    if res.times > hours_list[i] and res.times < hours_list[i+1]:
                        # 计算问题次数
                        hours_num[i] += 1
            data_json['datanum'] = []
            data_json['date'] = []
            for i in range(len(hours_list) - 1):
                daydata = []
                daydata.append(hours_list[i].split()[1] + ' - ' + hours_list[i+1].split()[1])
                daydata.append(hours_num[i])

                data_json['date'].append(hours_list[i].split()[1] + ' - ' + hours_list[i+1].split()[1])

                data_json['datanum'].append(daydata)

            # print(data_json)


        return HttpResponse(json.dumps(data_json))

def statistics():
    #print("do")
    # 批量清空
    cursor = connection.cursor()

    # Data modifying operation
    cursor.execute("delete from QAManagement_questioncount")
    # transaction.set_dirty()
    cursor.execute("alter table QAManagement_questioncount auto_increment=1")
    # 对用户问题出现的次数进行计数
    query = User.objects.all().values('userquestion').annotate(count=Count('userquestion')).values('userquestion', 'count')
    questioncount_list = list(query)
    # 对统计好出现次数的问题进行排序
    questioncount_sort = sorted(questioncount_list, key=lambda e: e.__getitem__('count'),reverse=True)
    i = 0
    # 出现次数最多的前五条插入数据库
    for qs in questioncount_sort:
        i = i+1
        #print(qs['count'])
        # if tempqc:
        #     tempqc.userquestion = qs['userquestion']
        #     tempqc.questioncount = qs['count']
        #     tempqc.save()
        # else:
        qc = {'userquestion': qs['userquestion'], 'questioncount': qs['count']}
        QuestionCount.objects.create(**qc)
        if(i==5):
            break
# 收藏功能
def collect(request):
    if request.method == 'POST':
        question = request.POST.get('collectquestion')  # 收藏问题
        iscollect = request.POST.get('iscollect')  # 收藏还是取消收藏
        print(iscollect)
        print(question)
        if iscollect:
            collecttemp = "是"
        else:
            collecttemp = "否"
        # 这个是有bug的存在，我是直接将最后一条插入的问题作为更改收藏的问题
        result = UserMining.objects.last()
        # 然后将所有的这个ip下的所有的这个问题改成这个评分
        UserMining.objects.filter(userquestion=result.userquestion,userip=result.userip).update(usercollect=collecttemp)
        return HttpResponse("cllectOk")
    else:
        return HttpResponse("cllectwrong")
# 用户评分
def userscore(request):
    if request.method == 'POST':
        scoredata = request.POST.get("scoredata")
        scoredata = json.loads(scoredata)
        # print("ffff"+scoredata['likequestion'])
        # print("ffff"+scoredata['likescore'])
        # 把小傻子张同学的代码注释了，怎么能用答案去问题库里匹配呢？
        # result = UserMining.objects.filter(userquestion=scoredata['likequestion']).update(userlike=float(scoredata['likescore']))

        # 这个是有bug的存在，我是直接将最后一条插入的问题作为更改评分的问题
        result = UserMining.objects.last()
        # 然后将所有的这个ip下的所有的这个问题改成这个评分
        UserMining.objects.filter(userquestion=result.userquestion,userip=result.userip).update(userlike=float(scoredata['likescore']))

        return HttpResponse("scoreOk")
    else:
        return HttpResponse("scorewrong")


def Regsiter(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        retype_password = request.POST.get('retype_password')
        agree_terms = request.POST.get('agree_terms')

        # 进行必要的验证和处理
        if password != retype_password:
            # 密码不一致的处理逻辑
            pass

        if not agree_terms:
            # 未同意服务条款的处理逻辑
            pass
        # 创建新用户
        user = NewUser(first_name=first_name, last_name=last_name, email=email, gender=gender, password=password)
        user.save()
        success_message = "注册成功！"
        return render(request, "register.html", {'success_message': success_message})
    return render(request, "register.html")

def Login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email,password)
        try:
            user = NewUser.objects.get(email=email)
            if user.password == password:
                return JsonResponse({'success': True, 'redirect_url': '/userPage/'})
            else:
                return JsonResponse({'success': False, 'message': '邮箱或密码错误！'})
        except NewUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': '用户不存在，请注册！'})
    return render(request, "register.html")


scheduler = BackgroundScheduler()# 后台运行
scheduler.add_job(statistics, 'interval', seconds=2)
scheduler.start()    # 这里的调度任务是独立的一个线程
