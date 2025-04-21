
# tool_final_fancy_full_final_updated.py

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import BooleanProperty
import os, sys, json, requests

KV = """
<MainLayout>:
    orientation: 'horizontal'
    canvas.before:
        Color:
            rgba: (0.05, 0.05, 0.05, 1) if self.dark_mode else (1, 0.95, 0.97, 1)
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.4
        padding: 10
        spacing: 10

        ToggleButton:
            text: "Chọn thư mục"
            on_press: root.select_folder()
        ToggleButton:
            text: "Tách ảnh"
            on_press: root.split_image()
        ToggleButton:
            text: "Mở ZIP"
            on_press: root.open_zip()
        ToggleButton:
            text: "Xoá tệp"
            on_press: root.delete_files()
        ToggleButton:
            text: "Công cụ khác"
            on_press: root.launch_tool()
        ToggleButton:
            text: "Thông tin tác giả"
            on_press: root.show_author_info()
        ToggleButton:
            text: "Kiểm tra cập nhật"
            on_press: root.check_update()

        Button:
            text: "Cài đặt"
            size_hint_x: 0.8
            pos_hint: {"center_x": 0.5}
            on_press: root.open_setting()

    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.6
        padding: 10

        Label:
            text: "[b]LOG THỜI GIAN THỰC[/b]"
            markup: True
            size_hint_y: None
            height: 30
            color: 1, 1, 1, 1

        TextInput:
            id: log
            readonly: True
            background_color: (0.05, 0.05, 0.05, 1) if root.dark_mode else (1, 0.95, 0.97, 1)
            foreground_color: (0, 0.8, 0, 1)
            font_size: 14
            size_hint_y: None
            height: 200
            canvas.before:
                Color:
                    rgba: (0, 0.8, 0, 1)
                Line:
                    width: 2
                    rectangle: self.x, self.y, self.width, self.height
"""

Builder.load_string(KV)

class MainLayout(BoxLayout):
    dark_mode = BooleanProperty(False)
    current_version = "v1.2"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_folder = None
        self.load_config()

    def log(self, text, delay=0.01):
        self.ids.log.text = ""
        def typewriter(i=0):
            if i < len(text):
                self.ids.log.text += text[i]
                Clock.schedule_once(lambda dt: typewriter(i+1), delay)
            else:
                Clock.schedule_once(self.clear_log, 3)
        typewriter()

    def clear_log(self, dt):
        self.ids.log.text = ""

    def select_folder(self):
        content = BoxLayout(orientation='vertical')
        chooser = FileChooserIconView(path="/sdcard", filters=['*/'], dirselect=True)
        ok = Button(text="Chọn")
        content.add_widget(chooser)
        content.add_widget(ok)
        popup = Popup(title="Chọn thư mục", content=content, size_hint=(0.9, 0.9))
        def set_path(*_):
            if chooser.selection:
                self.selected_folder = chooser.selection[0]
                self.log(f"Đã chọn thư mục: {self.selected_folder}")
            popup.dismiss()
        ok.bind(on_press=set_path)
        popup.open()

    def split_image(self):
        if not self.selected_folder:
            self.log("Chưa chọn thư mục.")
            return
        try:
            from PIL import Image
            files = [f for f in os.listdir(self.selected_folder) if f.endswith((".jpg", ".png"))]
            if not files:
                self.log("Không tìm thấy ảnh.")
                return
            img = Image.open(os.path.join(self.selected_folder, files[0]))
            w, h = img.size[0]//3, img.size[1]//3
            for i in range(3):
                for j in range(3):
                    crop = img.crop((j*w, i*h, (j+1)*w, (i+1)*h))
                    name = f"sticker_{i}_{j}.png"
                    crop.save(os.path.join(self.selected_folder, name))
            self.log("Đã tách ảnh thành công.")
        except Exception as e:
            self.log(f"Lỗi: {e}")

    def open_zip(self):
        path = os.path.join(self.selected_folder or "", "sticker_pack.zip")
        os.system(f"xdg-open {path}")
        self.log("Đã mở ZIP.")

    def delete_files(self):
        count = 0
        for f in os.listdir(self.selected_folder):
            if f.startswith("sticker_") and f.endswith(".png"):
                os.remove(os.path.join(self.selected_folder, f))
                count += 1
        self.log(f"Đã xoá {count} ảnh.")

    def launch_tool(self):
        content = BoxLayout(orientation='vertical')
        chooser = FileChooserIconView(path="/sdcard", filters=["*.py"])
        ok = Button(text="Chạy")
        content.add_widget(chooser)
        content.add_widget(ok)
        popup = Popup(title="Chọn file .py", content=content, size_hint=(0.9, 0.9))
        def run_tool(*_):
            if chooser.selection:
                os.execl(sys.executable, sys.executable, chooser.selection[0])
        ok.bind(on_press=run_tool)
        popup.open()

    def show_author_info(self):
        content = Label(text="Công cụ được phát triển bởi dev0x4\n\nLịch sử cập nhật:\nv1.0 - Ý tưởng\nv1.1 - Giao diện\nv1.2 - Dark mode + cập nhật\n\nKhó khăn: thiết kế UI, quản lý trạng thái, tối ưu hóa hiệu năng.",
                        color=(1,1,1,1), markup=True)
        popup = Popup(title="Thông tin tác giả", content=content, size_hint=(0.9, 0.9))
        popup.open()

    
    def check_update(self):
        try:
            url = "https://raw.githubusercontent.com/dev0x4/Tools-update/main/version.txt"
            r = requests.get(url)
            remote_version = r.text.strip()
            if remote_version > self.current_version:
                self.log(f"Đã phát hiện phiên bản mới: {remote_version}")
                Clock.schedule_once(lambda dt: self.download_update(remote_version), 1)
            else:
                self.log("Bạn đang dùng phiên bản mới nhất.")
        except Exception as e:
            self.log(f"Lỗi kiểm tra cập nhật: {e}")

    def download_update(self, ver):
        try:
            url = f"https://raw.githubusercontent.com/dev0x4/Tools-update/main/tool_final_fancy_{ver}.py"
            r = requests.get(url)
            if r.status_code == 200:
                with open(__file__, "w", encoding="utf-8") as f:
                    f.write(r.text)
                self.log("Đã cập nhật thành công. Đang khởi động lại...")

                # Save the file and delete it after
                temp_file = f"tool_final_fancy_{ver}.py"
                with open(temp_file, "w", encoding="utf-8") as temp_f:
                    temp_f.write(r.text)
                os.remove(temp_file)

                Clock.schedule_once(lambda dt: os.execl(sys.executable, sys.executable, __file__), 2)
            else:
                self.log("Không tìm thấy file cập nhật.")
        except Exception as e:
            self.log(f"Lỗi tải file: {e}")

    def open_setting(self):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        label = Label(text="Bật chế độ tối?", size_hint_y=None, height=40)
        check_box = CheckBox()
        btn = Button(text="Xác nhận", size_hint_y=None, height=40)
        layout.add_widget(label)
        layout.add_widget(check_box)
        layout.add_widget(btn)
        popup = Popup(title="Cài đặt", content=layout, size_hint=(0.7, 0.4))

        def apply(*_):
            self.dark_mode = check_box.active
            self.save_config()
            popup.dismiss()

        btn.bind(on_press=apply)
        popup.open()

    def load_config(self):
        try:
            with open("config/settings.json") as f:
                conf = json.load(f)
                self.dark_mode = conf.get("dark_mode", False)
        except:
            self.dark_mode = False

    def save_config(self):
        os.makedirs("config", exist_ok=True)
        with open("config/settings.json", "w") as f:
            json.dump({"dark_mode": self.dark_mode}, f)

class FancyFinalApp(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    FancyFinalApp().run()

# tools by dev0x4
