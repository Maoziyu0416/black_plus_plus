import sys
import re
import json
import traceback

sinfo = len(sys.argv)

# 从 JSON 文件加载关键字映射表
with open('keyword_map.json', 'r', encoding='utf-8') as f:
    keyword = json.load(f)


def parse(code):
    def replace_keyword(match):
        # 获取匹配到的文本
        text = match.group(0)
        # 进行替换
        return keyword.get(text, text)  # 如果关键字存在于字典中，则替换，否则保留原文本

    # 使用正则避免替换字符串中的内容，注意全角符号也应被替换
    code = re.sub(
        r'(?<!")(\b(?:true|false|null|真|假|伪|类型|格式化字符串|空|类|\+\+|--|重复执行如果|重复遍历|属于|函数|导入|如果|否则如果|否则|作为|时间|系统|海龟|继承|初始化|输出|输入|￥￥|（|）|’|“|”|，|：|？|！)\b)(?!")',
        replace_keyword, code)

    # 额外处理没有被正则捕获的全角符号
    for key in keyword:
        code = code.replace(key, keyword[key])

    return code


run_type = 0
if sinfo == 1:
    print("参数错误，退出程序")
    sys.exit(0)
elif sinfo >= 3:
    if sys.argv[2] == 'compile':
        run_type = 1
    if sys.argv[2] == 'run':
        run_type = 2

file = sys.argv[1]

with open(file, 'r', encoding='utf-8') as f:
    original_code = f.read()  # 保存原始代码
    code = parse(original_code)  # 转换后的代码

if run_type == 2:
    try:
        exec(code)  # 直接运行转换后的 Python 代码
    except Exception as e:
        print("运行时错误")
        # 打印详细的错误堆栈信息
        traceback.print_exc()
        print("\n错误发生在原始代码中：\n")
        print(original_code)  # 输出原始代码，帮助定位
        sys.exit(255)
    sys.exit(0)

if run_type == 1:
    with open(file + '.class', 'w', encoding='utf-8') as f:
        f.write(code)
    sys.exit(0)

try:
    exec(code)
except Exception as e:
    print("运行时错误")
    # 打印详细的错误堆栈信息
    traceback.print_exc()
    print("\n错误发生在原始代码中：\n")
    print(original_code)  # 输出原始代码
