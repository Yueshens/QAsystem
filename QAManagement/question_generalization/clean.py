

import os
from pyltp import Segmentor
from pyltp import SentenceSplitter


# 问句清洗
class Clean():


    LTP_DATA_DIR = 'ltp_data_v3.4.0/'  # ltp模型目录的路径
    cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
    segmentor = Segmentor(cws_model_path)  # 初始化实例


    # 读取疑问词
    ques_word_file = open('ltp_data_v3.4.0/question_word.txt', encoding='utf-8')
    ques_words_list = []
    for line in ques_word_file:
        ques_words_list.append(line.strip('\n'))

    # print(len(question_list))


    # 对问句进行清洗

    # 1.去重
    def repeat(self,question_list):

        result = list(set(question_list))
        result.sort(key=question_list.index)

        return result


    # 2.长度限制
    def length(self,question_list):

        result = []
        # 将句子长度小于3或者大于20的去掉
        for i in question_list:
            if len(i) > 3 and len(i) < 25:
                result.append(i)

        # print(len(second))
        return result

    # 3.疑问句判断
    # 判断输入的句子是否为问句 返回ture false
    # true为疑问句
    def is_ask_type(self, sentence):
        # 判断输入的是否为疑问句
        # 输出变量
        result = None
        words = Clean.segmentor.segment(sentence)  # 分词
        words_list = list(words)

        for i in words_list:
            # 根据句子末尾是否有问号，句子中是否有疑问词
            if i in Clean.ques_words_list or i == '？' or i == '?':
                result = True
                break
            else:
                result = False
        return result

    # 4.多句判断
    # 返回True和False，True为单句
    def is_multiple_sen(self,sentence):
        # 一个问句中可能有多个问句
        sents = SentenceSplitter.split(sentence)  # 分句

        if len(sents) == 1:
            return True
        else:
            return False

    # 5.给问句加标点
    def ques_punctuation(self, ques_sen):  # 问句的标点符号
        ques_sen = ques_sen.strip()
        # 判断问句的最后一位的标点
        if ques_sen[-1] in ['，', '。', '；','?','.',',']:  # 说明句子的最后一位是有标点的，但不是问号
            ques_sen = ques_sen[:-1] + '？'
        elif ques_sen[-1] not in ['，', '。', '？', '；', '！','.','!']:  # 句子最后没有标点结尾的
            ques_sen = ques_sen + '？'

        ques_sen = ques_sen.replace('\'','"')
        return ques_sen

    # 主函数
    def main(self,question_list):
        question_list = self.repeat(question_list)
        question_list = self.length(question_list)

        result = []
        for i in question_list:
            if self.is_ask_type(i):
                if self.is_multiple_sen(i):
                    result.append(self.ques_punctuation(i))

        return result







