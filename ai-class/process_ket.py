import pandas as pd
import requests
import time
import random
from tqdm import tqdm

def translate_word_mymemory(word):
    """使用MyMemory翻译API获取中文释义"""
    url = 'https://api.mymemory.translated.net/get'
    
    params = {
        'q': word,
        'langpair': 'en|zh',
        'de': 'nicalhu@tencent.com'  # 可选：添加邮箱以获得更高的使用限额
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result['responseStatus'] == 200:
            translation = result['responseData']['translatedText']
            # 清理翻译结果，移除可能的HTML标签和特殊字符
            translation = translation.replace('&quot;', '"').strip()
            return translation
            
    except Exception as e:
        print(f"翻译'{word}'时出错: {str(e)}")
        time.sleep(1)  # 出错时等待1秒
    return None

def process_ket_vocabulary(input_file, output_file):
    try:
        # 读取Excel文件的所有工作表
        print("正在读取KET单词册...")
        xls = pd.ExcelFile(input_file)
        all_words = []
        
        # 处理每个工作表
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            # 提取所有单元格中的英文单词
            for col in df.columns:
                words = df[col].dropna().astype(str)
                # 只保留纯英文单词（可以包含连字符和撇号）
                words = words[words.str.match(r'^[a-zA-Z]+(-[a-zA-Z]+)*\'?s?$')]
                all_words.extend(words.tolist())

        # 去重并排序
        unique_words = sorted(set(all_words), key=str.lower)
        print(f"共提取到 {len(unique_words)} 个唯一单词")

        # 翻译单词并显示进度条
        translations = []
        failed_words = []  # 记录翻译失败的单词
        
        print("正在翻译单词...")
        for word in tqdm(unique_words):
            translation = None
            # 尝试最多3次翻译
            for attempt in range(3):
                translation = translate_word_mymemory(word)
                if translation:
                    break
                time.sleep(random.uniform(2, 3))  # 重试前等待更长时间
            
            if translation:
                translations.append(translation)
            else:
                translations.append("翻译失败")
                failed_words.append(word)
            
            # 随机延时2-3秒，避免触发API限制
            time.sleep(random.uniform(2, 3))

        # 创建结果DataFrame
        result_df = pd.DataFrame({
            'English': unique_words,
            'Chinese': translations
        })

        # 保存到新Excel文件
        print(f"正在保存结果到 {output_file}...")
        result_df.to_excel(output_file, index=False)
        
        # 显示处理结果
        print("\n处理完成！")
        print(f"总单词数：{len(unique_words)}")
        print(f"成功翻译：{len(unique_words) - len(failed_words)}")
        if failed_words:
            print(f"翻译失败：{len(failed_words)} 个单词")
            print("翻译失败的单词：")
            for word in failed_words:
                print(f"- {word}")
        
        # 显示前几个翻译结果作为示例
        print("\n翻译结果示例（前5个）：")
        print(result_df.head().to_string())

    except Exception as e:
        print(f"处理出错: {str(e)}")
        print("请检查：")
        print("1. 输入文件是否存在且格式正确")
        print("2. 是否有写入权限")
        print("3. 网络连接是否正常")

if __name__ == "__main__":
    input_file = r'e:\autotools\ai-class\KET单词册.xlsx'
    output_file = r'e:\autotools\ai-class\KET单词表(中英对照).xlsx'
    process_ket_vocabulary(input_file, output_file) 