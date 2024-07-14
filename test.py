from utils import load_json_data
from models import Inventory
import string
import random
from database import SessionLocal
from crud import hash_password, create_users, create_employee, create_customer, create_car, create_product
from datetime import datetime, date, timedelta
import random
from models import *
from models import Customer, Contract, Order, Employee
session = SessionLocal()

employees = [
    {
        "fullname": "أحمد محمد",
        "birthdate": "1985-03-15",
        "phone_number": "0500123456",
        "career": "مهندس برمجيات",
        "salary": 12000
    },
    {
        "fullname": "فاطمة علي",
        "birthdate": "1990-07-22",
        "phone_number": "00966500234567",
        "career": "مديرة مشاريع",
        "salary": 15000
    },
    {
        "fullname": "سارة عبد الله",
        "birthdate": "1988-11-30",
        "phone_number": "00966500345678",
        "career": "محللة نظم",
        "salary": 13000
    },
    {
        "fullname": "خالد حسن",
        "birthdate": "1975-06-10",
        "phone_number": "00966500456789",
        "career": "مطور ويب",
        "salary": 11000
    },
    {
        "fullname": "منى يوسف",
        "birthdate": "1982-04-18",
        "phone_number": "00966500567890",
        "career": "مصممة جرافيك",
        "salary": 9000
    },
    {
        "fullname": "ياسر إبراهيم",
        "birthdate": "1995-12-25",
        "phone_number": "00966500678901",
        "career": "مدير تسويق",
        "salary": 14000
    },
    {
        "fullname": "ليلى سامي",
        "birthdate": "1983-09-14",
        "phone_number": "00966500789012",
        "career": "محاسبة",
        "salary": 10000
    },
    {
        "fullname": "علي عبد الرحمن",
        "birthdate": "1978-01-05",
        "phone_number": "00966500890123",
        "career": "مستشار قانوني",
        "salary": 16000
    },
    {
        "fullname": "نورة سالم",
        "birthdate": "1992-03-19",
        "phone_number": "00966500901234",
        "career": "معلمة",
        "salary": 8000
    },
    {
        "fullname": "محمود كمال",
        "birthdate": "1986-08-20",
        "phone_number": "00966501012345",
        "career": "طبيب",
        "salary": 20000
    },
    {
        "fullname": "عائشة سعيد",
        "birthdate": "1993-07-07",
        "phone_number": "00966501123456",
        "career": "صيدلانية",
        "salary": 12000
    },
    {
        "fullname": "إبراهيم حسن",
        "birthdate": "1980-02-12",
        "phone_number": "00966501234567",
        "career": "مهندس معماري",
        "salary": 15000
    },
    {
        "fullname": "ريم محمد",
        "birthdate": "1987-05-29",
        "phone_number": "00966501345678",
        "career": "أخصائية نفسية",
        "salary": 13000
    },
    {
        "fullname": "حسين علي",
        "birthdate": "1991-11-03",
        "phone_number": "00966501456789",
        "career": "مبرمج",
        "salary": 10000
    },
    {
        "fullname": "سهى عبد الرحمن",
        "birthdate": "1976-04-17",
        "phone_number": "00966501567890",
        "career": "مديرة موارد بشرية",
        "salary": 16000
    },
    {
        "fullname": "جميل مصطفى",
        "birthdate": "1984-10-24",
        "phone_number": "00966501678901",
        "career": "فني كهرباء",
        "salary": 9000
    },
    {
        "fullname": "هند ناصر",
        "birthdate": "1996-06-11",
        "phone_number": "00966501789012",
        "career": "صحفية",
        "salary": 11000
    },
    {
        "fullname": "عماد يوسف",
        "birthdate": "1989-02-28",
        "phone_number": "00966501890123",
        "career": "مهندس شبكات",
        "salary": 13000
    },
    {
        "fullname": "خديجة أحمد",
        "birthdate": "1994-08-15",
        "phone_number": "00966501901234",
        "career": "مديرة مالية",
        "salary": 15000
    },
    {
        "fullname": "فؤاد عبد الكريم",
        "birthdate": "1973-01-20",
        "phone_number": "0502012345",
        "career": "مدير عام",
        "salary": 18000
    }
]

# Print the employees dictionary


def generate_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))


employees_users = [
    {'username': 'user2', 'email': 'user2@company.com',
        'password_hash': '!pa`Peznk&', 'employee_id': 2},
    {'username': 'user3', 'email': 'user3@company.com',
        'password_hash': '=:A9l==];g', 'employee_id': 3},
    {'username': 'user4', 'email': 'user4@company.com',
        'password_hash': 'qkA3+CPB^I', 'employee_id': 4},
    {'username': 'user5', 'email': 'user5@company.com',
        'password_hash': 'Q\\5)%-7~/q', 'employee_id': 5},
    {'username': 'user6', 'email': 'user6@company.com',
        'password_hash': 'R+IJ-&:qLY', 'employee_id': 6},
    {'username': 'user7', 'email': 'user7@company.com',
        'password_hash': 'V@Wjg"Q7Jp', 'employee_id': 7},
    {'username': 'user8', 'email': 'user8@company.com',
        'password_hash': "'^&^JIHUuJ", 'employee_id': 8},
    {'username': 'user9', 'email': 'user9@company.com',
        'password_hash': 'c!qfT/g1gv', 'employee_id': 9},
    {'username': 'user10', 'email': 'user10@company.com',
        'password_hash': '|w{muE]7o>', 'employee_id': 10},
    {'username': 'user11', 'email': 'user11@company.com',
        'password_hash': 'zUzO#b1S>#', 'employee_id': 11},
    {'username': 'user12', 'email': 'user12@company.com',
        'password_hash': 'UXH"6rPzYY', 'employee_id': 12},
    {'username': 'user13', 'email': 'user13@company.com',
        'password_hash': 'm0m4:KfaPI', 'employee_id': 13},
    {'username': 'user14', 'email': 'user14@company.com',
        'password_hash': '4qL{+]c-df', 'employee_id': 14},
    {'username': 'user15', 'email': 'user15@company.com',
        'password_hash': '@\\2Ap)0&hK', 'employee_id': 15},
    {'username': 'user16', 'email': 'user16@company.com',
        'password_hash': 'Anp/_ldf[m', 'employee_id': 16},
    {'username': 'user17', 'email': 'user17@company.com',
        'password_hash': 'L_4SS.6Pks', 'employee_id': 17},
    {'username': 'user18', 'email': 'user18@company.com',
        'password_hash': 'y5z5?,p[<!', 'employee_id': 18},
    {'username': 'user19', 'email': 'user19@company.com',
        'password_hash': 'AYNm{SapEw', 'employee_id': 19},
    {'username': 'user20', 'email': 'user20@company.com',
        'password_hash': 'YNyg+j\\dka', 'employee_id': 20},
    {'username': 'user21', 'email': 'user21@company.com',
        'password_hash': '~3.[{OlHNY', 'employee_id': 21}
]


customers = [
    {
        "name": "جون دو",
        "business_name": "متجر دو",
        "business_type": "تجزئة",
        "phone_number": "555-1234",
        "address": "123 شارع إلم، سبرينغفيلد"
    },
    {
        "name": "جين سميث",
        "business_name": "مخبز سميث",
        "business_type": "أطعمة ومشروبات",
        "phone_number": "555-5678",
        "address": "456 شارع أوك، سبرينغفيلد"
    },
    {
        "name": "سام ويلسون",
        "business_name": "ورشة ويلسون لتصليح السيارات",
        "business_type": "سيارات",
        "phone_number": "555-8765",
        "address": "789 شارع باين، سبرينغفيلد"
    },
    {
        "name": "نانسي درو",
        "business_name": "مكتبة درو",
        "business_type": "تجزئة",
        "phone_number": "555-2345",
        "address": "321 شارع مابل، سبرينغفيلد"
    },
    {
        "name": "علي أحمد",
        "business_name": "مطعم أحمد",
        "business_type": "أطعمة ومشروبات",
        "phone_number": "555-3456",
        "address": "654 شارع النخيل، سبرينغفيلد"
    },
    {
        "name": "فاطمة علي",
        "business_name": "بوتيك علي",
        "business_type": "ملابس",
        "phone_number": "555-4567",
        "address": "987 شارع الأرز، سبرينغفيلد"
    },
    {
        "name": "محمد حسن",
        "business_name": "محل حسن للأجهزة",
        "business_type": "إلكترونيات",
        "phone_number": "555-5679",
        "address": "159 شارع الزيتون، سبرينغفيلد"
    },
    {
        "name": "ليلى كريم",
        "business_name": "صالون كريم",
        "business_type": "تجميل",
        "phone_number": "555-6789",
        "address": "753 شارع الفل، سبرينغفيلد"
    },
    {
        "name": "يوسف سعيد",
        "business_name": "محل سعيد للكتب",
        "business_type": "تجزئة",
        "phone_number": "555-7890",
        "address": "357 شارع الورود، سبرينغفيلد"
    },
    {
        "name": "أحمد علي",
        "business_name": "ورشة علي للنجارة",
        "business_type": "أعمال يدوية",
        "phone_number": "555-8901",
        "address": "951 شارع الشجرة، سبرينغفيلد"
    },
    {
        "name": "منى خليل",
        "business_name": "حلويات خليل",
        "business_type": "أطعمة ومشروبات",
        "phone_number": "555-9012",
        "address": "159 شارع البنفسج، سبرينغفيلد"
    },
    {
        "name": "عادل محمود",
        "business_name": "شركة محمود للتمويل",
        "business_type": "خدمات مالية",
        "phone_number": "555-0123",
        "address": "753 شارع الشفاء، سبرينغفيلد"
    },
    {
        "name": "نورا سمير",
        "business_name": "متجر سمير للملابس",
        "business_type": "ملابس",
        "phone_number": "555-1235",
        "address": "357 شارع السعادة، سبرينغفيلد"
    },
    {
        "name": "أيمن يوسف",
        "business_name": "محل يوسف للالكترونيات",
        "business_type": "إلكترونيات",
        "phone_number": "555-2346",
        "address": "951 شارع الشمس، سبرينغفيلد"
    },
    {
        "name": "هدى إبراهيم",
        "business_name": "كافيه إبراهيم",
        "business_type": "أطعمة ومشروبات",
        "phone_number": "555-3457",
        "address": "159 شارع النجوم، سبرينغفيلد"
    },
    {
        "name": "عماد سعيد",
        "business_name": "سعيد للأدوات المكتبية",
        "business_type": "تجزئة",
        "phone_number": "555-4568",
        "address": "753 شارع الزهور، سبرينغفيلد"
    },
    {
        "name": "رنا حسن",
        "business_name": "بوتيك حسن",
        "business_type": "ملابس",
        "phone_number": "555-5670",
        "address": "357 شارع السحر، سبرينغفيلد"
    },
    {
        "name": "إيهاب فوزي",
        "business_name": "فوزي لتكنولوجيا المعلومات",
        "business_type": "تقنية",
        "phone_number": "555-6781",
        "address": "951 شارع القمر، سبرينغفيلد"
    },
    {
        "name": "سحر كريم",
        "business_name": "صالون تجميل كريم",
        "business_type": "تجميل",
        "phone_number": "555-7892",
        "address": "159 شارع اللؤلؤ، سبرينغفيلد"
    },
    {
        "name": "باسم جاد",
        "business_name": "محل جاد للحلويات",
        "business_type": "أطعمة ومشروبات",
        "phone_number": "555-8903",
        "address": "753 شارع الياقوت، سبرينغفيلد"
    }
]


def random_date():
    start_date = date.today() - timedelta(days=10*365)
    random_number_of_days = random.randint(0, 10*365)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date


cars = [
    {
        "make": "Toyota",
        "model": "Camry",
        "year": 2019,
        "driving_range": 600,
        "cost": 24000,
        "plate_letters": "ABC",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Honda",
        "model": "Civic",
        "year": 2018,
        "driving_range": 550,
        "cost": 22000,
        "plate_letters": "DEF",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Ford",
        "model": "F-150",
        "year": 2020,
        "driving_range": 700,
        "cost": 30000,
        "plate_letters": "GHI",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Chevrolet",
        "model": "Malibu",
        "year": 2021,
        "driving_range": 610,
        "cost": 25000,
        "plate_letters": "JKL",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Nissan",
        "model": "Altima",
        "year": 2017,
        "driving_range": 580,
        "cost": 23000,
        "plate_letters": "MNO",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Hyundai",
        "model": "Sonata",
        "year": 2022,
        "driving_range": 600,
        "cost": 27000,
        "plate_letters": "PQR",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "BMW",
        "model": "3 Series",
        "year": 2016,
        "driving_range": 520,
        "cost": 35000,
        "plate_letters": "STU",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Mercedes-Benz",
        "model": "C-Class",
        "year": 2015,
        "driving_range": 500,
        "cost": 40000,
        "plate_letters": "VWX",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Audi",
        "model": "A4",
        "year": 2020,
        "driving_range": 530,
        "cost": 38000,
        "plate_letters": "YZA",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Tesla",
        "model": "Model 3",
        "year": 2021,
        "driving_range": 400,
        "cost": 50000,
        "plate_letters": "BCD",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Kia",
        "model": "Optima",
        "year": 2018,
        "driving_range": 580,
        "cost": 23000,
        "plate_letters": "EFG",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Volkswagen",
        "model": "Passat",
        "year": 2019,
        "driving_range": 590,
        "cost": 24000,
        "plate_letters": "HIJ",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Subaru",
        "model": "Impreza",
        "year": 2017,
        "driving_range": 560,
        "cost": 21000,
        "plate_letters": "KLM",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Mazda",
        "model": "6",
        "year": 2022,
        "driving_range": 600,
        "cost": 28000,
        "plate_letters": "NOP",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Lexus",
        "model": "IS",
        "year": 2016,
        "driving_range": 510,
        "cost": 35000,
        "plate_letters": "QRS",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Jaguar",
        "model": "XE",
        "year": 2015,
        "driving_range": 480,
        "cost": 42000,
        "plate_letters": "TUV",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Acura",
        "model": "TLX",
        "year": 2020,
        "driving_range": 520,
        "cost": 37000,
        "plate_letters": "WXY",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Infiniti",
        "model": "Q50",
        "year": 2021,
        "driving_range": 530,
        "cost": 39000,
        "plate_letters": "ZAB",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Cadillac",
        "model": "CTS",
        "year": 2017,
        "driving_range": 500,
        "cost": 35000,
        "plate_letters": "CDE",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    },
    {
        "make": "Volvo",
        "model": "S60",
        "year": 2018,
        "driving_range": 540,
        "cost": 36000,
        "plate_letters": "FGH",
        "plate_numbers": random.randint(1000, 9999),
        "buy_date": str(random_date())
    }
]


# Function to generate a random barcode

def generate_barcode():
    return ''.join(random.choices(string.digits, k=12))

# Function to generate a random safety tool name in Arabic


def generate_safety_tool_name():
    adjectives = ["أداة", "معدات", "جهاز", "وسيلة",
                  "أداة أمان", "معدات أمان", "جهاز أمان"]
    nouns = ["القفازات", "الخوذة", "النظارات الواقية", "القناع", "حزام الأمان", "الأحذية الواقية", "السترة العاكسة", "طفاية الحريق", "مقياس الغاز", "أداة الإنقاذ", "الإنذار",
             "كاشف الدخان", "مجموعة الإسعافات الأولية", "ملابس الحماية", "القبعات الواقية", "سماعات الأذن الواقية", "قناع الغبار", "القفازات العازلة", "أقنعة الوجه", "واقي السمع"]
    return f"{random.choice(adjectives)} {random.choice(nouns)}"

# Function to generate a random description in Arabic


def generate_description():
    return "هذه أداة أمان عالية الجودة مصممة لتوفير الحماية المثلى في بيئات العمل المختلفة."


# List to store product information
# products = []

# Generate 100 safety tools
# for _ in range(1000):
#     product = {
#         "product": generate_safety_tool_name(),
#         "quantity": random.randint(1, 100),
#         "price": round(random.uniform(10.0, 500.0), 2),
#         "desc": generate_description(),
#         "barcode": generate_barcode()
#     }
#     products.append(product)


data = load_json_data('data.json')
# for doc in data.company_info.documents:
#     if doc.name == 'fonts':
#         print(doc.path)
