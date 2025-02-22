import tkinter as tk
import ctypes
import win32gui
import win32process
import traceback
import sys
from typing import List

class WindowTitleEditor:
    """窗口标题修改器（管理员权限运行）"""
    
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        master.title("窗口标题修改器（后门版）")
        master.geometry("450x250")
        self._check_admin()
        self._create_widgets()
    
    def _check_admin(self) -> None:
        """验证管理员权限"""
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.user32.MessageBoxW(0, "请右键以管理员身份运行", "权限错误", 0x10)
            sys.exit(1)
    
    def _create_widgets(self) -> None:
        """构建GUI界面"""
      
        input_frame = tk.Frame(self.master)
        tk.Label(input_frame, text="目标PID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_pid = tk.Entry(input_frame, width=20)
        self.entry_pid.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="新标题:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_title = tk.Entry(input_frame, width=30)
        self.entry_title.grid(row=1, column=1, padx=5, pady=5)
        input_frame.pack(pady=15)

   
        btn_frame = tk.Frame(self.master)
        tk.Button(btn_frame, text="修改标题", command=self._safe_modify, width=12, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="清空", command=self._clear, width=12).pack(side=tk.LEFT, padx=5)
        btn_frame.pack(pady=10)

      
        self.status = tk.Label(self.master, text="就绪", fg="gray", height=2)
        self.status.pack()

    def _safe_modify(self) -> None:
        """带异常处理的修改操作"""
        try:
            self._modify()
        except Exception as e:
            traceback.print_exc()
            self._update_status(f"严重错误：{str(e)}", "red")

    def _modify(self) -> None:
        """执行核心修改逻辑"""
        pid_str = self.entry_pid.get().strip()
        new_title = self.entry_title.get().strip()

        if not pid_str or not new_title:
            self._update_status("错误：请填写所有字段", "red")
            return

        try:
            pid = int(pid_str)
            if hwnds := self._get_window_handles(pid):
                for hwnd in hwnds:
                    ctypes.windll.user32.SetWindowTextW(hwnd, new_title)
                self._update_status(f"成功修改 {len(hwnds)} 个窗口", "green")
                self._clear()
            else:
                self._update_status("未找到对应窗口", "orange")
        except ValueError:
            self._update_status("错误：PID必须是数字", "red")

    def _get_window_handles(self, pid: int) -> List[int]:
        """获取指定进程的所有窗口句柄"""
        hwnds = []
        def callback(hwnd: int, _) -> bool:
            if win32process.GetWindowThreadProcessId(hwnd)[1] == pid:
                hwnds.append(hwnd)
            return True
        win32gui.EnumWindows(callback, None)
        return hwnds

    def _clear(self) -> None:
        """清空输入内容"""
        self.entry_pid.delete(0, tk.END)
        self.entry_title.delete(0, tk.END)
        self._update_status("已重置输入", "blue")

    def _update_status(self, text: str, color: str = "gray") -> None:
        """更新状态栏信息"""
        self.status.config(text=text, fg=color)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        WindowTitleEditor(root)
        root.mainloop()
    except Exception as e:
        traceback.print_exc()
        ctypes.windll.user32.MessageBoxW(0, f"程序崩溃：{str(e)}", "致命错误", 0x10)