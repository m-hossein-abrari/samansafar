import requests
import time
import sqlite3
from datetime import datetime
import re
import os
from reportlab.lib.pagesizes import A4, elevenSeventeen
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black, white, navy, gray, red
import tempfile

import arabic_reshaper
from bidi.algorithm import get_display
#########################################e3
#from persian_fpdf import PersianFPDF
import os
from datetime import datetime
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
####################################### edit2
from fpdf import FPDF
import os
from datetime import datetime
##########################################e4






TOKEN = "1358267125:T2_n-RuXha9cdoAPl3n7s-P3qWj70XcpxQU"
BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}"

# ==================== تنظیم فونت فارسی ====================
font_paths = [
    "C:/Windows/Fonts/B-NAZANIN.TTF",
    "C:/Windows/Fonts/BNazanin.ttf",
    "C:/Windows/Fonts/B Nazanin.ttf",

"C:/Windows/Fonts/Tahoma.TTF",
    "C:/Windows/Fonts/Tahoma.ttf",
    "C:/Windows/Fonts/Tahoma.ttf",
]

FONT_NAME = "Helvetica"
for path in font_paths:
    if os.path.exists(path):
        try:
            pdfmetrics.registerFont(TTFont('BNazanin', path))
            FONT_NAME = 'BNazanin'
            print(f"✅ فونت فارسی بارگذاری شد")
            break
        except:
            pass

# ==================== دیتابیس ====================
DRIVERS_DB = "drivers.db"
VACATIONS_DB = "saman_safar.db"


def init_vacation_db():
    conn = sqlite3.connect(VACATIONS_DB)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS vacations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        national_code TEXT,
        full_name TEXT,
        plate_number TEXT,
        destination TEXT,
        start_date TEXT,
        duration INTEGER,
        request_date TEXT,
        pdf_path TEXT,
        code TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        national_code TEXT,
        full_name TEXT,
        complaint_phon TEXT,
        description TEXT,
        request_date TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS lost_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        national_code TEXT,
        full_name TEXT,
        item_name TEXT,
        description TEXT,
        location TEXT,
        date_lost TEXT,
        contact_phone TEXT,
        request_date TEXT
    )''')
#####################################
    ##################### اضافه کردن دیتا edit1 ########################


init_vacation_db()


# ==================== تولید کد یکتا ====================
def generate_vacation_code(national_code):
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")
    return f"{national_code}{date_str}{time_str}"


# ==================== توابع دیتابیس ====================
def get_driver_by_national(national_code):
    if not os.path.exists(DRIVERS_DB):
        return None
    conn = sqlite3.connect(DRIVERS_DB)
    c = conn.cursor()
    c.execute("SELECT full_name, plate_number, phone FROM drivers WHERE national_code = ?", (national_code,))
    result = c.fetchone()
    conn.close()
    return result


def save_vacation(user_id, national_code, full_name, plate_number, destination, start_date, duration, pdf_path, code):
    conn = sqlite3.connect(VACATIONS_DB)
    c = conn.cursor()
    c.execute('''INSERT INTO vacations 
                 (user_id, national_code, full_name, plate_number, destination, start_date, duration, request_date, pdf_path, code)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (user_id, national_code, full_name, plate_number, destination, start_date, duration,
               datetime.now().strftime("%Y-%m-%d %H:%M"), pdf_path, code))
    conn.commit()
    conn.close()


def save_complaint(national_code, full_name, complaint_phon, description):
    conn = sqlite3.connect(VACATIONS_DB)
    c = conn.cursor()
    c.execute('''INSERT INTO complaints 
                 (national_code, full_name, complaint_phon, description,request_date)
                 VALUES (?, ?, ?, ?, ?)''',
              (national_code, full_name, complaint_phon, description,
               datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()


def save_lost_item(national_code, full_name, item_name, description, location, date_lost, contact_phone):
    conn = sqlite3.connect(VACATIONS_DB)
    c = conn.cursor()
    c.execute('''INSERT INTO lost_items 
                 (national_code, full_name, item_name, description, location, date_lost, contact_phone, request_date)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (national_code, full_name, item_name, description, location, date_lost, contact_phone,
               datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()


def save_financial(national_code, full_name, type, amount, description):
    conn = sqlite3.connect(VACATIONS_DB)
    c = conn.cursor()
    c.execute('''INSERT INTO financial 
                 (national_code, full_name, type, amount, description, date)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (national_code, full_name, type, amount, description,
               datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()


def get_financial_by_national(national_code):
    conn = sqlite3.connect(VACATIONS_DB)
    c = conn.cursor()
    c.execute("SELECT type, amount, description, date FROM financial WHERE national_code = ? ORDER BY id DESC",
              (national_code,))
    result = c.fetchall()
    conn.close()
    return result


def get_requests_by_national(national_code):
    conn = sqlite3.connect(VACATIONS_DB)
    c = conn.cursor()

    vacations = c.execute(
        "SELECT destination, start_date, duration, code FROM vacations WHERE national_code = ? ORDER BY id DESC",
        (national_code,)).fetchall()
    complaints = c.execute(
        "SELECT complaint_phon, description FROM complaints WHERE national_code = ? ORDER BY id DESC",
        (national_code,)).fetchall()
    lost_items = c.execute("SELECT item_name, location FROM lost_items WHERE national_code = ? ORDER BY id DESC",
                           (national_code,)).fetchall()

    conn.close()
    return vacations, complaints, lost_items




#########################
def reshape_text(text):
    try:
        if not text:
            return ""
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except:
        return text
########################


# ==================== تولید PDF ====================

##########################################  edit2
# ==================== کلاس PDF فارسی با FPDF ====================
class PersianPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')

        # بارگذاری فونت فارسی
        font_paths = [
            "fonts/BNazanin.ttf",
            "fonts/Vazir.ttf",
            "C:/Windows/Fonts/B-NAZANIN.TTF",
            "C:/Windows/Fonts/BNazanin.ttf",
            "C:/Windows/Fonts/Vazir.ttf",
        ]

        font_found = False
        for path in font_paths:
            if os.path.exists(path):
                try:
                    self.add_font('PersianFont', '', path, uni=True)
                    font_found = True
                    print(f"✅ فونت از {path} بارگذاری شد")
                    break
                except:
                    continue

        if not font_found:
            print("⚠️ فونت فارسی یافت نشد! از فونت پیش‌فرض استفاده می‌شود.")

        self.set_auto_page_break(auto=True, margin=15)
        self.rtl = True  # فعال‌سازی راست‌چین

    def header(self):
        """سربرگ با آرم"""
        # آرم (لوگو)
        if os.path.exists("logo.png"):
            try:
                self.image('logo.png', x=170, y=8, w=35, h=30)
            except:
                pass

           # عنوان شرکت (راست‌چین)
        self.set_font('PersianFont', '', 16)
        #self.set_text_color(0, 51, 102)
        self.ln(5)#----------  جابجایی عمودی y
        self.set_text_color(0, 0, 0)
        title = reshape_text("سامانه مدیریت حمل ونقل بار و مسافر لارستان")
        self.cell(0, 10, title, ln=True, align='C')





    def footer(self):
        """فوتر"""
        self.set_y(-15)
        self.set_font('PersianFont', '', 8)
        self.set_text_color(128, 128, 128)
        footer_text = reshape_text("شرکت حمل و نقل لارستان - کلیه حقوق محفوظ است")
        self.cell(0, 10, footer_text, ln=True, align='C')


def generate_pdf(data, doc_type="vacation"):
    """تولید PDF با فونت فارسی"""

    # ایجاد پوشه
    if not os.path.exists("pdfs"):
        os.makedirs("pdfs")

    # نام فایل
    code = data.get('code', datetime.now().strftime("%Y%m%d%H%M%S"))
    filepath = f"pdfs/{code}.pdf"

    pdf = PersianPDF()
    pdf.add_page()

    # ===== سربرگ =====
    # pdf.set_font('PersianFont', '', 16)
    # pdf.set_text_color(0, 51, 102)
    # pdf.cell(0, 10, reshape_text("شرکت حمل و نقل لارستان"), ln=True, align='C')

    pdf.set_font('PersianFont', '', 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 5, "Larestan Transportation Company", ln=True, align='C')
    pdf.ln(10)

    # ===== عنوان =====
    pdf.set_font('PersianFont', '', 18)
    pdf.set_text_color(204, 102, 0)

    titles = {
        "vacation": "فرم درخواست مرخصی",
        "complaint": "فرم ثبت شکایت",
        "lost": "فرم گزارش گمشده"
    }

    pdf.cell(0, 0, reshape_text(titles.get(doc_type, "فرم")), ln=True, align='C')
    # pdf.ln(5)

    # ===== کد مرخصی =====
    if doc_type == "vacation":
        pdf.set_font('PersianFont', '', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, reshape_text(f"کد صدور: {code}"), ln=True, align='L')
        pdf.ln(20)
        pdf.set_text_color(0, 0, 0)
        # جمله با جایگذاری دیتا
        sentence = f"درخواست مرخصی راننده {data.get('full_name', '')} با کد ملی {data.get('national_code', '')} به مقصد {data.get('destination', '')} به مدت {data.get('duration', 0)}روز از تاریخ {data.get('start_date', '')}  ثبت گردید."

        # نمایش در PDF (راست‌چین)
        pdf.multi_cell(0, 10, reshape_text(sentence), align='R')
        # ===== امضاها =====
        pdf.set_font('PersianFont', '', 11)
        #pdf.set_y(y)

        # pdf.line(120, y + 10, 180, y + 10)
        pdf.set_x(5)  # -----------جابجایی افقی x
        pdf.cell(0, 10, reshape_text(" مدیرعامل سازمان :"), ln=1, align='C')

        # pdf.line(20, y + 30, 200, y + 30)
        pdf.set_x(5)
        pdf.cell(0, 10, reshape_text("محمدامین منتظری"), ln=True, align='C')

        # آرم -----------------
        if os.path.exists("sign.jpg"):
            try:
                pdf.image('sign.jpg', x=20, y=80, w=35, h=30)
            except:
                pass
            if os.path.exists("mohr.jpg"):
                try:
                    pdf.image('mohr.jpg', x=50, y=80, w=35, h=30)
                except:
                    pass
        #----------------------  عکس راننده

        if os.path.exists(f"{data.get('national_code', '')}.jpg"):
            try:
                pdf.image(f"{data.get('national_code', '')}.jpg", x=20, y=50, w=18, h=20)
            except:
                pass

        pdf.ln(1)
    # ===== اطلاعات =====
    if doc_type == "vacation":

        fields = (
            # (data.get('national_code', ''), "کد ملی:"),
            # (data.get('full_name', ''), "نام:"),
            #  (data.get('plate_number', ''),"پلاک:" ),
            #  (data.get('destination', ''),"مقصد:" ),
            #   (data.get('start_date', ''),"تاریخ شروع:" ),
            #   (f"{data.get('duration', 0)} روز","مدت:" ),
            # ("تاریخ ثبت:", data.get('request_date', datetime.now().strftime("%Y-%m-%d %H:%M")))
            # (data.get('', ''),"پلیس راه کشور"),
            # (data.get('national_code', ''),"شماره ملی "),(data.get('full_name', ''),"بدینوسیله اعلام می گردد درخواست مرخصی آقای/ خانم "))
            # ("بلامانع می باشد",data.get('start_date', ''),"از تاریخ",f"{data.get('duration', 0)} روز","به مدت",data.get('destination', ''),"به مقصد",data.get('plate_number', ''),"خودرو به شماره انتظامی")
            # pdf.cell(0, 10, data.get('national_code', ''),"شماره ملی ",data.get('full_name', ''),"بدینوسیله اعلام می گردد درخواست مرخصی آقای/ خانم ", ln=1, align='L')
            # )
        )
    elif doc_type == "complaint":
        fields = [
            (data.get('national_code', ''),"کد ملی:" ),
            (data.get('full_name', ''),"نام:" ),
            (data.get('complaint_phon', ''),"شماره تماس:" ),
            (data.get('description', ''),"شرح:" ),
            (data.get('request_date', ''),"تاریخ ثبت:" )
        ]
    else:  # lost
        fields = [
            (data.get('national_code', ''),"کد ملی:" ),
            (data.get('full_name', ''),"نام:" ),
            (data.get('item_name', ''),"شیء گمشده:" ),
            (data.get('description', ''),"توضیحات:" ),
            (data.get('location', ''),"مکان:" ),
            (data.get('date_lost', ''),"تاریخ گم شدن:" ),
            (data.get('contact_phone', ''),"شماره تماس:" ),
            (data.get('request_date', ''),"تاریخ ثبت:" )
        ]

    # کادر
    y = pdf.get_y()
    # pdf.set_line_width(1)
    # pdf.set_draw_color(0, 51, 102)
    # pdf.rect(15, y, 180, (len(fields) + 2) * 10 + 5)

    # pdf.set_font('PersianFont', '', 14)
    # pdf.set_text_color(0, 51, 102)
    pdf.set_y(y + 5)
    # pdf.cell(0, 10, reshape_text("اطلاعات ثبت شده"), ln=True, align='C')
    # pdf.set_text_color(0, 0, 0)
    # pdf.set_font('PersianFont', '', 12)
    # =====نوشته ها
    y = pdf.get_y()
    pdf.set_text_color(0, 0, 0)
    for i, (label, value) in enumerate(fields):
        pdf.set_y(y + (i + 1) * 8 + 2)
        pdf.set_x(10)  # فاصله نوشته ها از سمت صفحه
        pdf.multi_cell(150, 5, reshape_text(label), ln=True, align='R')
        pdf.set_x(80)
        pdf.multi_cell(0, 8, reshape_text(str(value)), ln=True, align='R')

    y = pdf.get_y() + 1


    # ===== تاریخ چاپ =====
    pdf.set_font('PersianFont', '', 8)
    pdf.set_text_color(128, 128, 128)
    pdf.set_y(y + 30)
    pdf.cell(0, 10, reshape_text(
        f"تاریخ چاپ: {datetime.now().strftime('%Y-%m-%d %H:%M')}لارستان/شهرجدید/20 متری جنب اداره کل راه و شهرسازی لارستان  071-52254216    "),
             ln=True, align='C')

    if os.path.exists("join_qr_20260701.png"):
        try:
            pdf.image('join_qr_20260701.png', x=20, y=135, w=15, h=15)
        except:
            pass
            # عنوان بازو (راست‌چین)
            pdf.set_font('PersianFont', '', 16)
            # self.set_text_color(0, 51, 102)
            pdf.ln(5)  # ----------  جابجایی عمودی y
            pdf.set_text_color(0, 0, 0)
            title = reshape_text("@Tlar_bot")
            pdf.cell(0, 10, title, ln=True, align='C')

    # ===== ذخیره =====
    pdf.output(filepath)
    print(f"✅ PDF در {filepath} ذخیره شد")

    return filepath
##########################################


# ==================== ارسال پیام ====================
def send_message(chat_id, text, parse_mode=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass


def send_document(chat_id, file_path, caption=""):
    url = f"{BASE_URL}/sendDocument"
    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': chat_id, 'caption': caption}
        try:
            requests.post(url, files=files, data=data, timeout=30)
        except:
            pass


def send_menu(chat_id):
    url = f"{BASE_URL}/sendMessage"
    keyboard = {
        "inline_keyboard": [
            [{"text": "🏖️ درخواست مرخصی", "callback_data": "vacation"}],
            [],
            [{"text": "🔍 گزارش گمشده", "callback_data": "lost_item"},{"text": "📢 ثبت شکایت", "callback_data": "complaint"}],
            [{"text": "💰 امور مالی", "callback_data": "financial"}],
            [{"text": "📊 نرخ", "callback_data": "rate"},{"text": "🖼️ عکس راننده‌ها", "callback_data": "driver_photo"}],
            [],
            [{"text": "📋 مشاهده درخواست‌ها", "callback_data": "my_requests"}],
            [{"text": "❓ راهنما", "callback_data": "help"}]
        ]
    }
    payload = {
        "chat_id": chat_id,
        "text": "📋 **سامان‌سفر** - منوی اصلی\nلطفاً انتخاب کنید:",
        "reply_markup": keyboard
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass




def answer_callback(callback_id):
    url = f"{BASE_URL}/answerCallbackQuery"
    try:
        requests.post(url, json={"callback_query_id": callback_id}, timeout=5)
    except:
        pass


# ==================== وضعیت کاربران ====================
user_states = {}


# ==================== دریافت پیام‌ها ====================
def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    payload = {"timeout": 25}
    if offset:
        payload["offset"] = offset
    try:
        response = requests.post(url, json=payload, timeout=30)
        return response.json()
    except:
        return {"ok": False, "result": []}


# ==================== پردازش ====================
def process_update(update):
    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"]["id"]
        text = msg.get("text", "")

        if text == "/start":
            send_message(chat_id, "👋 به **سامان‌سفر** خوش آمدید!")
            send_menu(chat_id)
            return

        if user_id in user_states:
            state = user_states[user_id]
            step = state.get("step")

            # ========== مشاهده درخواست‌ها ==========
            if step == "view_requests":
                if not text.isdigit() or len(text) != 10:
                    send_message(chat_id, "❌ کد ملی باید 10 رقم باشد. دوباره وارد کنید:")
                    return

                national_code = text
                vacations, complaints, lost_items = get_requests_by_national(national_code)

                result = f"📋 **درخواست‌های کد ملی {national_code}**\n\n"

                if vacations:
                    result += "🏖️ **مرخصی:**\n"
                    for v in vacations[:5]:
                        result += f"   • {v[0]} | {v[1]} | {v[2]} روز | کد: {v[3]}\n"

                if complaints:
                    result += "\n📢 **شکایات:**\n"
                    for c in complaints[:5]:
                        result += f"   • {c[0]} | {c[1][:30]}...\n"

                if lost_items:
                    result += "\n🔍 **گمشده:**\n"
                    for l in lost_items[:5]:
                        result += f"   • {l[0]} | مکان: {l[1]}\n"

                if not vacations and not complaints and not lost_items:
                    result = f"📭 هیچ درخواستی برای کد ملی {national_code} یافت نشد."

                send_message(chat_id, result)
                del user_states[user_id]
                send_menu(chat_id)
                return

            # ========== مرخصی ==========
            if step == "vacation_national":
                if not text.isdigit() or len(text) != 10:
                    send_message(chat_id, "❌ کد ملی باید 10 رقم باشد. دوباره وارد کنید:")
                    return
                driver = get_driver_by_national(text)
                if not driver:
                    send_message(chat_id, "❌ راننده با این کد ملی یافت نشد!")
                    del user_states[user_id]
                    send_menu(chat_id)
                    return
                state["national_code"] = text
                state["full_name"] = driver[0]
                state["plate_number"] = driver[1]
                state["step"] = "vacation_destination"
                send_message(chat_id, f"✅ {driver[0]} عزیز، مقصد را وارد کنید:")
                return

            elif step == "vacation_destination":
                state["destination"] = text
                state["step"] = "vacation_start_date"
                send_message(chat_id, "✅ مقصد ثبت شد.\n📅 تاریخ شروع (مثال: 1403-01-01):")
                return

            elif step == "vacation_start_date":
                if not re.match(r'^\d{2}-\d{2}-\d{4}$', text):
                    send_message(chat_id, "❌ فرمت تاریخ صحیح نیست. مثال: 1403-01-01")
                    return
                state["start_date"] = text
                state["step"] = "vacation_duration"
                send_message(chat_id, "✅ تاریخ شروع ثبت شد.\n📊 مدت مرخصی (حداکثر 30 روز):")
                return

            elif step == "vacation_duration":
                if not text.isdigit():
                    send_message(chat_id, "❌ عدد وارد کنید:")
                    return
                duration = int(text)
                if duration < 1 or duration > 30:
                    send_message(chat_id, "❌ مدت باید بین 1 تا 30 روز باشد. دوباره:")
                    return

                code = generate_vacation_code(state["national_code"])

                pdf_data = {
                    'national_code': state["national_code"],
                    'full_name': state["full_name"],
                    'plate_number': state["plate_number"],
                    'destination': state["destination"],
                    'start_date': state["start_date"],
                    'duration': duration,
                    'request_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'code': code
                }
                pdf_path = generate_pdf(pdf_data, "vacation")
                save_vacation(user_id, state["national_code"], state["full_name"], state["plate_number"],
                              state["destination"], state["start_date"], duration, pdf_path, code)
                del user_states[user_id]

                send_document(chat_id, pdf_path,
                              f"✅ مرخصی {duration} روزه ثبت شد!\n"
                              f"📌 کد پیگیری: `{code}`\n\n"
                              f"این کد را برای پیگیری نگه دارید.")
                send_menu(chat_id)
                return

            # ========== شکایت ==========
            elif step == "complaint_national":
                if not text.isdigit() or len(text) != 10:
                    send_message(chat_id, "❌ کد ملی باید 10 رقم باشد. دوباره وارد کنید:")
                    return
                state["national_code"] = text
                state["step"] = "complaint_name"
                send_message(chat_id, "✅ کد ملی ثبت شد.\n👤 نام خود را وارد کنید:")
                return

            elif step == "complaint_name":
                if len(text) < 3:
                    send_message(chat_id, "❌ نام باید حداقل 3 حرف باشد. دوباره وارد کنید:")
                    return
                state["full_name"] = text
                state["step"] = "complaint_phon"
                send_message(chat_id, "✅ نام ثبت شد.\n📝 شماره تماس را وارد کنید:")
                return

            elif step == "complaint_phon":
                state["complaint_phon"] = text
                state["step"] = "complaint_desc"
                send_message(chat_id, "✅ شماره تماس ثبت شد.\n📝 شرح کامل شکایت:")
                return

            elif step == "complaint_desc":
                state["description"] = text
                pdf_data = {
                    'national_code': state["national_code"],
                    'full_name': state["full_name"],
                    'complaint_phon': state["complaint_phon"],
                    'description': state["description"],
                    'request_date': datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                pdf_path = generate_pdf(pdf_data, "complaint")
                save_complaint(state["national_code"], state["full_name"], state["complaint_phon"],state["description"])
                del user_states[user_id]
                send_document(chat_id, pdf_path, "✅ شکایت شما ثبت شد!")
                send_menu(chat_id)
                return

            # ========== گمشده ==========
            elif step == "lost_national":
                if not text.isdigit() or len(text) != 10:
                    send_message(chat_id, "❌ کد ملی باید 10 رقم باشد. دوباره وارد کنید:")
                    return
                state["national_code"] = text
                state["step"] = "lost_name"
                send_message(chat_id, "✅ کد ملی ثبت شد.\n👤 نام خود را وارد کنید:")
                return

            elif step == "lost_name":
                if len(text) < 3:
                    send_message(chat_id, "❌ نام باید حداقل 3 حرف باشد. دوباره وارد کنید:")
                    return
                state["full_name"] = text
                state["step"] = "lost_item_name"
                send_message(chat_id, "✅ نام ثبت شد.\n🔍 نام شیء گمشده:")
                return

            elif step == "lost_item_name":
                state["item_name"] = text
                state["step"] = "lost_desc"
                send_message(chat_id, "✅ نام شیء ثبت شد.\n📝 توضیحات بیشتر:")
                return

            elif step == "lost_desc":
                state["description"] = text
                state["step"] = "lost_location"
                send_message(chat_id, "✅ توضیحات ثبت شد.\n📍 مکان گم شدن:")
                return

            elif step == "lost_location":
                state["location"] = text
                state["step"] = "lost_date"
                send_message(chat_id, "✅ مکان ثبت شد.\n📅 تاریخ گم شدن (مثال: 1403-01-01):")
                return

            elif step == "lost_date":
                if not re.match(r'^\d{2}-\d{2}-\d{4}$', text):
                    send_message(chat_id, "❌ فرمت تاریخ صحیح نیست. مثال: 1403-01-01")
                    return
                state["date_lost"] = text
                state["step"] = "lost_phone"
                send_message(chat_id, "✅ تاریخ ثبت شد.\n📞 شماره تماس:")
                return

            elif step == "lost_phone":
                if not text.isdigit() or len(text) < 10:
                    send_message(chat_id, "❌ شماره تماس نامعتبر است. دوباره وارد کنید:")
                    return
                state["contact_phone"] = text
                pdf_data = {
                    'national_code': state["national_code"],
                    'full_name': state["full_name"],
                    'item_name': state["item_name"],
                    'description': state["description"],
                    'location': state["location"],
                    'date_lost': state["date_lost"],
                    'contact_phone': state["contact_phone"],
                    'request_date': datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                pdf_path = generate_pdf(pdf_data, "lost")
                save_lost_item(state["national_code"], state["full_name"], state["item_name"], state["description"],
                               state["location"], state["date_lost"], state["contact_phone"])
                del user_states[user_id]
                send_document(chat_id, pdf_path, "✅ گزارش گمشده ثبت شد!")
                send_menu(chat_id)
                return

            # ========== امور مالی ==========
            elif step == "financial_national":
                if not text.isdigit() or len(text) != 10:
                    send_message(chat_id, "❌ کد ملی باید 10 رقم باشد. دوباره وارد کنید:")
                    return
                driver = get_driver_by_national(text)
                if not driver:
                    send_message(chat_id, "❌ راننده با این کد ملی یافت نشد!")
                    del user_states[user_id]
                    send_menu(chat_id)
                    return

                state["national_code"] = text
                state["full_name"] = driver[0]

                # دریافت اطلاعات مالی از دیتابیس
                financial_records = get_financial_by_national(text)

                if financial_records:
                    total_income = 0
                    total_expense = 0
                    result = f"💰 **امور مالی {driver[0]}**\n\n"

                    for record in financial_records[:10]:
                        type_icon = "➕" if record[0] == "درآمد" else "➖"
                        result += f"{type_icon} {record[0]}: {record[1]:,} تومان\n"
                        result += f"   📝 {record[2]}\n"
                        result += f"   📅 {record[3]}\n\n"

                        if record[0] == "درآمد":
                            total_income += record[1]
                        else:
                            total_expense += record[1]

                    balance = total_income - total_expense
                    result += f"📊 **خلاصه مالی:**\n"
                    result += f"   ✅ کل درآمد: {total_income:,} تومان\n"
                    result += f"   ❌ کل هزینه: {total_expense:,} تومان\n"
                    result += f"   {'✅' if balance >= 0 else '❌'} مانده: {balance:,} تومان"

                    #send_message(chat_id, result)

                    # نمایش لینک پرداخت در صورت بدهی
                    if balance < 0:
                        result += f"\n\n🔗 **لطفاً برای تسویه بدهی روی لینک زیر کلیک کنید:**\n"
                        result += f"[پرداخت آنلاین بدهی](https://saman-safar.com/pay?code={text}&amount={abs(balance)})"

                    send_message(chat_id, result)


                else:
                    send_message(chat_id, f"📭 هیچ اطلاعات مالی برای {driver[0]} یافت نشد.")

                del user_states[user_id]
                send_menu(chat_id)
                return


            else:
                send_message(chat_id, f"📭 هیچ اطلاعات مالی برای {driver[0]} یافت نشد.")

            del user_states[user_id]
            send_menu(chat_id)
            return


    elif "callback_query" in update:
        cb = update["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        user_id = cb["from"]["id"]
        data = cb["data"]
        callback_id = cb["id"]

        answer_callback(callback_id)

        if data == "vacation":
            send_message(chat_id, "🏖️ **درخواست مرخصی**\n\nلطفاً کد ملی خود را وارد کنید:")
            user_states[user_id] = {"step": "vacation_national"}

        elif data == "complaint":
            send_message(chat_id, "📢 **ثبت شکایت**\n\nلطفاً کد ملی خود را وارد کنید:")
            user_states[user_id] = {"step": "complaint_national"}

        elif data == "lost_item":
            send_message(chat_id, "🔍 **گزارش گمشده**\n\nلطفاً کد ملی خود را وارد کنید:")
            user_states[user_id] = {"step": "lost_national"}

        elif data == "financial":
            send_message(chat_id,
                         "💰 **امور مالی**\n\nلطفاً کد ملی خود را وارد کنید تا اطلاعات مالی شما نمایش داده شود:")
            user_states[user_id] = {"step": "financial_national"}

        elif data == "rate":
            send_message(chat_id,
                         "📊 **نرخ‌های حمل و نقل**\n\n"
                         "لطفاً برای مشاهده نرخ‌ها روی لینک زیر کلیک کنید:\n\n"
                         "🔗 [مشاهده نرخ‌های حمل و نقل](http://f33-preview.awardspace.net/larvand.ir/gps.html)\n\n"
                         "📞 پشتیبانی: 07152254216")
            send_menu(chat_id)

        elif data == "driver_photo":
            send_message(chat_id,
                         "🖼️ **عکس راننده‌ها**\n\n"
                         "لطفاً برای مشاهده عکس‌های رانندگان روی لینک زیر کلیک کنید:\n\n"
                         "🔗 [مشاهده عکس راننده‌ها](http://f33-preview.awardspace.net/larvand.ir/card.html)\n\n"
                         "📞 پشتیبانی: 07152254216")
            send_menu(chat_id)

        elif data == "my_requests":
            send_message(chat_id, "📋 **مشاهده درخواست‌ها**\n\nلطفاً کد ملی خود را وارد کنید:")
            user_states[user_id] = {"step": "view_requests"}

        elif data == "help":
            help_text = """❓ **راهنمای سامان‌سفر**

🏖️ **مرخصی:** کد ملی + مقصد + تاریخ شروع + مدت (حداکثر 30 روز)
📢 **شکایت:** کد ملی + نام + نوع شکایت + شرح
🔍 **گمشده:** کد ملی + نام + توضیحات + مکان + تاریخ + شماره تماس
💰 **امور مالی:** کد ملی + مشاهده درآمد و هزینه‌ها
📊 **نرخ:** مشاهده نرخ‌های حمل بار و مسافر (لینک)
🖼️ **عکس راننده‌ها:** مشاهده عکس رانندگان (لینک)

📞 پشتیبانی: 07152254216"""
            send_message(chat_id, help_text)
            send_menu(chat_id)


# ==================== حلقه اصلی ====================
def main():
    print("🚀 سامان‌سفر نسخه 4.7 روشن شد...")
    print("💰 امور مالی | 📊 نرخ (لینک) | 🖼️ عکس (لینک)")
    last_update_id = 0

    while True:
        try:
            updates = get_updates(offset=last_update_id + 1)
            if updates.get("ok") and updates.get("result"):
                for update in updates["result"]:
                    last_update_id = update["update_id"]
                    process_update(update)
            time.sleep(1)
        except Exception as e:
            print(f"❌ خطا: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
