import pandas as pd
import requests
import re
from time import sleep
from tqdm import tqdm  # 进度条库

from PyDictionary import PyDictionary
dictionary = PyDictionary()

def translate_word(word):
    """使用有道词典API获取准确中文释义"""
    # 有道词典API参数
    url = 'https://fanyi.youdao.com/translate'
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'i': word,
        'from': 'AUTO',
        'to': 'AUTO',
        'doctype': 'json'
    }

    try:
        response = requests.post(url, headers=headers, data=data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            # 解析有道返回结果
            if 'translateResult' in result:
                translations = []
                for item in result['translateResult'][0]:
                    if 'tgt' in item:
                        translations.append(item['tgt'])
                if translations:
                    return "；".join(translations)
        return "未找到释义"
    except Exception as e:
        print(f"翻译'{word}'时出错: {str(e)}")
        return "翻译服务暂时不可用"
    
# 在process_excel函数中添加重试机制
MAX_RETRIES = 3

def process_excel(input_path, output_path):
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            # 原有处理逻辑...
            break
        except requests.exceptions.RequestException:
            retry_count += 1
            print(f"网络错误，正在重试({retry_count}/{MAX_RETRIES})...")
            sleep(2)

def extract_words(text):
    """改进的单词提取，支持更多格式"""
    # 匹配英文单词(包括带连字符的)
    words = re.findall(r'\b[a-zA-Z]+(?:-[a-zA-Z]+)*\'?s?\b', str(text))
    return [w.lower() for w in words if len(w) > 1]  # 过滤单个字母

def process_excel(input_path, output_path):
    try:
        # 读取Excel所有工作表
        xls = pd.ExcelFile(input_path)
        all_words = []
        
        # 处理每个工作表
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            # 提取所有单元格中的单词
            for col in df.columns:
                for cell in df[col]:
                    all_words.extend(extract_words(cell))
        
        # 去重排序
        unique_words = sorted(set(all_words), key=lambda x: x.lower())
        print(f"共提取到 {len(unique_words)} 个唯一单词")
        
        # 翻译(带进度条)
        translations = []
        for word in tqdm(unique_words, desc="翻译进度"):
            translations.append(translate_word(word))
        
        # 创建DataFrame并保存
        result = pd.DataFrame({
            'English': unique_words,
            'Chinese': translations
        })
        
        # 保存到新Excel文件
        with pd.ExcelWriter(output_path) as writer:
            result.to_excel(writer, index=False, sheet_name='中英对照')
        
        print(f"处理完成！结果已保存到: {output_path}")
    
    except Exception as e:
        print(f"处理出错: {str(e)}")
        print("常见问题：1.文件被占用 2.网络问题 3.Excel格式异常")

if __name__ == "__main__":
    # 安装依赖：python -m pip install pandas openpyxl requests tqdm
    input_file = r'e:\autotools\ai-class\KET单词册.xlsx'
    output_file = r'e:\autotools\ai-class\KET单词表(中英对照).xlsx'
    process_excel(input_file, output_file)