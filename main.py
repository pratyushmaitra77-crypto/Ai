from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window
import threading, requests, os, json

# ============ গ্লোবাল সেটিংস ============
Window.clearcolor = (0.04, 0.05, 0.13, 1)  # গাঢ় নেভি ব্যাকগ্রাউন্ড

# Android পারমিশন (শুধু অ্যান্ড্রয়েডে চলে)
if platform == "android":
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.RECORD_AUDIO, Permission.INTERNET])
    except:
        pass


class JarvisApp(App):
    def build(self):
        self.title = "J.A.R.V.I.S."
        self.api_key = ""
        self.config_file = ""

        # ============ মেইন লেআউট ============
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)

        # ---------- হেডার (টাইটেল + SET বাটন) ----------
        header = BoxLayout(size_hint_y=None, height=60, spacing=6)

        title_lbl = Label(
            text="J.A.R.V.I.S.",
            font_size="26sp",
            color=(0, 0.9, 1, 1),  # সায়ান নীল
            bold=True
        )
        header.add_widget(title_lbl)

        settings_btn = Button(
            text="SET",
            size_hint_x=None,
            width=70,
            font_size="16sp",
            background_color=(0.1, 0.15, 0.25, 1)  # গাঢ় নেভি
        )
        settings_btn.bind(on_press=self.open_settings)
        header.add_widget(settings_btn)

        root.add_widget(header)

        # ---------- চ্যাট এরিয়া (স্ক্রলযোগ্য) ----------
        self.scroll = ScrollView()
        self.chat = BoxLayout(orientation="vertical", size_hint_y=None,
                              spacing=8, padding=5)
        self.chat.bind(minimum_height=self.chat.setter("height"))
        self.scroll.add_widget(self.chat)
        root.add_widget(self.scroll)

        # ---------- ইনপুট রো (টেক্সট + SEND বাটন) ----------
        row = BoxLayout(size_hint_y=None, height=55, spacing=6)

        self.input = TextInput(
            hint_text="Type message...",
            multiline=False,
            font_size="16sp"
        )
        row.add_widget(self.input)

        send = Button(
            text="SEND",
            size_hint_x=None,
            width=90,
            background_color=(0, 0.9, 1, 1),  # সায়ান নীল
            font_size="16sp"
        )
        send.bind(on_press=self.send_msg)
        row.add_widget(send)

        root.add_widget(row)

        # ============ API Key লোড করুন ============
        Clock.schedule_once(self.load_api_key, 0.5)

        return root

    # ------------------------------------------------------------
    # API Key ম্যানেজমেন্ট
    # ------------------------------------------------------------
    def load_api_key(self, dt):
        """ফাইল থেকে API key লোড করুন"""
        try:
            self.config_file = os.path.join(self.user_data_dir, "jarvis_config.json")
        except:
            self.config_file = "jarvis_config.json"

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self.api_key = data.get("api_key", "")
            except:
                self.api_key = ""

        if not self.api_key:
            self.add_msg("Jarvis: Welcome! Tap SET button to add your API key.")
        else:
            self.add_msg("Jarvis: Online. How can I help you?")

    def save_api_key(self, key):
        """API key ফাইলে সেভ করুন"""
        try:
            if not self.config_file:
                self.config_file = os.path.join(self.user_data_dir, "jarvis_config.json")
            with open(self.config_file, "w") as f:
                json.dump({"api_key": key}, f)
            return True
        except Exception as e:
            print("Save error:", e)
            return False

    # ------------------------------------------------------------
    # Settings পপআপ
    # ------------------------------------------------------------
    def open_settings(self, *args):
        content = BoxLayout(orientation="vertical", padding=20, spacing=15)

        content.add_widget(Label(
            text="Settings",
            font_size="22sp",
            color=(0, 0.9, 1, 1),
            size_hint_y=None,
            height=40
        ))

        content.add_widget(Label(
            text="Paste your Gemini API Key below:",
            font_size="14sp",
            size_hint_y=None,
            height=30
        ))

        key_input = TextInput(
            text=self.api_key if self.api_key else "",
            hint_text="AIzaSy...",
            multiline=False,
            font_size="14sp",
            size_hint_y=None,
            height=50
        )
        content.add_widget(key_input)

        content.add_widget(Label(
            text="Get free key from: aistudio.google.com/app/apikey",
            font_size="11sp",
            color=(0.5, 0.7, 0.9, 1),
            size_hint_y=None,
            height=25
        ))

        status_lbl = Label(
            text="",
            font_size="13sp",
            size_hint_y=None,
            height=30
        )
        content.add_widget(status_lbl)

        btns = BoxLayout(size_hint_y=None, height=50, spacing=10)

        cancel_btn = Button(text="Cancel", background_color=(0.4, 0.4, 0.4, 1))
        save_btn = Button(text="Save", background_color=(0, 0.7, 0.4, 1))

        btns.add_widget(cancel_btn)
        btns.add_widget(save_btn)
        content.add_widget(btns)

        popup = Popup(
            title="J.A.R.V.I.S. Settings",
            content=content,
            size_hint=(0.9, 0.7),
            auto_dismiss=False
        )

        def on_cancel(instance):
            popup.dismiss()

        def on_save(instance):
            new_key = key_input.text.strip()
            if not new_key:
                status_lbl.text = "Please enter a valid key"
                status_lbl.color = (1, 0.3, 0.3, 1)
                return
            if len(new_key) < 20:
                status_lbl.text = "Key looks too short"
                status_lbl.color = (1, 0.3, 0.3, 1)
                return
            if self.save_api_key(new_key):
                self.api_key = new_key
                status_lbl.text = "API Key saved successfully!"
                status_lbl.color = (0.2, 1, 0.4, 1)
                self.add_msg("Jarvis: API key configured. Ready!")
                Clock.schedule_once(lambda dt: popup.dismiss(), 1)
            else:
                status_lbl.text = "Failed to save key"
                status_lbl.color = (1, 0.3, 0.3, 1)

        cancel_btn.bind(on_press=on_cancel)
        save_btn.bind(on_press=on_save)

        popup.open()

    # ------------------------------------------------------------
    # চ্যাট মেসেজ হ্যান্ডলিং
    # ------------------------------------------------------------
    def add_msg(self, text):
        """চ্যাট এরিয়ায় মেসেজ যোগ করুন"""
        lbl = Label(
            text=text,
            size_hint_y=None,
            font_size="15sp",
            halign="left",
            valign="top",
            padding=(15, 15),
            text_size=(Window.width - 60, None)
        )
        lbl.bind(
            texture_size=lambda inst, val: setattr(inst, "height", val[1] + 30)
        )
        self.chat.add_widget(lbl)
        Clock.schedule_once(lambda dt: setattr(self.scroll, "scroll_y", 0))

    def send_msg(self, *args):
        """SEND বাটনে চাপলে"""
        t = self.input.text.strip()
        if not t:
            return
        self.input.text = ""
        self.add_msg("You: " + t)
        threading.Thread(target=self.get_ai, args=(t,), daemon=True).start()

    # ------------------------------------------------------------
    # Gemini API কল (gemini-3.6-flash)
    # ------------------------------------------------------------
    def get_ai(self, prompt):
        """Gemini API থেকে উত্তর আনুন"""
        if not self.api_key:
            Clock.schedule_once(
                lambda dt: self.add_msg(
                    "Jarvis: Please set API key first (tap SET button)"
                ), 0
            )
            return

        # -------- মডেল নাম: gemini-3.6-flash --------
        url = ("https://generativelanguage.googleapis.com/v1beta/"
               "models/gemini-3.6-flash:generateContent?key=" + self.api_key)

        try:
            r = requests.post(
                url,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            d = r.json()
            if "candidates" in d and len(d["candidates"]) > 0:
                reply = d["candidates"][0]["content"]["parts"][0]["text"]
            elif "error" in d:
                reply = "Error: " + d["error"].get("message", "Unknown")
            else:
                reply = "No response from AI"
        except Exception as e:
            reply = "Network error: " + str(e)

        Clock.schedule_once(lambda dt: self.add_msg("Jarvis: " + reply), 0)


# ============ অ্যাপ চালু ============
JarvisApp().run()
