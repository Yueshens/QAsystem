
# 标点符号的拼接测试

a = "行车 记录仪 什么 牌子 好 ' ？ "
words_list = a.split(' ')
question = ''

for word in words_list:
    if word == "'":
        print('单引号')
        question += "/'" + ' '
    elif word == '"':
        print('双引号')
        question += '/"'
    else:
        question += word + ' '

print(question)