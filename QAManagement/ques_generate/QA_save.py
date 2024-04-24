

from QAManagement.withweb_all import Withweb_all
class SaveInEs():
    withweb = Withweb_all()
    '''
        保存类的主函数
        输入：datatable 要存入的表名
        qa_list QA的列表
    '''
    def main(self,datatable,qa_list):
        # 在存入时，首先调用查询函数
        # 查看所有的总数
        search_result = self.check_database(datatable)
        num = search_result['max_id']
        questions = search_result['questions']
        # 查看是否有重复
        if qa_list['question'] not in questions:
            SaveInEs.withweb.webinsert(datatable, qa_list['question'], qa_list['question'], qa_list['answer'], qa_list['answer_link'],
                                   qa_list['subject'], num+1)




    # 查询有的es的表
    def check_database(self,datatable):
        # 返回值是一个list，包括所有的结果
        result = SaveInEs.withweb.searchall(datatable)
        # list的长度
        max_id = 0
        questions = []
        for i in result:
            questions.append(i['_source']['question'])
            if int(i['_id']) > max_id:
                max_id = int(i['_id'])
        search_result = {'max_id':max_id,'questions':questions}
        return search_result