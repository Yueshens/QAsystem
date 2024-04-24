

# 构建树的测试类
from QAManagement.question_generalization.templatetree import Templatetree

templatetree = Templatetree()



import os
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import Parser


ques_words_list = '数据 存储 在 DIS 和 OBS 有什么 区别 ？'.split()
ques_postags_list = 'n v p ws c ws list_ques n wp'.split()
ques_arcs_list = '2:SBV 0:HED 2:CMP 7:ATT 6:LAD 4:COO 3:POB 2:VOB 2:WP'.split()


model_words_list = 'redis 和 memcache 有 哪些 区别 ？'.split()
model_postags_list = 'ws c ws modal list_ques n wp'.split()
model_arcs_list = '4:SBV 3:LAD 1:COO 0:HED 6:ATT 4:VOB 4:WP'.split()


ques_tree = templatetree.create(words_list=ques_words_list,postags_list=ques_postags_list,arcs_list=ques_arcs_list)
model_tree = templatetree.create(words_list=model_words_list,postags_list=model_postags_list,arcs_list=model_arcs_list)

print(ques_tree)
print(model_tree)

print(templatetree.depth_first(ques_tree))
print(templatetree.depth_first(model_tree))
# ques_str = templatetree.depth_first(ques_tree)
# model_str = templatetree.depth_first(model_tree)

templatetree.matchandgenerate(question_tree=ques_tree,model_tree=model_tree)