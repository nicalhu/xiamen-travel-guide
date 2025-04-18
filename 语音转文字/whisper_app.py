import os
import sys
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import threading
import subprocess
import time

class WhisperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper 语音转文字工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="Whisper 语音转文字工具", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 创建模型选择框架
        model_frame = ttk.LabelFrame(main_frame, text="模型选择", padding="10")
        model_frame.pack(fill=tk.X, pady=5)
        
        self.model_var = tk.StringVar(value="base")
        models = [("tiny", "最小 (速度最快，精度最低)"), 
                  ("base", "基础 (速度快，精度一般)"), 
                  ("small", "小型 (速度和精度平衡)"), 
                  ("medium", "中型 (速度较慢，精度较高)"), 
                  ("large", "大型 (速度最慢，精度最高)")]
        
        for i, (model, desc) in enumerate(models):
            ttk.Radiobutton(model_frame, text=f"{model} - {desc}", value=model, variable=self.model_var).grid(row=i, column=0, sticky=tk.W, pady=2)
        
        # 创建文件选择框架
        file_frame = ttk.LabelFrame(main_frame, text="音频文件", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        self.file_path = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=60)
        file_entry.grid(row=0, column=0, padx=5, pady=5)
        
        browse_button = ttk.Button(file_frame, text="浏览...", command=self.browse_file)
        browse_button.grid(row=0, column=1, padx=5, pady=5)
        
        # 创建转录按钮
        self.transcribe_button = ttk.Button(main_frame, text="开始转录", command=self.start_transcription)
        self.transcribe_button.pack(pady=10)
        
        # 创建进度条
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=100, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # 创建结果文本框
        result_frame = ttk.LabelFrame(main_frame, text="转录结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, width=80, height=15)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 创建状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 创建菜单
        menu_bar = tk.Menu(root)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="打开音频文件", command=self.browse_file)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=root.quit)
        menu_bar.add_cascade(label="文件", menu=file_menu)
        
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="检查环境", command=self.check_environment)
        help_menu.add_command(label="关于", command=self.show_about)
        menu_bar.add_cascade(label="帮助", menu=help_menu)
        
        root.config(menu=menu_bar)
    
    def browse_file(self):
        filetypes = (
            ('音频文件', '*.mp3 *.wav *.m4a *.ogg'),
            ('所有文件', '*.*')
        )
        filename = filedialog.askopenfilename(title="选择音频文件", filetypes=filetypes)
        if filename:
            self.file_path.set(filename)
    
    def start_transcription(self):
        if not self.file_path.get():
            self.status_var.set("错误：请先选择音频文件")
            return
        
        self.transcribe_button.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("正在转录...")
        self.result_text.delete(1.0, tk.END)
        
        # 在新线程中运行转录任务
        threading.Thread(target=self.run_transcription, daemon=True).start()
    
    def run_transcription(self):
        try:
            model = self.model_var.get()
            audio_file = self.file_path.get()
            
            # 检查 whisper 命令是否可用
            try:
                # 尝试使用 whisper 命令行工具
                cmd = ["whisper", audio_file, "--model", model, "--language", "zh"]
                self.root.after(0, lambda: self.result_text.insert(tk.END, f"执行命令: {' '.join(cmd)}\n\n"))
                
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    raise Exception(f"Whisper 命令执行失败: {stderr}")
                
                # 读取生成的文本文件
                txt_file = os.path.splitext(audio_file)[0] + ".txt"
                if os.path.exists(txt_file):
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        transcription = f.read()
                    self.root.after(0, lambda: self.result_text.insert(tk.END, transcription))
                else:
                    self.root.after(0, lambda: self.result_text.insert(tk.END, stdout))
                
            except FileNotFoundError:
                # 如果 whisper 命令不可用，显示安装指南
                self.root.after(0, lambda: self.result_text.insert(tk.END, "未检测到 Whisper 命令行工具。请按照以下步骤安装：\n\n"))
                self.root.after(0, lambda: self.result_text.insert(tk.END, "1. 下载并安装 Python: https://www.python.org/downloads/\n"))
                self.root.after(0, lambda: self.result_text.insert(tk.END, "2. 下载并安装 Git: https://git-scm.com/downloads\n"))
                self.root.after(0, lambda: self.result_text.insert(tk.END, "3. 打开命令提示符，运行以下命令：\n"))
                self.root.after(0, lambda: self.result_text.insert(tk.END, "   git clone https://github.com/openai/whisper.git\n"))
                self.root.after(0, lambda: self.result_text.insert(tk.END, "   cd whisper\n"))
                self.root.after(0, lambda: self.result_text.insert(tk.END, "   pip install -e .\n"))
                self.root.after(0, lambda: self.result_text.insert(tk.END, "   pip install setuptools-rust\n"))
                self.root.after(0, lambda: self.result_text.insert(tk.END, "4. 安装 FFmpeg: https://ffmpeg.org/download.html\n"))
                self.root.after(0, lambda: self.result_text.insert(tk.END, "\n安装完成后重启应用。\n"))
        
        except Exception as e:
            self.root.after(0, lambda: self.result_text.insert(tk.END, f"错误: {str(e)}\n"))
        
        finally:
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.transcribe_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.status_var.set("转录完成"))
    
    def check_environment(self):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "正在检查环境...\n\n")
        
        # 检查 Python 版本
        self.result_text.insert(tk.END, f"Python 版本: {sys.version}\n")
        
        # 检查 whisper 是否已安装
        try:
            subprocess.run(["whisper", "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.result_text.insert(tk.END, "Whisper: 已安装\n")
        except FileNotFoundError:
            self.result_text.insert(tk.END, "Whisper: 未安装\n")
        
        # 检查 FFmpeg 是否已安装
        try:
            result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            version = result.stdout.decode().split('\n')[0]
            self.result_text.insert(tk.END, f"FFmpeg: {version}\n")
        except FileNotFoundError:
            self.result_text.insert(tk.END, "FFmpeg: 未安装\n")
    
    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        
        ttk.Label(about_window, text="Whisper 语音转文字工具", font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Label(about_window, text="基于 OpenAI Whisper 模型").pack()
        ttk.Label(about_window, text="版本: 1.0.0").pack(pady=5)
        ttk.Label(about_window, text="© 2023 All Rights Reserved").pack(pady=10)
        
        ttk.Button(about_window, text="确定", command=about_window.destroy).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperGUI(root)
    root.mainloop()