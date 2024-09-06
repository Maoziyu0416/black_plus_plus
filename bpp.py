import sys
import re
import json
import traceback
import os

# 加载关键字映射表
with open('keyword_map.json', 'r', encoding='utf-8') as f:
    keyword = json.load(f)


def parse(code):
    # 处理自定义的 from module import function 语句
    code = re.sub(r'从\s+([a-zA-Z_]\w*)\s+导入\s+([a-zA-Z_]\w*)', r'load_specific_from_bpp_module("\1", "\2")', code)

    # 处理导入整个模块的情况
    code = re.sub(r'导入\s+([a-zA-Z_]\w*)', r'\1 = load_bpp_module("\1")', code)

    # 按照关键字长度从长到短排序，确保优先替换长的关键字
    for key in sorted(keyword.keys(), key=len, reverse=True):
        code = code.replace(key, keyword[key])

    return code


class ModuleNamespace:
    """将字典形式的命名空间转化为支持点操作的对象"""

    def __init__(self, namespace_dict):
        self.__dict__.update(namespace_dict)


def load_bpp_module(module_name):
    """导入 .bpp 文件，并转换为 Python 代码"""
    module_file = module_name + '.bpp'
    if not os.path.exists(module_file):
        raise ImportError(f"无法找到模块 {module_file}")

    with open(module_file, 'r', encoding='utf-8') as f:
        original_code = f.read()
        # 解析并转换为 Python 代码
        python_code = parse(original_code)

    # 执行转换后的 Python 代码，相当于导入模块
    module_namespace = {}
    try:
        exec(python_code, module_namespace)
    except Exception as e:
        print(f"导入模块 {module_name} 时发生错误：", e)
        traceback.print_exc()
        sys.exit(255)

    # 返回一个支持点操作的对象
    return ModuleNamespace(module_namespace)


def load_specific_from_bpp_module(module_name, item_name):
    """从 .bpp 文件中导入特定的函数或变量"""
    module_file = module_name + '.bpp'
    if not os.path.exists(module_file):
        raise ImportError(f"无法找到模块 {module_file}")

    with open(module_file, 'r', encoding='utf-8') as f:
        original_code = f.read()
        # 解析并转换为 Python 代码
        python_code = parse(original_code)

    # 执行转换后的 Python 代码，相当于导入模块
    module_namespace = {}
    try:
        exec(python_code, module_namespace)
    except Exception as e:
        print(f"导入模块 {module_name} 时发生错误：", e)
        traceback.print_exc()
        sys.exit(255)

    # 检查模块中是否存在指定的函数或变量
    if item_name not in module_namespace:
        raise ImportError(f"无法从模块 {module_name} 中找到 {item_name}")

    # 返回导入的特定函数或变量
    return module_namespace[item_name]


run_type = 0
sinfo = len(sys.argv)

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

# 处理运行类型
if run_type == 2:
    try:
        exec(code)  # 直接运行转换后的 Python 代码
    except Exception as e:
        print("运行时错误")
        traceback.print_exc()
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
    traceback.print_exc()
    sys.exit(255)
