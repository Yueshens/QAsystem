from QAManagement.question_generalization.extract import Extract

extract = Extract()

question = 'cad为什么打开图形后文字都是问号？'
# type = 'why'
#
# result = extract.Pretreate(question,type)
# print(result)
#
# result1 = extract.compression(result[1])
# print(result1)

# extract.savedb(['1','2'],['a','b'],'how_long')
extract.main(question=question)
