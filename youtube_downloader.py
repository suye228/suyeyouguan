import customtkinter as ctk
from tkinter import messagebox
import threading
import os
import yt_dlp
from urllib.parse import urlparse

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 配置窗口
        self.title("YouTube视频下载器")
        self.geometry("600x400")
        
        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 创建主框架
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # 标题标签
        self.title_label = ctk.CTkLabel(self.main_frame, 
                                      text="YouTube视频下载器",
                                      font=("Helvetica", 24, "bold"))
        self.title_label.pack(pady=10)

        # URL输入框
        self.url_entry = ctk.CTkEntry(self.main_frame, 
                                    placeholder_text="请输入YouTube视频链接",
                                    width=400)
        self.url_entry.pack(pady=10)

        # 下载按钮
        self.download_button = ctk.CTkButton(self.main_frame, 
                                           text="下载视频",
                                           command=self.start_download)
        self.download_button.pack(pady=10)

        # 进度标签
        self.progress_label = ctk.CTkLabel(self.main_frame, text="")
        self.progress_label.pack(pady=10)

        # 进度条
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                # 计算下载进度
                total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                
                if total > 0:
                    percentage = (downloaded / total) * 100
                    speed = d.get('speed', 0)
                    if speed:
                        speed_mb = speed / 1024 / 1024  # 转换为MB/s
                        self.progress_label.configure(
                            text=f"下载进度: {percentage:.1f}% ({downloaded/1024/1024:.1f}MB/{total/1024/1024:.1f}MB) - {speed_mb:.1f}MB/s"
                        )
                    else:
                        self.progress_label.configure(
                            text=f"下载进度: {percentage:.1f}% ({downloaded/1024/1024:.1f}MB/{total/1024/1024:.1f}MB)"
                        )
                    self.progress_bar.set(percentage / 100)
                else:
                    self.progress_label.configure(
                        text=f"已下载: {downloaded/1024/1024:.1f}MB"
                    )
            except Exception as e:
                print(f"Progress calculation error: {str(e)}")
                
        elif d['status'] == 'finished':
            self.progress_label.configure(text="下载完成，正在处理视频...")
            self.progress_bar.set(1)

    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and ('youtube.com' in result.netloc or 'youtu.be' in result.netloc)
        except:
            return False

    def download_video(self):
        try:
            url = self.url_entry.get()
            if not url:
                messagebox.showerror("错误", "请输入视频URL")
                return
            
            if not self.is_valid_url(url):
                messagebox.showerror("错误", "请输入有效的YouTube视频链接")
                return

            self.progress_label.configure(text="正在准备下载...")
            self.download_button.configure(state="disabled")
            
            # 创建下载目录
            download_path = os.path.join(os.path.expanduser("~"), "Downloads", "YouTube Downloads")
            os.makedirs(download_path, exist_ok=True)

            # 配置yt-dlp选项
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # 最佳质量MP4
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
                'nocheckcertificate': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
                },
            }

            # 开始下载
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.progress_label.configure(text="正在获取视频信息...")
                info = ydl.extract_info(url, download=True)
                
                if info:
                    title = info.get('title', 'Unknown Title')
                    self.progress_label.configure(text="下载完成！")
                    messagebox.showinfo("下载完成", f"视频 '{title}' 已成功下载到:\n{download_path}")
                else:
                    raise Exception("无法获取视频信息")

        except Exception as e:
            error_msg = str(e)
            if "Video unavailable" in error_msg:
                error_msg = "视频不可用，请检查链接是否正确"
            elif "Unsupported URL" in error_msg:
                error_msg = "不支持的URL格式，请确保是YouTube视频链接"
            messagebox.showerror("错误", f"下载失败: {error_msg}")
        finally:
            self.download_button.configure(state="normal")

    def start_download(self):
        # 在新线程中启动下载
        download_thread = threading.Thread(target=self.download_video)
        download_thread.start()

if __name__ == "__main__":
    app = App()
    app.mainloop()
