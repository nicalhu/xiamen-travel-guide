import whisper
import time

def transcribe_audio(audio_file_path, model_name="base"):
    """
    使用 Whisper 模型转录音频文件
    
    参数:
        audio_file_path: 音频文件路径
        model_name: 模型名称，可选 "tiny", "base", "small", "medium", "large"
    
    返回:
        转录结果字典
    """
    print(f"正在加载 {model_name} 模型...")
    start_time = time.time()
    model = whisper.load_model(model_name)
    print(f"模型加载完成，耗时 {time.time() - start_time:.2f} 秒")
    
    print(f"开始转录音频: {audio_file_path}")
    start_time = time.time()
    result = model.transcribe(audio_file_path, language="zh")
    print(f"转录完成，耗时 {time.time() - start_time:.2f} 秒")
    
    return result

if __name__ == "__main__":
    # 替换为您的音频文件路径
    audio_path = input("请输入音频文件路径: ")
    
    # 选择模型
    print("\n可用模型:")
    print("1. tiny (最小，速度最快，精度最低)")
    print("2. base (基础，速度快，精度一般)")
    print("3. small (小型，速度和精度平衡)")
    print("4. medium (中型，速度较慢，精度较高)")
    print("5. large (大型，速度最慢，精度最高)")
    
    model_choice = input("\n请选择模型 (1-5，默认为2): ")
    model_names = ["tiny", "base", "small", "medium", "large"]
    
    try:
        model_index = int(model_choice) - 1
        if model_index < 0 or model_index >= len(model_names):
            model_index = 1  # 默认使用 base 模型
    except ValueError:
        model_index = 1  # 默认使用 base 模型
    
    model_name = model_names[model_index]
    print(f"\n使用 {model_name} 模型进行转录...")
    
    # 执行转录
    result = transcribe_audio(audio_path, model_name)
    
    # 打印结果
    print("\n转录结果:")
    print(result["text"])
    
    # 保存结果到文件
    output_file = audio_path.rsplit(".", 1)[0] + "_transcription.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result["text"])
    
    print(f"\n转录结果已保存到: {output_file}")