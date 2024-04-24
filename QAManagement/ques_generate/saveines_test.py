

from QAManagement.ques_generate.QA_save import SaveInEs
from QAManagement.withweb_all import Withweb_all
import  xdrlib ,sys
from elasticsearch import Elasticsearch
import xlrd
import random

save = SaveInEs()
withweb = Withweb_all()


def open_excel(file):
    data = xlrd.open_workbook(file)
    return data

def excel_table_byname(file,colnameindex=0,by_name=u'Sheet1'):
     data = open_excel(file)
     table = data.sheet_by_name(by_name)
     nrows = table.nrows #行数
     colnames =  table.row_values(colnameindex) #某一行数据
     list =[]
     for rownum in range(1,nrows):
          row = table.row_values(rownum)
          if row:
              app = {}
              for i in range(len(colnames)):
                 app[colnames[i]] = row[i]
              list.append(app)
     return list

def save_test():
    result = excel_table_byname('G:\桌面\998\QAsystem\QAManagement\ques_generate\QA_pairs.xlsx',0,'Sheet1')

    # print(result)

    # withweb.webinit('qa_test')

    for qa_list in result:
        withweb.webinsert('qa_test', qa_list['标准问题'], qa_list['标准问题'], qa_list['答案'], qa_list['答案链接'],qa_list['主题'],int(qa_list['标准问题ID']),'','',random.randint(1, 300),round(random.uniform(0.5, 5.0), 1))


def clear_es():
    # 定义要删除文档的索引名称
    index_name = "qa_test"

    # 构建删除所有文档的查询
    query = {
        "query": {
            "match_all": {}
        }
    }

    try:
        # 使用 Delete By Query API 执行删除操作
        response = es.delete_by_query(index=index_name, body=query)

        # 打印删除操作的结果
        print("Deleted documents:", response["deleted"])

    except Exception as e:
        # 捕获可能的异常
        print(f"An error occurred: {e}")