
# 相似度计算的测试
from QAManagement.question_generalization.similarity import Similarity
import time

similarity = Similarity()

question = '入党 积极分子 的 培养 联系人 什么时候 确定 ？'

model_list = ['入党 积极分子 的 培养 联系人 什么时候 确定 ？','护卫队 到底 什么时候 在 中国 上映 ？','鹅 为什么 看见 人 会 攻击 ？','鬼谷子 和 诸葛亮 到底 谁 厉害 ？','确定 为 入党 积极分子 的 时间 是 什么时候 ？']

result = similarity.main(question,model_list)

print(result)
