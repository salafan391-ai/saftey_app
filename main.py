import tkinter as tk
from tkinter import messagebox, filedialog, StringVar
from ttkbootstrap import ttk, Frame, DateEntry
import ttkbootstrap as tts
from ttkbootstrap.constants import *
from ttkbootstrap.window import Toplevel
from crud import create_customer, update_customer, car_detection_false, deduct_quantity
from models import Customer, Base, Insurance, Permission, Notification, Inventory, Car, CarDriver, CarDriverCache, CarLisince, CarPartsDetection, CarYearlyDetection, User, Employee, Vacation, Visits, ToolRequest, WithdrawMoney
from schema import CustomersModel, InventoryModel, MaintenenceModel, ContractModel
from pydantic import ValidationError
from database import engine, db_session
from crud import *
from utils import *
from datetime import time
from reciepts_pdf import CreatePdf, Product, get_inventory
from conditions_pdf import create_setup_conditions
from repair_pdf import create_maintenence_pdf
from pdf_utils import translate_conditions, is_connected

# Ensure the database tables are created
Base.metadata.create_all(bind=engine, checkfirst=True)


def tk_success_message(obj_name: str):
    return messagebox.showinfo('نجاح العملية', f'تم إدخال {obj_name} بنجاح')


def show_validation_errors(e):
    errors = e.errors()
    error_messages = "\n".join(
        [f"{error['loc'][0]}: {error['msg']}" for error in errors])
    messagebox.showerror("Validation Error", error_messages)


def get_unselected_cars():
    cars = [i.id for i in db.query(Car).all()]
    car_drivers = [i.car_id for i in db.query(CarDriver).all()]
    none_selected = [get_cars(db)[i-1]
                     for i in cars if i not in car_drivers]
    return none_selected


def get_unselected_employees():
    employees = [i.id for i in db.query(Employee).all()]
    car_drivers = [i.employee_id for i in db.query(CarDriver).all()]
    none_selected = [get_employee_names(db)[i-1]
                     for i in employees if i not in car_drivers]
    return none_selected


db = db_session()
get_customers = get_customer_names(db)

TABLES = [Vacation, ToolRequest, WithdrawMoney, Permission, Notification]


def get_user_data(db: Session, model, user_id):
    instance = db.query(model).filter_by(employee_id=user_id).all()
    return instance


class LoginWindow(tk.Toplevel):
    def __init__(self, main_app):
        super().__init__(main_app)
        self.title("Login")

        tk.Label(self, text='اسم المستخدم', font=(
            'Amiri', 12)).pack(pady=5, padx=10)
        self.user_entry = ttk.Entry(self)
        self.user_entry.pack(pady=5, padx=10)

        tk.Label(self, text='كلمة المرور', font=(
            'Amiri', 12)).pack(pady=5, padx=10)
        self.password_entry = ttk.Entry(self, show='*')
        self.password_entry.pack(pady=10, padx=10)

        ttk.Button(self, text='دخول', command=self.get_access).pack(
            pady=10, padx=10)
        self.main_app = main_app

    def get_access(self):
        user = self.user_entry.get()
        password = self.password_entry.get()
        if not (user and password):
            messagebox.showerror("Error", "Username and password are required")
            return

        try:
            user_record = db.query(User).filter_by(username=user).first()
            if user_record:
                if check_password(password, user_record.password_hash):
                    self.main_app.current_user = user_record
                    # Debug print
                    self.main_app.accessibility()
                    self.destroy()
                    self.main_app.deiconify()
                else:
                    messagebox.showerror("خطأ", "كلمة المرور غير صحيحة")
            else:
                messagebox.showerror("خطأ", "اسم المستخدم غير صحيح")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))


class MainApplication(tts.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        self.title("Management Systems")
        self.withdraw()
        self.current_user = None  # Add attribute to store the current user
        self.login = LoginWindow(self)
        self.login.grab_set()
        self.create_widgets()

    def create_widgets(self):
        main_frame = Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.sales_window = None
        self.employee_window = None
        self.company_window = None
        self.car_window = None
        self.approval_window = None
        self.notification_window = None
        larger_font = ("Arial", 18)

        icons = ['🛒', '⚒️', 'ℹ️', '🚗', '✅', '👨‍🏫']
        adms = ["ادارة المبيعات", "الموارد البشرية", "معلومات المؤسسة",
                "إدارة المركبات", "إدارة الاعتمادات", "الملف الشخصي"]
        funcs = [self.open_sales_window, self.open_employee_window, self.open_company_window,
                 self.open_car_window, self.open_approval_window, self.open_notification_window]

        lst = list(zip(adms, funcs, icons))
        row, col = 0, 0
        for l, f, i in lst:
            frame = Frame(main_frame, padding=(20, 20),
                          borderwidth=2, relief="groove")
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            ttk.Label(frame, text=l, font=larger_font).pack(padx=5, pady=5)
            ttk.Label(frame, text=i, font=larger_font).pack(padx=5, pady=20)
            self.button = ttk.Button(frame, text=l, command=f)
            self.button.pack(padx=5, pady=50)

            col += 1
            if col == 3:
                col = 0
                row += 1

        for i in range(2):
            main_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
            main_frame.grid_columnconfigure(i, weight=1)

    def accessibility(self):
        if self.current_user:
            if self.current_user.employee.career != 'admin':
                if self.buttons['إدارة الاعتمادات'].cget('text') == 'إدارة الاعتمادات':
                    self.buttons['إدارة الاعتمادات'].config(state=DISABLED)
                if self.buttons['معلومات المؤسسة'].cget('text') == 'معلومات المؤسسة':
                    self.buttons['معلومات المؤسسة'].config(state=DISABLED)

    def open_sales_window(self):
        if self.sales_window is None or not self.sales_window.winfo_exists():
            self.sales_window = SalesApplication(self)

    def open_employee_window(self):
        if self.employee_window is None or not self.employee_window.winfo_exists():
            self.employee_window = EmployeeApplication(self)

    def open_company_window(self):
        if self.company_window is None or not self.company_window.winfo_exists():
            self.company_window = CompanyApplication(self)

    def open_car_window(self):
        if self.car_window is None or not self.car_window.winfo_exists():
            self.car_window = CarApplication(self)

    def open_approval_window(self):
        if self.approval_window is None or not self.approval_window.winfo_exists():
            self.approval_window = ApprovalApplication(self)

    def open_notification_window(self):
        if self.notification_window is None or not self.notification_window.winfo_exists():
            self.notification_window = NotificationApplication(self)


class AddTaskWindow(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)
        self.main_app = main_app
        current_user = self.main_app.current_user
        self.user_employee_id = current_user.employee_id
        for i in get_user_data(db, Task, self.user_employee_id):

            tts.Label(self, text=i if i.status != 'قيد العمل' else i).pack()

            def update_task_status(status):
                try:
                    status.status = 'قيد العمل'
                    db.commit()
                    messagebox.showinfo('نجاح العملية', 'تمت العملية بنجاح')
                except Exception as e:
                    messagebox.showerror('خطأ', e)
            ttk.Button(self, text='قبول', command=lambda: update_task_status(
                i)).pack() if i.status != 'قيد العمل' else None


class AddEmployeeNotifications(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)
        self.main_app = main_app
        current_user = self.main_app.current_user
        row = 1
        column = 0
        max_columns = 3  # Number of items per row
        employee_id = current_user.employee_id
        employee = db.query(Employee).filter_by(id=employee_id).one()

        ttk.Label(self, text=f"مرحبا {employee.fullname}").grid()

        for table in TABLES:
            for i, element in enumerate(get_user_data(db, table, employee.id)):
                try:
                    text = f"{element} {element.status}"
                except AttributeError:
                    text = f"{element}"
                except Exception as e:
                    messagebox.showerror('error', e)

                label = tk.Label(
                    self, text=text, borderwidth=2, relief="groove")
                label.grid(row=row, column=column,
                           padx=10, pady=10, sticky='nsew')

                column += 1
                if column >= max_columns:
                    column = 0
                    row += 1


class NotificationApplication(Toplevel):
    def __init__(self, main_app):
        super().__init__(main_app)
        self.title("ادارة التنبيهات")

        self.main_app = main_app

        self.main_frame = Frame(self)
        self.tab_control = ttk.Notebook(self.main_frame, bootstyle=PRIMARY)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Define tab configuration: (tab_text, frame_class)
        tab_configs = [
            ('التنبيهات الشخصية', AddEmployeeNotifications),
            ('طلب إجازة', AddVacationWindow),
            ('طلب إذن', AddPermissionWindow),
            ('طلب مستلزمات', AddToolRequestWindow),
            ('طلب مصروف', AddWithdrawMoney),
            ('اضافة مستند', AddDocumentsWindow),
        ]

        # Add tabs dynamically
        for tab_text, frame_class in tab_configs:
            self.add_tab(tab_text, frame_class)

    def add_tab(self, tab_text, frame_class):
        tab_frame = Frame(self.tab_control)
        self.tab_control.add(tab_frame, text=tab_text)
        tab_content = frame_class(tab_frame, self.main_app)
        tab_content.pack(fill=tk.BOTH, expand=True)
        self.tab_control.pack(expand=True, fill='both')

    def get_tab_names(self):
        return [self.tab_control.tab(index, "text") for index in range(self.tab_control.index("end"))]


class EmployeeApplication(Toplevel):
    def __init__(self, main_app,):
        super().__init__(main_app)
        self.title("الموارد البشرية")

        self.main_app = main_app

        self.main_frame = Frame(self)
        self.tab_control = ttk.Notebook(self.main_frame, bootstyle="primary")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.tab_control.pack(expand=True, fill='both')

        # Define tab configuration: (tab_text, frame_class)
        tab_configs = [
            ('الموظفين', AddEmployeeWindow),
            ('التأمين الطبي', AddMedicalInsuranceWindow)
        ]

        # Add tabs dynamicallys
        self.windows = {}
        for tab_text, frame_class in tab_configs:
            self.add_tab(tab_text, frame_class)

    def add_tab(self, tab_text, frame_class):
        tab_frame = Frame(self.tab_control, bootstyle="primary")
        self.tab_control.add(tab_frame, text=tab_text)
        if tab_text == 'الموظفين':
            window_instance = frame_class(
                tab_frame, self.main_app, self.update_employees)

        else:
            window_instance = frame_class(tab_frame, self.main_app)
        window_instance.pack(fill=tk.BOTH, expand=True)
        self.windows[tab_text] = window_instance

    def update_employees(self):
        # Update customers in AddOrderWindow
        ins_window = self.windows.get('التأمين الطبي')
        permission_window = self.windows.get('الانذارات')
        task_window = self.windows.get('إدارة المهام')
        if ins_window:
            ins_window.employee_name['values'] = get_employee_names(db)
        if permission_window:
            permission_window.person_combo['values'] = get_employee_names(db)
        if task_window:
            task_window.employee_entry['values'] = get_customer_names(db)

    def get_tab_names(self):
        return [self.tab_control.tab(index, "text") for index in range(self.tab_control.index("end"))]


class AddDocumentsWindow(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)

        user = main_app.current_user
        user = db.query(User).filter_by(id=user.id).one()
        self.user_name = user.employee.fullname

        tk.Label(self, text=f"مرحبا {self.user_name}").pack()

        tk.Label(self, text="اسم الوثيقة:").pack()
        self.document_name_entry = ttk.Entry(self)
        self.document_name_entry.pack()

        self.documents = []
        self.docs_listbox = tk.Listbox(self)
        self.docs_listbox.pack()

        ttk.Button(self, text="إضافة وثيقة",
                   command=self.add_document).pack(pady=10)
        ttk.Button(self, text="حفظ الوثائق",
                   command=self.save_documents).pack(pady=10)

    def add_document(self):
        document_name = self.document_name_entry.get().strip()
        if not document_name:
            messagebox.showerror("Error", "اسم الوثيقة مطلوب.")
            return

        doc_path = filedialog.askopenfilename()
        if doc_path:
            self.documents.append((document_name, doc_path))
            self.docs_listbox.insert(tk.END, document_name)
            self.document_name_entry.delete(0, tk.END)

    def fetch_employee_documents(self, employee_name):
        with get_db() as db:
            documents = get_employee_documents(db, employee_name)
            return documents

    def save_documents(self):
        employee_name = self.user_name
        if not employee_name:
            messagebox.showerror("Error", "اختر موظفا.")
            return
        try:
            for doc_name, doc_path in self.documents:
                with open(doc_path, 'rb') as file:
                    document_data = file.read()
                create_document(db, employee_name, doc_name, document_data)
            messagebox.showinfo("Success", "Document added successfully!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add document: {str(e)}")
            self.destroy()


class AddEmployeeWindow(Frame):
    def __init__(self, master, main_app, update_employee):
        super().__init__(master)

        self.main_app = main_app
        self.update_employee = update_employee

        ttk.Label(self, text="اسم الموظف كاملا:").grid(
            row=0, column=1, padx=10, pady=10)
        self.fullname_entry = ttk.Entry(self)
        self.fullname_entry.grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(self, text="تاريخ الميلاد:").grid(
            row=1, column=1, padx=10, pady=10)
        self.birthdate_entry = DateEntry(self, startdate=NOW)
        self.birthdate_entry.grid(row=1, column=0, padx=10, pady=10)

        ttk.Label(self, text="رقم التواصل:").grid(
            row=2, column=1, padx=10, pady=10)
        self.phone_entry = ttk.Entry(self)
        self.phone_entry.grid(row=2, column=0, padx=10, pady=10)

        ttk.Label(self, text="المسمى الوظبفي:").grid(
            row=3, column=1, padx=10, pady=10)
        self.career_entry = ttk.Entry(self)
        self.career_entry.grid(row=3, column=0, padx=10, pady=10)

        ttk.Label(self, text="الراتب:").grid(row=4, column=1, padx=10, pady=10)
        self.salary_entry = ttk.Spinbox(
            self, from_=1, to=1000000, format='%02.2f')
        self.salary_entry.grid(row=4, column=0, padx=10, pady=10)
        ttk.Button(self, text="إضافة موظف",
                   command=self.add_employee).grid(row=5, columnspan=2, padx=10, pady=10)

        # Create a frame to hold the table
        table_frame = Frame(self)
        table_frame.grid(row=6, columnspan=2, padx=10, pady=10)
        self.employee_table = ttk.Treeview(table_frame, bootstyle="primary")

        # Create the table
        self.employee_table = ttk.Treeview(table_frame, columns=(
            "اسم الموظف", 'المسمى الوظيفي'), show='headings', bootstyle="primary")
        self.employee_table.heading("اسم الموظف", text="Employee Name")
        self.employee_table.heading("المسمى الوظيفي", text="Employee Career")
        self.employee_table.grid(row=6, columnspan=2, padx=20, pady=20)
        self.populate_employee_table()

        # Populate the table with employee names

    def populate_employee_table(self):
        # Clear the existing table
        for row in self.employee_table.get_children():
            self.employee_table.delete(row)

        # Get all employees from the database
        employees = get_employee_details(db)

        # Populate the table with employee names
        for employee_name, employee_career in employees:
            self.employee_table.insert(
                "", tk.END, values=(employee_name, employee_career))

    def clear_entries(self):
        self.fullname_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.career_entry.delete(0, tk.END)
        self.salary_entry.delete(0, tk.END)

    def add_employee(self):
        try:
            fullname = self.fullname_entry.get().strip()
            if not fullname:
                messagebox.showerror('خطأ', 'يرجى ملئ الحقل')
                return
            birthdate = get_date(self.birthdate_entry)
            check_age(birthdate)
            phone = self.phone_entry.get()
            career = self.career_entry.get()
            salary = float(self.salary_entry.get())
            create_employee(db, fullname, birthdate, phone, career, salary)
            self.clear_entries()
            self.populate_employee_table()
            self.update_employee()
            messagebox.showinfo("Success", "Employee added successfully!")
        except ValueError:
            messagebox.showinfo('error', 'يرجى ادخال رقما صالحا')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {str(e)}")
            self.destroy()


class AddVacationWindow(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)
        self.main_app = main_app
        ttk.Label(self, text="بداية الإجازة: ").pack()
        self.start_date_entry = DateEntry(self, startdate=NOW)
        self.start_date_entry.pack()

        ttk.Label(self, text="المدة: ").pack()
        self.period_entry = ttk.Entry(self)
        self.period_entry.pack()

        ttk.Label(self, text="سبب الإجازة:").pack()
        self.reason_entry = ttk.Entry(self)
        self.reason_entry.pack()

        ttk.Button(self, text="اضافة إجازة",
                   command=self.add_vacation).pack(pady=10)

        cols = ('الموظف', 'بداية الإجازة', 'نهاية الإجازة', 'الحالة')
        self.tree = ttk.Treeview(self, bootstyle="primary")
        # self.tree,7,2,*cols
        self.tree['columns'] = cols
        self.tree.heading('#0', text='ID')
        self.tree.column('#0', width=50)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)
            self.tree.pack(expand=True, padx=20, pady=20)
        self.populate_tree()

    def populate_tree(self):
        vacation_details = self.main_app.current_user.employee.vacations
        for v in vacation_details:
            self.tree.insert('', 'end', text=v.id, values=(
                v.employee.fullname,
                v.start_date,
                timedelta(int(v.period))+v.start_date,
                'تحت المراجعة' if v.status is None else v.status
            ))

    def add_vacation(self):
        startdate = get_date(self.start_date_entry)
        period = self.period_entry.get()
        reason = self.reason_entry.get()

        employee_id = self.main_app.current_user.employee_id

        # Validate input if needed
        try:
            create_vacation(db, employee_id, startdate, period, reason)
            messagebox.showinfo("Success", "Vacation added successfully!")
            self.populate_tree()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {str(e)}")
            self.destroy()


class AddTaskWindow(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)

        self.main_app = main_app

        ttk.Label(self, text="الموظف المكلف بالمهمة").pack()
        self.employee_entry = ttk.Combobox(self, values=get_employee_names(db))
        self.employee_entry.pack()

        ttk.Label(self, text="وصف المهمة:").pack()
        self.description_entry = ttk.Entry(self)
        self.description_entry.pack()

        ttk.Label(self, text="تاريخ الانجاز:").pack()
        self.due_date_entry = DateEntry(self, startdate=NOW)
        self.due_date_entry.pack()

        ttk.Label(self, text="الاولوية:").pack()
        self.priority_var = tk.StringVar()
        self.priority_combo = ttk.Combobox(
            self, textvariable=self.priority_var, values=['منخفض', 'متوسط', 'عالي'])
        self.priority_combo.pack()

        ttk.Button(self, text="اضافة مهمة",
                   command=self.add_task).pack(pady=10)

    def add_task(self):
        employee = self.employee_entry.get()
        description = self.description_entry.get()
        due_date = get_date(self.due_date_entry)
        periority = self.priority_var.get()

        employee_id = db.query(Employee).filter_by(
            fullname=employee).first().id

        assighner_id = self.main_app.current_user.employee_id

        # Validate input if needed
        try:
            create_task(db, employee_id, description, due_date,
                        periority, assigned_by_id=assighner_id)
            messagebox.showinfo("Success", "Task added successfully!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {str(e)}")
            self.destroy()


class AddNotificationWindow(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)

        self.main_app = main_app

        ttk.Label(self, text="المستهدف بالانذار").pack()
        self.person_var = tk.StringVar()
        self.person_combo = ttk.Combobox(
            self, textvariable=self.person_var, values=get_employee_names(db))
        self.person_combo.pack()

        ttk.Label(self, text="الرسالة: ").pack()
        self.message_entry = tk.Entry(self)
        self.message_entry.pack()

        ttk.Label(self, text="نوع التحذير: ").pack()
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(self, textvariable=self.type_var, values=[
                                       'إنذار', 'تذكير', 'آخر'])
        self.type_combo.pack()

        ttk.Button(self, text="اضافة رسالة",
                   command=self.add_notification).pack(pady=10)

    def add_notification(self):
        employee = self.person_var.get()
        employee_id = db.query(Employee).filter_by(
            fullname=employee).first().id

        message = self.message_entry.get()
        type = self.type_var.get()

        user_id = self.main_app.current_user.id

        if not message:
            messagebox.showerror('خطأ', 'لم تعين نوع الانذار!')

        # Validate input if needed

        try:
            create_notification(db, employee_id=employee_id,
                                message=message, type=type, user_id=user_id)
            messagebox.showinfo("Success", "Vacation added successfully!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {str(e)}")
            self.destroy()


class AddToolRequestWindow(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)

        self.main_app = main_app

        ttk.Label(self, text="المنتج: ").pack()
        self.item_entry = ttk.Entry(self)
        self.item_entry.pack()

        ttk.Label(self, text="الكمية: ").pack()
        self.quantity_entry = ttk.Entry(self)
        self.quantity_entry.pack()

        tk.Label(self, text="السعر: ").pack()
        self.cost_entry = ttk.Entry(self)
        self.cost_entry.pack()

        ttk.Button(self, text="إضافة طلب",
                   command=self.add_request_tool).pack(pady=10)

    def add_request_tool(self):
        item = self.item_entry.get()
        quantity = self.quantity_entry.get()
        cost = self.cost_entry.get()
        employee_id = self.main_app.current_user.employee_id

        try:
            create_request_tool(db, employee_id, item, quantity, cost)
            messagebox.showinfo("Success", "Employee added successfully!")
            self.destroy()
        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to add Tool Request: {str(e)}")
            self.destroy()

        # Validate input if needed


class AddPermissionWindow(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)
        self.main_app = main_app

        ttk.Label(self, text="تاريخ الاستئذان: ").grid(
            row=2, column=2, padx=10, pady=10)
        self.date_entry = DateEntry(self, startdate=NOW)
        self.date_entry.grid(row=2, column=1, padx=10, pady=10)

        frame_start = tk.Frame(self, bd=2, relief='sunken')
        frame_start.grid(row=3, column=1, columnspan=2, padx=10, pady=10)
        ttk.Label(frame_start, text='وقت البدء').grid(
            row=1, columnspan=6, padx=10, pady=10)
        ttk.Label(frame_start, text="ساعة: ").grid(
            row=2, column=6, padx=10, pady=10)
        self.start_hour_entry = ttk.Spinbox(
            frame_start, from_=0, to=23, wrap=True, format='%02.0f', width=5)
        self.start_hour_entry.grid(row=2, column=5, padx=10, pady=10)

        ttk.Label(frame_start, text="دقيقة: ").grid(
            row=2, column=4, padx=10, pady=10)
        self.start_min_entry = ttk.Spinbox(
            frame_start, from_=0, to=59, wrap=True, format='%02.0f', width=5)
        self.start_min_entry.grid(row=2, column=3, padx=10, pady=10)

        ttk.Label(frame_start, text="ثانية: ").grid(
            row=2, column=2, padx=10, pady=10)
        self.start_sec_entry = ttk.Spinbox(
            frame_start, from_=0, to=59, wrap=True, format='%02.0f', width=5)
        self.start_sec_entry.grid(row=2, column=1, padx=10, pady=10)

        frame_end = tk.Frame(self, bd=2, relief='sunken')
        frame_end.grid(row=4, column=1, columnspan=2, padx=10, pady=10)
        ttk.Label(frame_end, text='وقت الانتهاء').grid(
            row=1, columnspan=6, padx=10, pady=10)
        ttk.Label(frame_end, text="ساعة: ").grid(
            row=2, column=6, padx=10, pady=10)
        self.end_hour_entry = ttk.Spinbox(
            frame_end, from_=0, to=23, wrap=True, format='%02.0f', width=5)
        self.end_hour_entry.grid(row=2, column=5, padx=10, pady=10)

        ttk.Label(frame_end, text="دقيقة: ").grid(
            row=2, column=4, padx=10, pady=10)
        self.end_min_entry = ttk.Spinbox(
            frame_end, from_=0, to=59, wrap=True, format='%02.0f', width=5)
        self.end_min_entry.grid(row=2, column=3, padx=10, pady=10)

        ttk.Label(frame_end, text="ثانية: ").grid(
            row=2, column=2, padx=10, pady=10)
        self.end_sec_entry = ttk.Spinbox(
            frame_end, from_=0, to=59, wrap=True, format='%02.0f', width=5)
        self.end_sec_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self, text="الغرض: ").grid(row=6, column=2)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(self, textvariable=self.type_var, values=[
                                       'مرض', 'أمر شخصي', 'آخر'])
        self.type_combo.grid(row=5, column=1)
        self.type_combo.bind("<<ComboboxSelected>>", self.on_type_selected)

        # Hidden Label and Entry for "السبب اذا لم يكن أعلاه"
        self.reason_label = ttk.Label(self, text=" السبب اذا لم يكن أعلاه: ")
        self.reason_entry = ttk.Entry(self)

        # Button to add request
        ttk.Button(self, text="Add Request", command=self.add_permission_tool).grid(
            row=7, columnspan=2, padx=10, pady=10)

    def on_type_selected(self, event):
        selected_value = self.type_var.get()
        if selected_value == 'آخر':
            self.reason_label.grid(row=6, column=2)
            self.reason_entry.grid(row=6, column=1, padx=10, pady=10)
        else:
            self.reason_label.grid_remove()
            self.reason_entry.grid_remove()

    def get_start_time(self):
        selected_hour = self.start_hour_entry.get()
        selected_minute = self.start_min_entry.get()
        selected_second = self.start_sec_entry.get()
        start_time = time(int(selected_hour), int(
            selected_minute), int(selected_second))
        return start_time

    def get_end_time(self):
        selected_hour = self.end_hour_entry.get()
        selected_minute = self.end_min_entry.get()
        selected_second = self.end_sec_entry.get()
        end_time = time(int(selected_hour), int(
            selected_minute), int(selected_second))
        return end_time

    def is_valid_time_range(self):
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        return end_time >= start_time

    def add_permission_tool(self):
        start_date = get_date(self.date_entry)
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        reason = self.reason_entry.get()
        type = self.type_var.get()
        employee_id = self.main_app.current_user.employee_id

        if not self.is_valid_time_range():
            messagebox.showerror("خطأ", "يبدو أن نهاية الوقت يسبق بدايته 🤚")
            return

        # Validate input if needed
        try:
            create_permission(db, employee_id, start_date=start_date,
                              start_time=start_time, end_time=end_time, reason=reason, type=type)
            messagebox.showinfo("Success", "Permission added successfully!")
        except Exception as e:
            messagebox.showerror('error', e)
            self.destroy()


class AddWithdrawMoney(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)
        self.main_app = main_app

        ttk.Label(self, text='المبلغ المطلوب').pack()
        self.amount = ttk.Spinbox(
            self, from_=1, to=100000, format='%02.2f', wrap=True)
        self.amount.pack()

        ttk.Label(self, text='السبب').pack()
        self.reason = ttk.Entry(self)
        self.reason.pack()

        ttk.Button(self, text='طلب مصروف',
                   command=self.withdraw_add).pack(pady=10)

        # Create a frame to hold the table
        self.withdraw_table_frame = Frame(self)
        self.withdraw_table_frame.pack(pady=10)

        # Create the table
        self.withdraw_table = ttk.Treeview(self.withdraw_table_frame, columns=(
            "employee", 'amount', 'status'), show='headings', bootstyle="primary")
        self.withdraw_table.heading("employee", text="الموظف")
        self.withdraw_table.heading("amount", text="المبلغ")
        self.withdraw_table.heading("status", text="الحالة")
        self.withdraw_table.pack()

        ttk.Button(self, text='تحديث مصروف',
                   command=self.update_withdraw_data).pack(pady=10)
        self.populate_employee_table()

    def populate_employee_table(self):
        # Clear the existing table
        for row in self.withdraw_table.get_children():
            self.withdraw_table.delete(row)

        # Get all employees from the database
        employees = self.get_withdraw_details()

        # Populate the table with employee names
        for id, employee_name, amount, status in employees:
            self.withdraw_table.insert(
                "", tk.END, text=id, values=(employee_name, amount, status))

    def get_withdraw_details(self):
        employees = self.main_app.current_user.employee.withdraw_money
        return [(employee.id, employee.employee.fullname, employee.amount, employee.status) for employee in employees]

    def update_withdraw_data(self):
        try:
            selected_item = self.withdraw_table.selection()
            if selected_item:
                selected_withdraw_id = self.withdraw_table.item(
                    selected_item[0], 'text')
                withdraw = db.query(WithdrawMoney).filter_by(
                    id=int(selected_withdraw_id)).first()
                if withdraw:
                    top_level_withdraw = Toplevel()
                    top_level_withdraw.title('تحديث المصروف')

                    ttk.Label(top_level_withdraw, text='المبلغ المطلوب').pack()
                    amount_widget = ttk.Spinbox(
                        top_level_withdraw, from_=1, to=100000, format='%02.2f')
                    amount_widget.delete(0, tk.END)
                    # Pre-select the current amount
                    amount_widget.insert(0, withdraw.amount)
                    amount_widget.pack()

                    ttk.Label(top_level_withdraw, text='السبب').pack()
                    reason_widget = ttk.Entry(top_level_withdraw)
                    # Pre-select the current reason
                    reason_widget.insert(0, withdraw.reason)
                    reason_widget.pack()

                    def save_updates():
                        amount = float(amount_widget.get())
                        reason = reason_widget.get()
                        employee_id = self.main_app.current_user.employee_id
                        try:
                            update_withdraw(db, withdraw.id,
                                            employee_id, amount, reason)
                            self.populate_employee_table()
                            messagebox.showinfo('Message', 'تم التحديث بنجاح')
                            top_level_withdraw.destroy()
                        except Exception as e:
                            messagebox.showerror(
                                'Error', f"Failed to update: {str(e)}")
                            top_level_withdraw.destroy()

                    ttk.Button(top_level_withdraw, text='تحديث',
                               command=save_updates).pack(pady=10)
                else:
                    messagebox.showerror(
                        "Error", "No withdraw record found for the selected ID")
            else:
                messagebox.showerror("Error", "No withdraw record selected")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def withdraw_add(self):
        amount = float(self.amount.get())
        reason = self.reason.get()
        employee_id = self.main_app.current_user.employee_id
        try:
            create_withdraw(db, employee_id, amount, reason)
            self.populate_employee_table()
            messagebox.showinfo('Message', 'تمت الإضافة بنجاح')
        except Exception as e:
            messagebox.showerror(
                'Error', f"Failed to add withdraw record: {str(e)}")


class AddMedicalInsuranceWindow(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)

        self.main_app = main_app

        ttk.Label(self, text='اسم الموظف').pack()
        self.employee_name = ttk.Combobox(self, values=get_employee_names(db))
        self.employee_name.pack()

        ttk.Label(self, text="تاريخ البداية: ").pack()
        self.start_date_entry = DateEntry(self, startdate=NOW)
        self.start_date_entry.pack()

        ttk.Label(self, text="تاريخ النهاية: ").pack()
        self.end_date_entry = DateEntry(self, startdate=YEAR_AFTER)
        self.end_date_entry.pack()

        ttk.Button(self, text='حفظ', command=self.add_insurance).pack(pady=10)
        cols = ('اسم الموظف', 'بداية التأمين', 'نهاية التأمين')
        self.tree = ttk.Treeview(self, bootstyle="primary")

        self.tree['columns'] = cols
        self.tree.heading('#0', text='ID')
        self.tree.column('#0', width=50)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.E)
            self.tree.pack(expand=True, padx=20, pady=20)

        self.populate_treeview()

    def populate_treeview(self):
        # Clear the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch contract data from the database and populate the Treeview
        insurance = db.query(MedicalInsurance).all()

        for ins in insurance:
            self.tree.insert('', 'end', text=ins.id, values=(
                ins.employee.fullname,
                ins.start_date,
                ins.end_date

            ))

    def add_insurance(self):
        try:
            employee = self.employee_name.get()
            start_date = get_date(self.start_date_entry)
            end_date = get_date(self.end_date_entry)
            employee_id = get_employee_id(db, employee)

            create_employee_insurance(db, employee_id=employee_id,
                                      start_date=start_date, end_date=end_date)
            messagebox.showinfo('نجاح العملية', 'تمت أضافة تأمين بنجاح')
            self.populate_treeview()
        except Exception as e:
            messagebox.showerror('خطأ', e)


class CompanyApplication(tk.Toplevel):
    def __init__(self, main_app):
        super().__init__(main_app)

        self.title("Management Systems")
        self.main_app = main_app
        self.main_frame = Frame(self)
        self.tab_control = ttk.Notebook(self.main_frame)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # List of tabs and their associated windows
        tabs = [
            ('بيانات الشركة', AddCompanyWindow),
            ('اضافة حساب بنكي', AddAccountWindow),
            ('إضافة ملفات وصور', AddFileWindow),
            ('إدارة الشروط', AddConditionWindow),
        ]

        for tab_name, window_class in tabs:
            self.add_tab(tab_name, window_class)

    def add_tab(self, tab_name, window_class):
        tab_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(tab_frame, text=tab_name)
        window_instance = window_class(tab_frame, self.main_app)
        window_instance.pack(fill=tk.BOTH, expand=True)
        self.tab_control.pack(expand=True, fill='both')

    def get_tab_names(self):
        return [self.tab_control.tab(index, "text") for index in range(self.tab_control.index("end"))]


class AddCompanyWindow(tk.Frame):
    def __init__(self, master, main_app):
        super().__init__(master)

        self.main_app = main_app

        ttk.Label(self, text="اسم الشركة").grid(
            row=0, column=1, padx=10, pady=10)
        self.name_entry = ttk.Entry(self)
        self.name_entry.grid(row=0, column=0, padx=10, pady=10)

        tk.Label(self, text="رقم الجوال").grid(
            row=1, column=1, padx=10, pady=10)
        self.owner_entry = ttk.Entry(self)
        self.owner_entry.grid(row=1, column=0, padx=10, pady=10)

        ttk.Label(self, text="الرقم الضريبي").grid(
            row=2, column=1, padx=10, pady=10)
        self.tax_entry = ttk.Entry(self)
        self.tax_entry.grid(row=2, column=0, padx=10, pady=10)

        ttk.Label(self, text="رقم السجل التجاري").grid(
            row=3, column=1, padx=10, pady=10)
        self.permit_entry = ttk.Entry(self)
        self.permit_entry.grid(row=3, column=0, padx=10, pady=10)

        # Logo
        self.logo_path = StringVar()
        ttk.Button(self, text="شعار الشركة", command=self.browse_logo).grid(
            row=4, column=1, padx=10, pady=10)
        ttk.Entry(self, textvariable=self.logo_path).grid(row=4, column=0)

        # Document
        self.document_path = StringVar()
        ttk.Button(self, text="وثائق الشركة", command=self.browse_document).grid(
            row=5, column=1, padx=10, pady=10)
        ttk.Entry(self, textvariable=self.document_path).grid(
            row=5, column=0, padx=10, pady=10)

        # Save Button
        ttk.Button(self, text="حفظ", command=self.save_company).grid(
            row=6, columnspan=2, padx=10, pady=10)

        # Load existing company information if available
        self.load_company()

    def browse_logo(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.logo_path.set(file_path)

    def browse_document(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.document_path.set(file_path)

    def load_company(self):
        company = load_data.company_info
        if company:
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, company.name or "")

            self.owner_entry.delete(0, tk.END)
            self.owner_entry.insert(0, company.phone or "")

            self.tax_entry.delete(0, tk.END)
            self.tax_entry.insert(0, company.tax_number or "")

            self.permit_entry.delete(0, tk.END)
            self.permit_entry.insert(0, company.permit_number or "")
        else:
            messagebox.showinfo("Info", "No company information found.")

    def save_company(self):
        try:
            company_data = {
                'name': self.name_entry.get(),
                'phone': self.owner_entry.get(),
                'tax_number': self.tax_entry.get(),
                'permit_number': self.permit_entry.get(),
                'logo': self.logo_path.get()
            }
            update_company_info(load_data, **company_data)
            messagebox.showinfo(
                "Info", "Company information saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


class AddAccountWindow(tk.Frame):
    def __init__(self, master, main_app):
        super().__init__(master)
        self.accounts = []
        self.create_account_fields()
        self.main_app = main_app

    def create_account_fields(self):
        ttk.Label(self, text="اسم البنك").grid(
            row=0, column=1, padx=10, pady=10)
        self.bank_entry = ttk.Entry(self)
        self.bank_entry.grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(self, text="اسم المستفيد").grid(
            row=1, column=1, padx=10, pady=10)
        self.fullname_entry = ttk.Entry(self)
        self.fullname_entry.grid(row=1, column=0, padx=10, pady=10)

        ttk.Label(self, text="رقم الحساب").grid(
            row=2, column=1, padx=10, pady=10)
        self.account_number_entry = ttk.Entry(self)
        self.account_number_entry.grid(row=2, column=0, padx=10, pady=10)

        ttk.Label(self, text="رقم الايبان").grid(
            row=3, column=1, padx=10, pady=10)
        self.iban_entry = ttk.Entry(self)
        self.iban_entry.grid(row=3, column=0, padx=10, pady=10)
        ttk.Button(self, text='حذف حساب',
                   command=self.delete_account).grid(column=0, row=4)

        ttk.Button(self, text="اضافة حساب", command=self.add_account).grid(
            row=4, column=1, padx=10, pady=10)
        # ttk.Button(self, text="حفظ الحساب", command=self.save_accounts).grid(
        #     row=4, column=2, padx=10, pady=10)
        self.tree = ttk.Treeview(self, bootstyle=PRIMARY)
        cols = ('اسم البنك', 'اسم صاحب الحساب', 'رقم الحساب', 'رقم الايبان')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        self.tree.grid(row=5, column=0, columnspan=3)
        for col in cols:
            self.tree.heading(col, text=col)
        self.load_accounts()

    def add_account(self):
        account_data = {
            'bank_name': self.bank_entry.get(),
            'account_fullname': self.fullname_entry.get(),
            'account_number': self.account_number_entry.get(),
            'iban': self.iban_entry.get()
        }
        if self.bank_entry.get() != '' and self.account_number_entry.get() != '' and self.iban_entry.get() != '' and self.fullname_entry.get() != '':
            add_account(load_data, **account_data)
            self.accounts.append(account_data)
            self.tree.insert('', tk.END, values=(account_data['bank_name'], account_data['account_fullname'],
                                                 account_data['account_number'], account_data['iban']))
            self.clear_fields()
        else:
            messagebox.showerror('error', 'يجب ملئ الحقول')

    def clear_fields(self):
        self.bank_entry.delete(0, tk.END)
        self.fullname_entry.delete(0, tk.END)
        self.account_number_entry.delete(0, tk.END)
        self.iban_entry.delete(0, tk.END)

    def load_accounts(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for id, acc in enumerate(load_data.company_info.accounts) or []:
            self.tree.insert('', tk.END, text=id, values=(
                acc.bank_name, acc.account_fullname, acc.account_number, acc.account_iban))

    # def save_accounts(self):
    #     for account in self.accounts:
    #         add_account(load_data, **account)
    #     messagebox.showinfo("Info", "Accounts saved successfully.")

    def delete_account(self):
        self.accounts = load_data.company_info.accounts
        idx = self.tree.selection()
        if idx:
            id = int(self.tree.item(idx)['text'])
            delete_account(id, self.accounts)
            self.load_accounts()


class AddFileWindow(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)
        self.create_file_fields()

        self.main_app = main_app

    def create_file_fields(self):
        ttk.Label(self, text="اسم الملف").grid(
            row=0, column=1, padx=10, pady=10)
        self.file_name_entry = ttk.Entry(self)
        self.file_name_entry.grid(row=0, column=0, padx=10, pady=10)
        self.file_path = StringVar()
        ttk.Button(self, text="فتح الملف", command=self.browse_file).grid(
            row=1, column=1, padx=10, pady=10)
        ttk.Entry(self, textvariable=self.file_path).grid(
            row=1, column=0, padx=10, pady=10)

        ttk.Button(self, text="اضافة ملف", command=self.add_file).grid(
            row=2, columnspan=2, padx=10, pady=10)
        
        ttk.Button(self,text='حذف ملف',command=self.delete_file).grid(row=6,columnspan=2)

        self.tree = ttk.Treeview(self, bootstyle=PRIMARY)
        cols = ('اسم المستند', 'رابط المستند')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        self.tree.grid(row=5, column=0, columnspan=3)
        for col in cols:
            self.tree.heading(col, text=col)
        self.load_documents()


    def delete_file(self):
        documents = load_data.company_info.documents
        idx = self.tree.selection()
        if idx:
            name = self.tree.item(idx,'values')[0]
            get_index(name,documents)
            self.load_documents()
            

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path.set(file_path)

    def add_file(self):
        try:
            file_info = {
                'name': self.file_name_entry.get(),
                'path': self.file_path.get()
            }
            add_document(load_data,**file_info)
            self.clear_entries()
            self.load_documents()
        except Exception as e:
            messagebox.showerror('error',e)

    def clear_entries(self):
        self.file_name_entry.delete(0, tk.END)
        self.file_path.set("")

    def display_files(self):
        for idx, file in enumerate(self.files, start=3):
            ttk.Label(self, text=f"File {idx - 2}").grid(row=idx, columnspan=2)
            ttk.Label(self, text="File Name").grid(row=idx + 1, column=0)
            ttk.Label(self, text=file['name']).grid(row=idx + 1, column=1)

            ttk.Label(self, text="File Path").grid(row=idx + 2, column=0)
            ttk.Label(self, text=file['path']).grid(row=idx + 2, column=1)
    
    def load_documents(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for doc in load_data.company_info.documents or []:
            self.tree.insert('', tk.END, values=(
                doc.name, doc.path))


class AddConditionWindow(tk.Frame):
    def __init__(self, master, main_app):
        super().__init__(master)
        self.repair_conditions = load_data.conditions[0].condition_value
        self.setup_conditions = load_data.conditions[1].condition_value

        repair_frame1 = Frame(self)
        repair_frame2 = Frame(self)
        repair_frame1.grid(row=0, column=2, padx=20, pady=20)
        ttk.Label(repair_frame1, text='شرط صيانة').grid(
            row=0, column=1, padx=10, pady=10)
        self.new_condition_repair = ttk.Entry(repair_frame1)
        self.new_condition_repair.grid(row=0, column=0, padx=10, pady=10)
        repair_frame2.grid(row=0, column=1, padx=20)
        ttk.Label(repair_frame2, text='رقم الشرط').grid(
            row=0, column=1, padx=10, pady=10)
        self.new_index_repair_entry = ttk.Entry(repair_frame2, width=3)
        self.new_index_repair_entry.grid(row=0, column=0, padx=10, pady=10)
        self.tree_repair = ttk.Treeview(self, bootstyle=PRIMARY)
        add_button_repair = ttk.Button(
            self, text='إضافة الشرط', command=self.add_new_condition_repair, state=tk.DISABLED)
        add_button_repair.grid(row=0, column=0, pady=10)
        delete_button = ttk.Button(
            self, text='حذف شرط', command=self.delete_repair, state=tk.DISABLED)
        delete_button.grid(
            row=2, column=1, padx=10, pady=10)
        update_button = ttk.Button(
            self, text='تحدبث شرط', command=self.update_repair, state=tk.DISABLED)
        update_button.grid(
            row=2, column=0, padx=10, pady=10)

        if is_connected():
            add_button_repair.config(state=tk.NORMAL)
            delete_button.config(state=tk.NORMAL)
            update_button.config(state=tk.NORMAL)

        setup_frame1 = Frame(self)
        setup_frame2 = Frame(self)
        setup_frame2.grid(row=3, column=2, padx=20, pady=20)
        ttk.Label(setup_frame2, text='شرط تركيب').grid(row=0, column=1)
        self.new_setup_entry = ttk.Entry(setup_frame2)
        self.new_setup_entry.grid(row=0, column=0)
        setup_frame1.grid(row=3, column=1, padx=20)
        ttk.Label(setup_frame1, text='رقم الشرط').grid(row=0, column=1)
        self.new_setup_index_entry = ttk.Entry(setup_frame1, width=3)
        self.new_setup_index_entry.grid(row=0, column=0)
        ttk.Button(self, text='حذف شرط', command=self.delete_setup).grid(
            row=5, column=1, padx=10, pady=10)
        ttk.Button(self, text='تحدبث شرط', command=self.update_setup).grid(
            row=5, column=0, padx=10, pady=10)
        add_setup_button = ttk.Button(
            self, text='إضافة الشرط', command=self.add_new_condition_setup)
        add_setup_button.grid(row=3, column=0, pady=10, padx=10)

        cols = ('الصيانة',)
        self.repair_tree = ttk.Treeview(self, columns=cols, bootstyle=PRIMARY)
        self.repair_tree.heading('#0', text='ID')
        self.repair_tree.column('#0', width=50)
        for col in cols:
            self.repair_tree.heading(col, text=col)
            # Adjust width to fit long text
            self.repair_tree.column(col, anchor=tk.E, width=600)
        self.repair_tree.grid(row=1, columnspan=3, sticky='nsew')
        self.populate_repair_tree()

    def populate_repair_tree(self):
        for item in self.repair_tree.get_children():
            self.repair_tree.delete(item)
        for id, condition in enumerate(self.repair_conditions):
            self.repair_tree.insert('', 'end', text=id, values=(condition,))

        cols = ('تركيب',)
        self.setup_tree = ttk.Treeview(self, columns=cols)
        self.setup_tree.heading('#0', text='ID')
        self.setup_tree.column('#0', width=50)
        for col in cols:
            self.setup_tree.heading(col, text=col)
            self.setup_tree.column(col, anchor=tk.E, width=600)
        self.setup_tree.grid(row=4, columnspan=3, sticky='nsew')
        self.populate_setup_tree()

    def populate_setup_tree(self):
        for item in self.setup_tree.get_children():
            self.setup_tree.delete(item)
        for id, condition in enumerate(self.setup_conditions):
            self.setup_tree.insert('', 'end', text=id, values=(condition,))

    def add_new_condition_repair(self):
        new_condition = self.new_condition_repair.get()
        index_condition = int(self.new_index_repair_entry.get())
        add_condition(self.repair_conditions, new_condition=new_condition,
                      condition_number=index_condition)
        self.populate_repair_tree()
        translate_conditions()

    def delete_repair(self):
        idx = self.repair_tree.selection()
        if idx:
            id = int(self.repair_tree.item(idx[0], 'text'))
            delete_condition(id, self.repair_conditions)
            self.populate_repair_tree()
            translate_conditions()

    def update_repair(self):
        idx = self.repair_tree.selection()
        if idx:
            id = int(self.repair_tree.item(idx[0], 'text'))
            top_level = Toplevel(self)
            entry = tk.Text(top_level)
            entry.insert(tk.END, self.repair_conditions[id])
            entry.pack()

            def save_updates():
                updated_condition = entry.get()
                update_conditions(id, self.repair_conditions,
                                  updated_condition)
                self.populate_repair_tree()
                translate_conditions()
                top_level.destroy()

            save_button = ttk.Button(
                top_level, text='Save Updates', command=save_updates)
            save_button.pack()

    def add_new_condition_setup(self):
        new_condition = self.new_setup_entry.get()
        index_condition = int(self.new_setup_index_entry.get())
        add_condition(self.setup_conditions, new_condition,
                      condition_number=index_condition)
        self.populate_setup_tree()

    def delete_setup(self):
        idx = self.setup_tree.selection()
        if idx:
            id = int(self.setup_tree.item(idx[0], 'text'))
            delete_condition(id, self.setup_conditions)
            self.populate_setup_tree()

    def update_setup(self):
        idx = self.setup_tree.selection()
        if idx:
            id = int(self.setup_tree.item(idx[0], 'text'))
            top_level = Toplevel(self)
            entry = tk.Text(top_level)
            entry.insert(tk.END, self.setup_conditions[id])
            entry.pack()

            def save_updates():
                updated_condition = entry.get()
                update_conditions(id, self.setup_conditions, updated_condition)
                self.populate_repair_tree()
                top_level.destroy()

            save_button = ttk.Button(
                top_level, text='حفظ التحديث', command=save_updates)
            save_button.pack()


class AddCarWindow(tk.Frame):
    def __init__(self, master, update_car):
        super().__init__(master)
        self.update_car = update_car

        # Labels and entry fields for car information
        ttk.Label(self, text="الصنع:").grid(row=0, column=1, padx=5, pady=5)
        self.make_entry = ttk.Entry(self)
        self.make_entry.grid(row=0, column=0, padx=5, pady=5)

        ttk.Label(self, text="اسم الشركة:").grid(
            row=1, column=1, padx=5, pady=5)
        self.model_entry = ttk.Entry(self)
        self.model_entry.grid(row=1, column=0, padx=5, pady=5)

        ttk.Label(self, text="سنة الصنع:").grid(
            row=2, column=1, padx=5, pady=5)
        self.year_entry = ttk.Entry(self)
        self.year_entry.grid(row=2, column=0, padx=5, pady=5)

        ttk.Label(self, text="ممشى المركبة:").grid(
            row=3, column=1, padx=5, pady=5)
        self.range_entry = ttk.Entry(self)
        self.range_entry.grid(row=3, column=0, padx=5, pady=5)

        tk.Label(self, text="سعر المركبة:").grid(
            row=4, column=1, padx=5, pady=5)
        self.cost_entry = ttk.Spinbox(
            self, from_=1, to=10000000, format='%02.2f')
        self.cost_entry.grid(row=4, column=0, padx=5, pady=5)

        plate_frame = Frame(self)
        plate_frame.grid(row=5, column=0)
        arabic_letters = ['', 'أ', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س',
                          'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي']
        english_letters = ['', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
                           'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        numbers = ['', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        ttk.Label(self, text=' الاحرف والارقام\n بالعربية والانجليزية').grid(
            row=5, column=1)
        self.objs = []
        for i in range(4):
            arabic_combobox = ttk.Combobox(
                plate_frame, values=arabic_letters, width=4, justify='center')
            arabic_combobox.grid(row=0, column=i+1, padx=5)
            self.objs.append(arabic_combobox)

            english_combobox = ttk.Combobox(
                plate_frame, values=english_letters, width=4, justify='center')
            english_combobox.grid(row=1, column=i+1, padx=5)
            self.objs.append(english_combobox)

            number_combobox = ttk.Combobox(
                plate_frame, values=numbers, width=4, justify='center')
            number_combobox.grid(row=2, column=i+1, padx=5)
            self.objs.append(number_combobox)

        ttk.Label(self, text="تاريخ شراء المركبة:").grid(
            row=6, column=1, padx=5, pady=5)
        self.date_entry = DateEntry(self, startdate=NOW)
        self.date_entry.grid(row=6, column=0, padx=5, pady=5)

        # Button to add the car
        add_button = ttk.Button(
            self, text="إضافة سيارة جديدة", command=self.add_car)
        add_button.grid(row=7, columnspan=2, padx=5, pady=5)

        cols = ('الصنع', 'اسم الشركة', 'سنة الصنع',
                'ممشى المركبة', 'سعر المركبة')
        self.tree = ttk.Treeview(self, bootstyle=PRIMARY)
        # self.tree,7,2,*cols
        self.tree['columns'] = cols
        self.tree.heading('#0', text='ID')
        self.tree.column('#0', width=50)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.E)
            self.tree.grid(row=8, columnspan=2, padx=20, pady=20)
        self.populate_tree()

    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        cars = db.query(Car).all()
        for car in cars:
            self.tree.insert('', 'end', text=car.id, values=(
                car.make,
                car.model,
                car.year,
                car.driving_range,
                car.cost
            ))

    def clear_entries(self):
        self.make_entry.delete(0, tk.END)
        self.model_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.range_entry.delete(0, tk.END)
        self.cost_entry.delete(0, tk.END)
        for obj in self.objs:
            obj.set('')

    def add_car(self):
        # Retrieve values from entry fields
        make = self.make_entry.get()
        model = self.model_entry.get()
        year = self.year_entry.get()
        plate_letters = f"{self.objs[0].get()}-{self.objs[3].get()}-{self.objs[6].get()}\n{self.objs[1].get()}-{self.objs[4].get()}-{self.objs[7].get()}"
        plate_numbers = f"{self.objs[2].get()}-{self.objs[5].get()}-{self.objs[8].get()}"
        date_str = self.date_entry.entry.get()
        driving_range = self.range_entry.get()
        year = self.year_entry.get()
        cost = self.cost_entry.get()
        try:
            # Ensure proper data types
            year = int(year)
            driving_range = int(driving_range)
            cost = float(cost)

            create_car(
                db,
                make=make,
                model=model,
                year=year,
                plate_letters=plate_letters,
                plate_numbers=plate_numbers,
                buy_date=datetime.strptime(date_str, '%m/%d/%Y').date(),
                driving_range=driving_range,
                cost=cost
            )
            messagebox.showinfo("Success", "Car added successfully!")
            self.clear_entries()
            self.populate_tree()
            self.update_car()

        except Exception as e:
            messagebox.showerror("Error", str(e))


class AddCarYearlyDetectionWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        # Fields for Car Yearly Detection
        ttk.Label(self, text="اسم المركبة:").grid(
            row=0, column=1, padx=10, pady=10)
        self.car_id_entry = ttk.Combobox(self, values=get_cars(db))
        self.car_id_entry.grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(self, text="بداية الفحص الدوري:").grid(
            row=1, column=1, padx=10, pady=10)
        self.startdate_entry = DateEntry(self, startdate=datetime.now())
        self.startdate_entry.grid(row=1, column=0, padx=10, pady=10)

        ttk.Label(self, text="نهاية الفحص الدوري:").grid(
            row=2, column=1, padx=10, pady=10)
        self.enddate_entry = DateEntry(self, startdate=datetime.now())
        self.enddate_entry.grid(row=2, column=0, padx=10, pady=10)

        # Button to add the detection
        add_button = ttk.Button(self, text="توثيق الفحص",
                                command=self.add_detection)
        add_button.grid(row=3, columnspan=2, pady=10, padx=10)

        cols = ('اسم المركبة', 'بداية الفحص الدوري',
                'نهاية الفحص الدوري', 'الحالة')
        self.tree = ttk.Treeview(self, bootstyle=PRIMARY)
        # self.tree,7,2,*cols
        self.tree['columns'] = cols
        self.tree.heading('#0', text='ID')
        self.tree.column('#0', width=50)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)
            self.tree.grid(row=7, columnspan=2, padx=20, pady=20)
        self.populate_tree()

    def populate_tree(self):
        detection = db.query(CarYearlyDetection).all()
        for d in detection:
            self.tree.insert('', 'end', text=d.id, values=(
                get_cars(db)[d.car_id-1],
                d.startdate,
                d.enddate,
                'منتهي' if d.enddate < datetime.now().date() else 'فعال'
            ))

    def add_detection(self):
        # Retrieve values from entry fields
        car = self.car_id_entry.get()
        startdate = datetime.strptime(
            self.startdate_entry.entry.get(), '%m/%d/%Y').date()
        enddate = datetime.strptime(
            self.enddate_entry.entry.get(), '%m/%d/%Y').date()
        car_id = db.query(Car).filter_by(
            id=int(car.split('-')[0])).first().id

        try:
            create_car_yearly_detection(
                db,
                car_id=car_id,
                startdate=startdate,
                enddate=enddate
            )
            messagebox.showinfo(
                "نجاج العملية", "Car yearly detection added successfully!")
            self.clear_entries()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_entries(self):
        self.car_id_entry.delete(0, tk.END)
        self.startdate_entry.entry.delete(0, tk.END)
        self.enddate_entry.entry.delete(0, tk.END)


class AddInsuranceWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        # Fields for Insurance
        ttk.Label(self, text="اسم المركبة:").grid(
            row=0, column=1, padx=10, pady=10)
        self.car_id_entry = ttk.Combobox(self, values=get_cars(db))
        self.car_id_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self, text="بداية التأمين:").grid(
            row=1, column=1, padx=10, pady=10)
        self.start_date_entry = DateEntry(self, startdate=NOW)
        self.start_date_entry.grid(row=1, column=0, padx=10, pady=10)

        ttk.Label(self, text="نهاية التأمين:").grid(
            row=2, column=1, padx=10, pady=10)
        self.end_date_entry = DateEntry(self, startdate=YEAR_AFTER)
        self.end_date_entry.grid(row=2, column=0, padx=10, pady=10)

        ttk.Label(self, text="شركة التأمين:").grid(
            row=3, column=1, padx=10, pady=10)
        self.company_name_entry = ttk.Entry(self)
        self.company_name_entry.grid(row=3, column=0, padx=10, pady=10)

        # Button to add the insurance
        add_button = ttk.Button(self, text="توثيق تأمين",
                                command=self.add_insurance)
        add_button.grid(row=4, columnspan=2, pady=10, padx=10)

        cols = ('اسم المركبة', 'بداية التأمين', 'نهاية التأمين', 'الحالة')
        self.tree = ttk.Treeview(self)
        # self.tree,7,2,*cols
        self.tree['columns'] = cols
        self.tree.heading('#0', text='ID')
        self.tree.column('#0', width=50)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)
            self.tree.grid(row=7, columnspan=2)
        self.populate_tree()

    def populate_tree(self):
        insurance = db.query(Insurance).all()
        for ins in insurance:
            self.tree.insert('', 'end', text=ins.id, values=(
                get_cars(db)[ins.car_id-1],
                ins.start_date,
                ins.end_date,
                'منتهي' if ins.end_date < datetime.now().date() else 'فعال'
            ))

    def add_insurance(self):
        # Retrieve values from entry fields
        car = self.car_id_entry.get()
        start_date = get_date(self.start_date_entry)
        end_date = get_date(self.end_date_entry)
        company_name = self.company_name_entry.get()
        car_id = db.query(Car).filter_by(
            id=int(car.split('-')[0])).first().id

        try:
            create_car_insurance(
                db,
                car_id=car_id,
                start_date=start_date,
                end_date=end_date,
                company_name=company_name
            )
            messagebox.showinfo("Success", "Insurance added successfully!")
            self.clear_entries()
            self.populate_tree()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_entries(self):
        self.car_id_entry.delete(0, tk.END)
        self.start_date_entry.entry.delete(0, tk.END)
        self.end_date_entry.entry.delete(0, tk.END)
        self.company_name_entry.delete(0, tk.END)


class AddCarLisinceWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        # Fields for Car License
        ttk.Label(self, text="اسم المركبة:").grid(
            row=0, column=1, padx=10, pady=10)
        self.car_id_entry = ttk.Combobox(self, values=get_cars(db))
        self.car_id_entry.grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(self, text="الرقم التسلسلي:").grid(
            row=1, column=1, padx=10, pady=10)
        self.serial_number_entry = ttk.Entry(self)
        self.serial_number_entry.grid(row=1, column=0, padx=10, pady=10)

        ttk.Label(self, text="تاريخ انتهاء رخصة السير:").grid(
            row=2, column=1, padx=10, pady=10)
        self.lisince_expiry_entry = DateEntry(self, startdate=datetime.now())
        self.lisince_expiry_entry.grid(row=2, column=0, padx=10, pady=10)

        # Button to add the license
        add_button = ttk.Button(
            self, text="توثيق الرخصة", command=self.add_license)
        add_button.grid(row=3, columnspan=2, pady=10)

        cols = ('اسم المركبة', 'الرقم التسلسلي',
                'تاريخ انتهاء رخصة السير', 'الحالة')
        self.tree = ttk.Treeview(self, bootstyle=PRIMARY)
        # self.tree,7,2,*cols
        self.tree['columns'] = cols
        self.tree.heading('#0', text='ID')
        self.tree.column('#0', width=50)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)
            self.tree.grid(row=7, columnspan=2, padx=20, pady=20)
        self.populate_tree()

    def populate_tree(self):
        car_license = db.query(CarLisince).all()
        for c in car_license:
            self.tree.insert('', 'end', text=c.id, values=(
                get_cars(db)[c.car_id-1],
                c.serial_number,
                c.lisince_expiry,
                'منتهي' if c.lisince_expiry < datetime.now().date() else 'فعال'
            ))

    def add_license(self):
        # Retrieve values from entry fields
        car = self.car_id_entry.get()
        serial_number = self.serial_number_entry.get()
        lisince_expiry = datetime.strptime(
            self.lisince_expiry_entry.entry.get(), '%m/%d/%Y').date()
        car_id = db.query(Car).filter_by(
            id=int(car.split('-')[0])).first().id
        try:
            create_car_license(
                db,
                car_id=car_id,
                serial_number=serial_number,
                lisince_expiry=lisince_expiry
            )
            messagebox.showinfo("Success", "Car license added successfully!")
            self.clear_entries()
            self.populate_tree()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_entries(self):
        self.car_id_entry.delete(0, tk.END)
        self.serial_number_entry.delete(0, tk.END)
        self.lisince_expiry_entry.entry.delete(0, tk.END)


class AddCarPartsDetectionWindow(tk.Frame):
    def __init__(self, master, update_driver):
        super().__init__(master)
        self.create_widgets()
        self.update_driver = update_driver

    def create_widgets(self):
        # Fields for Car Parts Detection
        ttk.Label(self, text="اسم المركبة:").grid(
            row=0, column=1, padx=10, pady=10)
        self.car_id_entry = ttk.Combobox(self, values=get_active_cars(db))
        self.car_id_entry.grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(self, text="ممشى المركبة:").grid(
            row=1, column=1, padx=10, pady=10)
        self.driving_range_entry = ttk.Entry(self)
        self.driving_range_entry.grid(row=1, column=0, padx=10, pady=10)

        ttk.Label(self, text="الحالة").grid(row=2, column=1, padx=10, pady=10)
        self.status_entry = ttk.Combobox(self, values=['تسليم', 'استلام'])
        self.status_entry.grid(row=2, column=0, padx=10, pady=10)

        ttk.Label(self, text="ملاحظات:").grid(
            row=3, column=1, padx=10, pady=10)
        self.notes_entry = tk.Text(self)
        self.notes_entry.grid(row=3, column=0, padx=10, pady=10)

        # Button to add the detection
        add_button = ttk.Button(self, text="حفظ", command=self.add_detection)
        add_button.grid(row=4, columnspan=2, pady=10)

    def add_detection(self):
        # Retrieve values from entry fields
        car = self.car_id_entry.get()
        driving_range = self.driving_range_entry.get()
        text = self.notes_entry.get('1.0', tk.END).strip()
        car_data = db.query(Car).filter_by(id=car.split('-')[0]).first()
        car_id = car_data.id
        status = self.status_entry.get()
        is_valid = True

        try:
            # Ensure proper data types
            car_id = int(car_id)
            driving_range = int(driving_range)

            create_car_parts_detection(
                db,
                car_id=car_id,
                driving_range=driving_range,
                notes=text,
                status=status,
                is_valid=is_valid
            )
            messagebox.showinfo(
                "Success", "Car parts detection added successfully!")
            self.update_driver()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_entries(self):
        self.car_id_entry.delete(0, tk.END)
        self.status_entry.delete(0, tk.END)
        self.driving_range_entry.delete(0, tk.END)


class AddCarDriverWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        # Fields for Car Driver
        ttk.Label(self, text="الموظف:").grid(row=0, column=1, padx=10, pady=10)
        self.employee_id_entry = ttk.Combobox(
            self, values=get_unselected_employees())
        self.employee_id_entry.grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(self, text="رقم رخصة القيادة").grid(
            row=2, column=1, padx=10, pady=10)
        self.driver_license_number_entry = tk.Entry(self)
        self.driver_license_number_entry.grid(
            row=2, column=0, padx=10, pady=10)

        ttk.Label(self, text="تاريخ انتهاء الرخصة:").grid(
            row=3, column=1, padx=10, pady=10)
        self.expiry_date_entry = DateEntry(self, startdate=datetime.now())
        self.expiry_date_entry.grid(row=3, column=0, padx=10, pady=10)

        ttk.Label(self, text="تاريخ استلام المركبة:").grid(
            row=4, column=1, padx=10, pady=10)
        self.date_entry = DateEntry(self, startdate=datetime.now())
        self.date_entry.grid(row=4, column=0, padx=10, pady=10)

        ttk.Label(self, text="الفحص").grid(row=5, column=1, padx=10, pady=10)
        self.detection_id_entry = ttk.Combobox(
            self, values=get_detection_id(db))
        self.detection_id_entry.grid(row=5, column=0, padx=10, pady=10)

        # Button to add the driver
        add_button = ttk.Button(
            self, text="تعيين سائق مركبة", command=self.add_driver)
        add_button.grid(row=6, columnspan=2, pady=10)

        delete_button = ttk.Button(
            self, text='إزالة سائق مركبة', command=self.delete_driver)
        delete_button.grid(row=8, column=0, padx=10, pady=10)
        update_button = ttk.Button(
            self, text='تحديث سائق مركبة', command=self.update_car_driver)
        update_button.grid(row=8, column=1, padx=10, pady=10)

        cols = ('الموظف', 'اسم المركبة', 'رقم رخصة القيادة',
                'تاريخ انتهاء رخصة القيادة', 'تاريخ استلام المركبة', 'الحالة')
        self.tree = ttk.Treeview(self, bootstyle=PRIMARY)
        self.tree['columns'] = cols
        self.tree.heading('#0', text='ID')
        self.tree.column('#0', width=50)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.E)
            self.tree.grid(row=7, columnspan=2, padx=10, pady=10)
        self.populate_tree()

    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        drivers = db.query(CarDriver).all()
        for driver in drivers:
            self.tree.insert('', 'end', text=driver.id, values=(
                driver.employee.fullname,
                driver.detection_id,
                driver.lisince_number,
                driver.lisince_expiry_date,
                driver.date,
                'فعال' if driver.date < datetime.now().date() else 'منتهي'
            ))

    def add_driver(self):
        # Retrieve values from entry fields
        employee_name = self.employee_id_entry.get()
        date = datetime.strptime(
            self.date_entry.entry.get(), '%m/%d/%Y').date()
        license_number = self.driver_license_number_entry.get()
        expiry_date = datetime.strptime(
            self.expiry_date_entry.entry.get(), '%m/%d/%Y').date()
        detection_id = int(self.detection_id_entry.get().split('-')[0])

        try:
            # Start a new session

            # Check if the employee exists
            employee = db.query(Employee).filter_by(
                fullname=employee_name).first()
            if not employee:
                messagebox.showerror("Error", "Employee not found.")
                return

            # Check if the detection ID exists
            detection = db.query(CarPartsDetection).filter_by(
                id=detection_id).first()
            if not detection:
                messagebox.showerror("Error", "Detection ID not found.")
                return

            text = f"{employee_name}-{detection_id}-{date}-{license_number}-{expiry_date}"

            create_car_drivers_cache(db, text=text)

            # Add new car driver
            create_car_driver(
                db,
                employee_id=employee.id,
                date=date,
                lisince_number=license_number,
                lisince_expiry_date=expiry_date,
                detection_id=detection_id
            )

            car_detection_false(db, detection_id)
            messagebox.showinfo("Success", "Car driver added successfully!")
            self.populate_tree()
            self.clear_entries()
        except Exception as e:
            db.rollback()
            messagebox.showerror("Error", str(e))

    def clear_entries(self):
        self.employee_id_entry.delete(0, tk.END)
        self.detection_id_entry.delete(0, tk.END)
        self.date_entry.entry.delete(0, tk.END)
        self.driver_license_number_entry.delete(0, tk.END)
        self.expiry_date_entry.entry.delete(0, tk.END)

    def delete_driver(self):
        try:
            selected_driver = self.tree.selection()
            if selected_driver:
                selected_driver_id = self.tree.item(selected_driver[0], 'text')
                driver = db.query(CarDriver).filter_by(
                    id=int(selected_driver_id)).first()
                if driver:
                    top_level = Toplevel()
                    ttk.Label(top_level, text='يرجى اختار تقرير الفحص').pack()
                    detection_entry = ttk.Combobox(
                        top_level, values=get_detection_id(db))
                    detection_entry.pack(padx=20, pady=20)

                    def save_detection_report():
                        session = db_session()
                        detection = detection_entry.get()
                        detection_id = detection.split('-')[0]
                        detection_data = session.query(CarPartsDetection).filter_by(
                            id=int(detection_id)).first()
                        detection_data.is_valid = False
                        session.commit()

                        create_car_drivers_cache(db, detection)
                        messagebox.showinfo(
                            'نجاح العملية', 'تم حفظ التقرير بنجاح')
                        delete_driver_crud(db, driver.id)
                        self.populate_tree()
                        top_level.destroy()

                    ttk.Button(top_level, text='حفظ تقرير الفحص',
                               command=save_detection_report).pack(padx=10, pady=10)
                else:
                    messagebox.showerror("Error", "Driver not found")
            else:
                messagebox.showwarning("Warning", "No driver selected")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_car_driver(self):
        try:
            # Get the selected contract from the Treeview and allow the user to update its details
            selected_item = self.tree.selection()
            if selected_item:
                # Get the contract ID from the selected item
                selected_driver_id = self.tree.item(selected_item[0], 'text')
                driver = db.query(CarDriver).filter_by(
                    id=int(selected_driver_id)).first()

                if driver:
                    top_level_widget = Toplevel()
                    top_level_widget.title("تحديث معلومات سائق مركبة")

                    ttk.Label(top_level_widget, text="رقم رخصة القيادة").grid(
                        row=2, column=1)
                    self.driver_license_number_entry = ttk.Entry(
                        top_level_widget)
                    self.driver_license_number_entry.grid(row=2, column=0)

                    ttk.Label(top_level_widget, text="تاريخ انتهاء الرخصة:").grid(
                        row=3, column=1)
                    self.expiry_date_entry = DateEntry(
                        top_level_widget, startdate=driver.lisince_expiry_date)
                    self.expiry_date_entry.grid(row=3, column=0)

                    ttk.Label(top_level_widget, text="تاريخ استلام المركبة:").grid(
                        row=4, column=1)
                    self.date_entry = DateEntry(
                        top_level_widget, startdate=driver.date)
                    self.date_entry.grid(row=4, column=0)

                    ttk.Label(self, text="الفحص").grid(
                        row=5, column=1, padx=10, pady=10)
                    self.detection_id_entry = ttk.Combobox(
                        top_level_widget, values=get_detection_id(db))
                    self.detection_id_entry.grid(
                        row=5, column=0, padx=10, pady=10)

                    self.driver_license_number_entry.insert(
                        0, driver.lisince_number)
                    self.detection_id_entry.insert(0, driver.detection_id)

                    def save_updates():
                        license_number = self.driver_license_number_entry.get()
                        expiry_lisence = self.expiry_date_entry.entry.get()
                        date = self.date_entry.entry.get()
                        detection = self.detection_id_entry.get()

                        try:
                            update_car_driver(db, id=selected_driver_id, employee_id=driver.employee_id, date=date,
                                              lisince_expiry_date=expiry_lisence, lisince_number=license_number, detection_id=detection)
                            messagebox.showinfo(
                                "نجاح العملية", "تم تحديث السائق بنجاح")
                            self.populate_tree()
                            top_level_widget.destroy()
                        except Exception as e:
                            db.rollback()
                            messagebox.showerror(
                                "Error", f"Failed to update car driver: {str(e)}")

                    ttk.Button(top_level_widget, text='تحديث سائق',
                               command=save_updates).grid(row=6, columnspan=2)
                else:
                    messagebox.showerror(
                        "Error", "No contract found for the selected ID")
            else:
                messagebox.showerror("Error", "No contract selected")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


class CarApplication(Toplevel):
    def __init__(self, main_app):
        super().__init__(main_app)
        self.title("ادارة المركبات")

        self.main_app = main_app

        self.main_frame = Frame(self)
        self.tab_control = ttk.Notebook(self.main_frame, bootstyle=PRIMARY)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.tab_control.pack(expand=True, fill='both')
        # Define tab configuration: (tab_text, frame_class)
        tab_configs = [
            ('مركبة جديدة', AddCarWindow),
            ('الفحص السنوي', AddCarYearlyDetectionWindow),
            ('التأمين', AddInsuranceWindow),
            ('رخصة المركبة', AddCarLisinceWindow),
            ('فحص قطع المركبة', AddCarPartsDetectionWindow),
            ('سائق المركبة', AddCarDriverWindow)]

        # Add tabs dynamically
        self.windows = {}
        for tab_text, frame_class in tab_configs:
            self.add_tab(tab_text, frame_class)

    def add_tab(self, tab_text, frame_class):
        tab_frame = Frame(self.tab_control)
        self.tab_control.add(tab_frame, text=tab_text)
        if tab_text == 'مركبة جديدة':
            yearly_inspection = frame_class(
                tab_frame, self.update_cars)
        elif tab_text == 'فحص قطع المركبة':
            yearly_inspection = frame_class(
                tab_frame, self.update_detection)

        else:
            yearly_inspection = frame_class(tab_frame)
        yearly_inspection.pack(fill=tk.BOTH, expand=True)
        self.windows[tab_text] = yearly_inspection

    def update_detection(self):
        car_driver_window = self.windows.get('سائق المركبة')
        if car_driver_window:
            car_driver_window.detection_id_entry['values'] = get_detection_id(
                db)

    def update_cars(self):
        # Update customers in AddOrderWindow
        yearly_inspection_window = self.windows.get('الفحص السنوي')
        insurance_window = self.windows.get('التأمين')
        car_lisince = self.windows.get('رخصة المركبة')
        if yearly_inspection_window:
            yearly_inspection_window.car_id_entry['values'] = get_cars(db)
        if insurance_window:
            insurance_window.car_id_entry['values'] = get_cars(db)
        if car_lisince:
            car_lisince.car_id_entry['values'] = get_cars(db)

    def get_tab_names(self):
        return [self.tab_control.tab(index, "text") for index in range(self.tab_control.index("end"))]


class AddApprovalWindow(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)

        self.main_app = main_app
        self.new_applications = []
        self.frames = []

        vacations = db.query(Vacation).all()
        permissions = db.query(Permission).all()
        tool_requests = db.query(ToolRequest).all()
        money_requests = db.query(WithdrawMoney).all()
        tasks = db.query(Task).all()

        # List of all application tables
        tables = [vacations, permissions, tool_requests, money_requests, tasks]

        # Filter applications with status None
        for table in tables:
            self.new_applications.extend(
                [application for application in table if application.status is None])

        # Create a frame for each new application and add it to the GUI
        for application in self.new_applications:
            self.create_application_frame(application)

        self.pack(expand=True, fill='both')

    def create_application_frame(self, application):
        frame = Frame(self)
        frame.pack(pady=5)
        self.frames.append(frame)

        # Display the employee's full name
        ttk.Label(frame, text=f"{application}").pack(pady=10)

        # Approve and Decline buttons
        approve_button = ttk.Button(frame, text='اعتماد', command=lambda: self.save_status(
            application, 'معتمد'), bootstyle=SUCCESS)
        approve_button.pack(side=tk.LEFT, padx=5, pady=10)
        decline_button = ttk.Button(frame, text='رفض', command=lambda: self.save_status(
            application, 'مرفوض'), bootstyle=DANGER)
        decline_button.pack(side=tk.LEFT, padx=5, pady=10)

    def save_status(self, application, status):
        application.status = status
        db.commit()  # Save changes to the database
        messagebox.showinfo("Success", "Status saved successfully.")
        self.destroy()

    def get_frame_count(self):
        return len(self.frames)


class AddTaskCompletion(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)
        self.main_app = main_app
        self.current_user = self.main_app.current_user
        self.new_applications = []
        self.frames = []
        self.tasks = db.query(Task).all()
        for task in self.tasks:
            self.create_application_frame(task)
        # for application self.tasks:
        #     self.create_application_frame(application)

    def create_application_frame(self, application):
        frame = Frame(self)
        frame.pack(pady=5)
        self.frames.append(frame)

        # Display the employee's full name
        ttk.Label(
            frame, text=f"{application.employee.fullname}\n{application}\n{'الحالة منجزة' if application.completed == True else 'لم تنجز بعد'}").pack(pady=10)

        # Approve and Decline buttons
        self.approve_button = ttk.Button(
            frame, text='اعتماد الانجاز', command=lambda: self.save_status(application), bootstyle=SUCCESS)
        self.approve_button.pack(
            side=tk.LEFT, padx=5, pady=10) if application.completed == False else None

    def save_status(self, application):
        application.completed = True
        db.commit()  # Save changes to the database
        messagebox.showinfo("Success", "Status saved successfully.")
        self.destroy()
        self.approve_button.destroy()


class AddUsersWindow(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)

        self.main_app = main_app

        self.employee_id_label = ttk.Label(self, text="الموظف")
        self.employee_id_label.grid(row=0, column=1, padx=10, pady=10)
        self.employee_id_entry = ttk.Combobox(self, values=get_none_users(db))
        self.employee_id_entry.grid(row=0, column=0, padx=10, pady=10)

        self.username_label = ttk.Label(self, text="اسم المستخدم")
        self.username_label.grid(row=1, column=1, padx=10, pady=10)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=1, column=0, padx=10, pady=10)

        self.email_label = ttk.Label(self, text="الايميل")
        self.email_label.grid(row=2, column=1, padx=10, pady=10)
        self.email_entry = ttk.Entry(self)
        self.email_entry.grid(row=2, column=0, padx=10, pady=10)

        self.password_label = ttk.Label(self, text="كلمة المرور")
        self.password_label.grid(row=3, column=1, padx=10, pady=10)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=3, column=0, padx=10, pady=10)

        self.submit_button = ttk.Button(
            self, text="مستخدم جديد", command=self.create_or_update_user)
        self.submit_button.grid(row=4, columnspan=2, padx=5, pady=5)

    def create_or_update_user(self):
        employee_name = self.employee_id_entry.get()
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not (employee_name and username and email):
            messagebox.showerror(
                "Error", "Employee name, username, and email are required")
            return

        try:
            employee = db.query(Employee).filter_by(
                fullname=employee_name).first()
            if not employee:
                messagebox.showerror("Error", "Employee not found")
                return

            hashed_password = hash_password(password)

            # Check if the user already exists
            user = db.query(User).filter_by(username=username).first()
            if user:
                # Update the user's password and email
                user.employee_id = employee.id
                user.email = email
                user.password_hash = hashed_password
                messagebox.showinfo(
                    'Success', f'User information updated for {employee.fullname}')
                self.destroy()
            else:
                # Create a new user
                create_users(db, username=username, employee_id=employee.id,
                             password_hash=hashed_password, email=email)
                messagebox.showinfo(
                    'Success', f'New user created for {employee.fullname}')
                self.destroy()

            db.commit()
            self.master.master.approval_app_open = False

        except Exception as e:
            db.rollback()
            messagebox.showerror("Error", str(e))


class ApprovalApplication(tk.Toplevel):
    def __init__(self, main_app):
        super().__init__(main_app)
        self.title(f"ادارة الاعتمادات")
        self.main_app = main_app
        self.main_frame = ttk.Frame(self)
        self.tab_control = ttk.Notebook(self.main_frame, bootstyle=PRIMARY)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Define tab configuration: (tab_text, frame_class)
        tab_configs = [
            ('المستخدمين', AddUsersWindow),
            ('الاعتمادات', AddApprovalWindow),
            ('اعتماد الانجازات', AddTaskCompletion),
            ('إدارة المهام', AddTaskWindow),
        ]

        # Add tabs dynamically
        for tab_text, frame_class in tab_configs:
            self.add_tab(tab_text, frame_class)

    def add_tab(self, tab_text, frame_class):
        tab_frame = Frame(self.tab_control)
        self.tab_control.add(tab_frame, text=tab_text)
        tab_content = frame_class(tab_frame, self.main_app)
        tab_content.pack(fill=tk.BOTH, expand=True)
        self.tab_control.pack(expand=True, fill='both')

        # If the tab is AddApprovalWindow, update the title with the number of frames
        if isinstance(tab_content, AddApprovalWindow):
            frame_count = tab_content.get_frame_count()
            tab_text = f"{tab_text} ({frame_count})"
            self.tab_control.tab(
                len(self.tab_control.tabs()) - 1, text=tab_text)

    def get_tab_names(self):
        return [self.tab_control.tab(index, "text") for index in range(self.tab_control.index("end"))]


class AddProductWindow(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)

        self.main_app = main_app

        ttk.Label(self, text='اسم المنتج').grid(
            row=0, column=1, pady=10, padx=10)
        self.product_entry = ttk.Entry(self)
        self.product_entry.grid(row=0, column=0, pady=10, padx=10)

        ttk.Label(self, text='الكمية').grid(row=1, column=1, pady=10, padx=10)
        self.quantity_entry = ttk.Spinbox(self, from_=0, to=10000)
        self.quantity_entry.grid(row=1, column=0, pady=10, padx=10)

        ttk.Label(self, text='السعر').grid(row=2, column=1, pady=10, padx=10)
        self.price_entry = ttk.Spinbox(
            self, from_=0, to=10000, format='%02.2f')
        self.price_entry.grid(row=2, column=0, pady=10, padx=10)

        ttk.Label(self, text='الوصف').grid(row=3, column=1, pady=10, padx=10)
        self.desc_entry = tk.Text(self, height=5, width=40)
        self.desc_entry.grid(row=3, column=0, pady=10, padx=10)

        ttk.Label(self, text='باركود').grid(row=4, column=1, pady=10, padx=10)
        self.barcode_entry = tk.Entry(self)
        self.barcode_entry.grid(row=4, column=0, pady=10, padx=10)

        ttk.Button(self, text='إضافة منتج',
                   command=self.add_product_command).grid(row=5, columnspan=2, pady=10, padx=10)
        cols = ('اسم المنتج', 'الكمية', 'السعر', 'الوصف', 'باركود')
        self.tree = ttk.Treeview(self, bootstyle='primary')

        self.tree['columns'] = cols
        self.tree.heading('#0', text='ID')
        self.tree.column('#0', width=50)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.E)
            self.tree.grid(row=6, columnspan=2, padx=20, pady=20)

    #     # Add Update and Print buttons
        self.update_button = ttk.Button(
            self, text='تحديث', command=self.update_product_data)
        self.update_button.grid(row=7, columnspan=2, padx=10, pady=10)
        self.populate_treeview()

    def populate_treeview(self):
        # Clear the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Fetch contract data from the database and populate the Treeview
        products = db.query(Inventory).all()
        for product in products:
            self.tree.insert('', 'end', text=product.id, values=(
                product.product,
                product.quantity,
                product.price,
                product.desc,
                product.barcode,
            ))

    def update_product_data(self):
        try:
            # Get the selected contract from the Treeview and allow the user to update its details
            selected_item = self.tree.selection()
            if selected_item:
                # Get the contract ID from the selected item
                selected_produce_id = self.tree.item(selected_item[0], 'text')
                product = db.query(Inventory).filter_by(
                    id=int(selected_produce_id)).first()

                if product:
                    top_level_widget = Toplevel()
                    top_level_widget.title("تحديث المنتج")

                    ttk.Label(top_level_widget, text='اسم المنتج').pack(
                        pady=10, padx=10)
                    self.product_entry = tk.Entry(top_level_widget)
                    self.product_entry.insert(0, product.product)
                    self.product_entry.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text='الكمية').pack(
                        pady=10, padx=10)
                    self.product_quantity_entry = tk.Entry(top_level_widget)
                    self.product_quantity_entry.insert(0, product.quantity)
                    self.product_quantity_entry.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text='السعر').pack(
                        pady=10, padx=10)
                    self.product_price_entry = tk.Entry(top_level_widget)
                    self.product_price_entry.insert(0, product.price)
                    self.product_price_entry.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text='الوصف').pack(
                        pady=10, padx=10)
                    self.product_desc_entry = tk.Entry(top_level_widget)
                    self.product_desc_entry.insert(0, product.desc)
                    self.product_desc_entry.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text='باركود').pack(
                        pady=10, padx=10)
                    self.product_barcode_entry = tk.Entry(top_level_widget)
                    self.product_barcode_entry.insert(0, product.barcode)
                    self.product_barcode_entry.pack(pady=10, padx=10)

                    def save_updates():
                        product = self.product_entry.get()
                        quantity = self.product_quantity_entry.get()
                        price = self.product_price_entry.get()
                        desc = self.product_desc_entry.get()
                        barcode = self.product_barcode_entry.get()

                        try:
                            product_valdiation = InventoryModel(
                                product=product,
                                quantity=int(quantity),
                                price=float(price),
                                desc=desc,
                                barcode=barcode
                            )
                            update_product(db, id=selected_produce_id, product=product_valdiation.product, quantity=product_valdiation.quantity,
                                           price=product_valdiation.price, desc=product_valdiation.desc, barcode=product_valdiation.barcode)
                            messagebox.showinfo(
                                "نجاح العملية", "تم تحديث المنتج بنجاح")
                            self.populate_treeview()  # Refresh the Treeview to show updated data
                            top_level_widget.destroy()
                        except ValidationError as e:
                            self.show_validation_errors(e)
                        except Exception as e:
                            db.rollback()
                            messagebox.showerror(
                                "Error", f"Failed to update product: {str(e)}")

                    ttk.Button(top_level_widget, text='تحديث منتج',
                               command=save_updates).pack(pady=10, padx=10)
                else:
                    messagebox.showerror(
                        "Error", "No contract found for the selected ID")
            else:
                messagebox.showerror("Error", "No contract selected")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def add_product_command(self):
        try:
            product = self.product_entry.get().strip()
            if not product:
                messagebox.showerror('خطأ', 'يرجى عدم ترك الحقول فارغة')
                return
            quantity = int(self.quantity_entry.get())
            price = float(self.price_entry.get().strip())
            if not price:
                messagebox.showerror('خطأ', 'يرجى عدم ترك الحقول فارغة')
                return

            desc = self.desc_entry.get("1.0", tk.END).strip()
            barcode = self.barcode_entry.get()
            inventory = InventoryModel(product=product, quantity=int(
                quantity), price=float(price), desc=desc, barcode=barcode)
            create_product(db, product=inventory.product, quantity=inventory.quantity,
                           price=inventory.price, desc=inventory.desc, barcode=inventory.barcode)
            messagebox.showinfo("نجاح العملية", "تم إدخال المنتج بنجاح!")
            self.clear_entries()
            self.populate_treeview()
        except ValidationError as e:
            self.show_validation_errors(e)
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            self.destroy()

    def show_validation_errors(self, e):
        errors = e.errors()
        error_messages = "\n".join(
            [f"{error['loc'][0]}: {error['msg']}" for error in errors])
        messagebox.showerror("Validation Error", error_messages)

    def clear_entries(self):
        self.product_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.desc_entry.delete('1.0', tk.END)
        self.barcode_entry.delete(0, tk.END)


class AddCustomerWindow(Frame):
    def __init__(self, master, main_app, update_orders_callback):
        super().__init__(master)
        self.main_app = main_app
        self.update_orders_callback = update_orders_callback

        ttk.Label(self, text='اسم العميل').grid(
            row=0, column=1, pady=10, padx=10)
        self.customer_name_entry = tk.Entry(self)
        self.customer_name_entry.grid(row=0, column=0, pady=10, padx=10)

        ttk.Label(self, text='اسم الشركة').grid(
            row=1, column=1, pady=10, padx=10)
        self.customer_business_entry = tk.Entry(self)
        self.customer_business_entry.grid(row=1, column=0, pady=10, padx=10)

        ttk.Label(self, text='نوع النشاط').grid(
            row=2, column=1, pady=10, padx=10)
        self.business_type_entry = tk.Entry(self)
        self.business_type_entry.grid(row=2, column=0, pady=10, padx=10)

        ttk.Label(self, text='جوال العميل').grid(
            row=3, column=1, pady=10, padx=10)
        self.cusomer_phone_entry = tk.Entry(self)
        self.cusomer_phone_entry.grid(row=3, column=0, pady=10, padx=10)

        ttk.Label(self, text='العنوان').grid(row=4, column=1, pady=10, padx=10)
        self.cusomer_address_entry = tk.Entry(self)
        self.cusomer_address_entry.grid(row=4, column=0, pady=10, padx=10)

        ttk.Button(self, text='إضافة عميل', command=self.add_customer_command).grid(
            row=5, columnspan=2, pady=10, padx=10)

        cols = ('اسم العميل', 'اسم الشركة',
                'نوع النشاط', 'رقم الجوال', 'العنوان')
        self.tree = ttk.Treeview(self, bootstyle="primary")
        self.tree['columns'] = cols
        self.tree.heading('#0', text='ID')
        self.tree.column('#0', width=50)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.E)
        self.tree.grid(row=6, columnspan=2)

        self.update_button = ttk.Button(
            self, text='تحديث', command=self.update_customer_data)
        self.update_button.grid(row=7, columnspan=2, padx=10, pady=10)

        self.populate_treeview()

    def populate_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        customers = db.query(Customer).all()
        for customer in customers:
            self.tree.insert('', 'end', text=customer.id, values=(
                customer.name,
                customer.business_name,
                customer.business_type,
                customer.phone_number,
                customer.address
            ))

    def update_customer_data(self):
        try:
            selected_item = self.tree.selection()
            if selected_item:
                selected_contract_id = self.tree.item(selected_item[0], 'text')
                customer = db.query(Customer).filter_by(
                    id=int(selected_contract_id)).first()

                if customer:
                    top_level_widget = Toplevel()
                    top_level_widget.title("تحديث العميل")

                    ttk.Label(top_level_widget, text='اسم العميل').pack(
                        pady=10, padx=10)
                    self.customer_name_entry = ttk.Entry(top_level_widget)
                    self.customer_name_entry.insert(0, customer.name)
                    self.customer_name_entry.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text='اسم الشركة').pack(
                        pady=10, padx=10)
                    self.customer_business_entry = tk.Entry(top_level_widget)
                    self.customer_business_entry.insert(
                        0, customer.business_name)
                    self.customer_business_entry.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text='نوع النشاط').pack(
                        pady=10, padx=10)
                    self.business_type_entry = tk.Entry(top_level_widget)
                    self.business_type_entry.insert(0, customer.business_type)
                    self.business_type_entry.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text='جوال العميل').pack(
                        pady=10, padx=10)
                    self.cusomer_phone_entry = tk.Entry(top_level_widget)
                    self.cusomer_phone_entry.insert(0, customer.phone_number)
                    self.cusomer_phone_entry.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text='العنوان').pack(
                        pady=10, padx=10)
                    self.cusomer_address_entry = tk.Entry(top_level_widget)
                    self.cusomer_address_entry.insert(0, customer.address)
                    self.cusomer_address_entry.pack(pady=10, padx=10)

                    def save_updates():
                        customer = self.customer_name_entry.get()
                        business_name = self.customer_business_entry.get()
                        business_type = self.business_type_entry.get()
                        phone = self.cusomer_phone_entry.get()
                        address = self.cusomer_address_entry.get()
                        try:
                            phone_validation = CustomersModel(
                                phone_number=phone)
                            update_customer(db, id=selected_contract_id, name=customer, business_name=business_name,
                                            business_type=business_type, phone_number=phone_validation.phone_number, address=address)
                            messagebox.showinfo(
                                "نجاح العملية", "تم تحديث العميل بنجاح")
                            self.populate_treeview()
                            top_level_widget.destroy()
                        except ValidationError as e:
                            self.show_validation_errors(e)
                        except Exception as e:
                            db.rollback()
                            messagebox.showerror(
                                "Error", f"Failed to update customer: {str(e)}")

                    ttk.Button(top_level_widget, text='تحديث عقد',
                               command=save_updates).pack(pady=10, padx=10)
                else:
                    messagebox.showerror(
                        "Error", "No contract found for the selected ID")
            else:
                messagebox.showerror("Error", "No contract selected")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def add_customer_command(self):
        name = self.customer_name_entry.get()
        business_name = self.customer_business_entry.get()
        business_type = self.business_type_entry.get()
        phone_number = self.cusomer_phone_entry.get()
        address = self.cusomer_address_entry.get()
        if not name:
            messagebox.showerror('خطأ', 'يرجى ملئ الحقول')
            return
        if not business_name:
            messagebox.showerror('خطأ', 'يرجى ملئ الحقول')
            return
        if not phone_number:
            messagebox.showerror('خطأ', 'يرجى ملئ الحقول')
            return

        try:
            customer_data = {'phone_number': phone_number}
            validated_customer = CustomersModel(**customer_data)
            create_customer(db, name, business_name, business_type,
                            validated_customer.phone_number, address)
            messagebox.showinfo("نجاح العملية", "تمت إضافة العميل بنجاح")
            self.clear_entries()
            self.populate_treeview()
            self.update_orders_callback()  # Call the callback to update orders combobox
        except ValidationError as e:
            self.show_validation_errors(e)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add customer: {str(e)}")
            self.destroy()

    def show_validation_errors(self, e):
        errors = e.errors()
        error_messages = "\n".join(
            [f"{error['loc'][0]}: {error['msg']}" for error in errors])
        messagebox.showerror("Validation Error", error_messages)

    def clear_entries(self):
        self.customer_name_entry.delete(0, tk.END)
        self.customer_business_entry.delete(0, tk.END)
        self.business_type_entry.delete(0, tk.END)
        self.cusomer_phone_entry.delete(0, tk.END)
        self.cusomer_address_entry.delete(0, tk.END)


class AddMiantenence(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)

        self.main_app = main_app

        ttk.Label(self, text='معلومات الزيارة').grid(
            row=0, column=1, pady=10, padx=10)
        self.visit_info_combobox = ttk.Combobox(self, values=get_visit(db))
        self.visit_info_combobox.grid(row=0, column=0, pady=10, padx=10)

        ttk.Label(self, text='نوع النظام').grid(
            row=1, column=1, pady=10, padx=10)
        self.sysetm_type_combobox = ttk.Combobox(
            self, values=['انذار', 'إطفاء', 'مراقبة'])
        self.sysetm_type_combobox.grid(row=1, column=0, pady=10, padx=10)

        ttk.Label(self, text='القطعة المفحوصة').grid(
            row=2, column=1, pady=10, padx=10)
        self.product_checked_entry = ttk.Entry(self)
        self.product_checked_entry.grid(row=2, column=0, pady=10, padx=10)

        ttk.Label(self, text='حالة القطعة المفحوصة').grid(
            row=3, column=1, pady=10, padx=10)
        self.product_status_entry = ttk.Combobox(
            self, values=['سليم', 'غير سليم'])
        self.product_status_entry.grid(row=3, column=0, pady=10, padx=10)

        ttk.Label(self, text="تم الإصلاح:").grid(
            row=4, column=1, pady=10, padx=10)
        self.completed_var = tk.BooleanVar()
        self.completed_checkbox = ttk.Checkbutton(
            self, text="نعم", variable=self.completed_var)
        self.completed_checkbox.grid(row=4, column=0, pady=10, padx=10)

        ttk.Label(self, text='السعر').grid(row=5, column=1, pady=10, padx=10)
        self.product_price_entry = ttk.Spinbox(
            self, from_=1, to=10000000000, format='%02.2f')
        self.product_price_entry.grid(row=5, column=0, pady=10, padx=10)
        ttk.Button(self, text='اضافة صيانة',
                   command=self.add_maintnance).grid(row=6, columnspan=2, pady=10, padx=10)
        cols = ('معلومات الزيارة', 'نوع النظام', 'القطعة المفحوصة',
                'حالة القطعة المفحوصة', 'السعر', "تم الإصلاح")
        self.tree = ttk.Treeview(self, bootstyle="primary")
        self.tree['columns'] = cols
        self.tree.heading('#0', text='ID')
        self.tree.column('#0', width=50)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.E)
            self.tree.grid(row=7, columnspan=2)

        # Add Update and Print buttons
        self.update_button = ttk.Button(
            self, text='تحديث', command=self.update_miantenence_data)
        self.update_button.grid(
            row=8, column=1, padx=10, pady=10)
        self.pdf_button = ttk.Button(
            self, text='طباعة محضر السلامة', command=self.print_maintenence)
        self.pdf_button.grid(row=8, column=0, padx=10, pady=10)

        # Populate Treeview with contract data

        self.populate_treeview()

        # Fetch contract data from the database and populate the Treeview
    def populate_treeview(self):
        # Clear the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch contract data from the database and populate the Treeview
        maintenence = db.query(Maintenence).all()
        for m in maintenence:
            self.tree.insert('', 'end', text=m.id, values=(
                m.visit_id,
                m.seytem_type,
                m.tool,
                m.status,
                m.cost,
                'تم الإصلاح' if m.fixed == True else 'سليم' if m.status == 'سليم' else 'لم يتم الاصلاح بعد'
            ))

    def clear_entries(self):
        # self.visit_info_combobox.delete(0,tk.END)
        # self.sysetm_type_combobox.delete(0,tk.END)
        self.product_checked_entry.delete(0, tk.END)
        self.product_status_entry.delete(0, tk.END)
        self.product_price_entry.delete(0, tk.END)

    def add_maintnance(self):
        visit = self.visit_info_combobox.get()
        visit_id = int(visit.split('-')[0])
        seytem_type = self.sysetm_type_combobox.get()
        tool = self.product_checked_entry.get()
        status = self.product_status_entry.get()
        fixed = bool(self.completed_var.get())
        price = self.product_price_entry.get()
        try:
            mntc_validation = MaintenenceModel(cost=price)
            create_maintenance(db, visit_id, seytem_type,
                               tool, status, fixed, mntc_validation.cost)
            messagebox.showinfo("نجاح العملية", "تمت إضافة الصيانة بنجاح")
            self.clear_entries()
            self.populate_treeview()
            self.visit_info_combobox['values'] = get_visit(
                db)  # Refresh the Combobox values
        except ValidationError as e:
            show_validation_errors(e)
        except Exception as e:

            messagebox.showerror(
                "Error", f"Failed to add maintenence: {str(e)}")
            self.destroy()

    def print_maintenence(self):
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "No contract selected")
                return

            selected_mtnc_id = int(self.tree.item(selected_item, 'values')[0])

            minnce = db.query(Maintenence).filter_by(
                id=selected_mtnc_id).first()
            if not minnce:
                messagebox.showerror("Error", "Contract not found")
                return

            # date = session.query(Customer).filter_by(id=minnce.visits.visit_date).first()
            # if not date:
            #     messagebox.showerror("Error", "Customer not found")
            #     return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if not file_path:
                return

            # Check if the file path is obtained correctly

            # Ensure the parameters passed to create_pdf_contract are correct
            create_maintenence_pdf(minnce.id, output_file=file_path)
            messagebox.showinfo("Success", "PDF created successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_miantenence_data(self):
        try:
            # Get the selected contract from the Treeview and allow the user to update its details
            selected_item = self.tree.selection()
            if selected_item:
                # Get the contract ID from the selected item
                selected_m_id = self.tree.item(selected_item[0], 'text')
                maintenence = db.query(Maintenence).filter_by(
                    id=int(selected_m_id)).first()

                if maintenence:
                    top_level_widget = Toplevel()
                    top_level_widget.title("تحديث الصيانة")

                    ttk.Label(top_level_widget, text='حالة القطعة المفحوصة').pack(
                        pady=10, padx=10)
                    self.product_status_entry = ttk.Combobox(
                        top_level_widget, values=['سليم', 'غير سليم'])
                    self.product_status_entry.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text="تم الإصلاح:").pack(
                        pady=10, padx=10)
                    self.completed_var = tk.BooleanVar()
                    self.completed_checkbox = ttk.Checkbutton(
                        top_level_widget, text="نعم", variable=self.completed_var)
                    self.completed_checkbox.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text='السعر').pack(
                        pady=10, padx=10)
                    self.product_price_entry = ttk.Spinbox(
                        top_level_widget, from_=1, to=10000000000, format='%02.2f')
                    self.product_price_entry.pack(pady=10, padx=10)

                    self.product_status_entry.insert(0, maintenence.status)
                    self.completed_var.set(maintenence.fixed)
                    self.product_price_entry.insert(0, maintenence.cost)

                    def save_updates():
                        status = self.product_status_entry.get()
                        completed = self.completed_var.get()
                        price = self.product_price_entry.get()
                        try:

                            mntc_validation = MaintenenceModel(cost=price)
                            update_maintenence(
                                db, id=selected_m_id, status=status, fixed=completed, cost=mntc_validation.cost)
                            messagebox.showinfo(
                                "نجاح العملية", "تم تحديث الصيانة بنجاح")
                            self.populate_treeview()  # Refresh the Treeview to show updated data
                            top_level_widget.destroy()
                        except Exception as e:
                            db.rollback()
                            messagebox.showerror(
                                "Error", f"Failed to update maintenece: {str(e)}")

                    ttk.Button(top_level_widget, text='تحديث صيانة',
                               command=save_updates).pack(pady=10, padx=10)
                else:
                    messagebox.showerror(
                        "Error", "No contract found for the selected ID")
            else:
                messagebox.showerror("Error", "No contract selected")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


class AddVisitsWindow(Frame):
    def __init__(self, master, main_app, update_mntc):
        super().__init__(master)
        self.main_app = main_app
        self.update_mntc = update_mntc

        ttk.Label(self, text='اسم العميل').pack(pady=10, padx=10)
        self.customer_name_entry = ttk.Combobox(
            self, values=customers_have_contracts(db))
        self.customer_name_entry.pack(pady=10, padx=10)

        ttk.Label(self, text='تاريخ الزيارة').pack(pady=10, padx=10)
        self.date_visit_entry = DateEntry(self, startdate=NOW)
        self.date_visit_entry.pack(pady=10, padx=10)

        ttk.Label(self, text='المهندسين').pack(pady=10, padx=10)
        self.engineers_entry = tk.Listbox(self, selectmode=tk.MULTIPLE)
        self.populate_engineers()  # Populate the engineers list
        self.engineers_entry.pack(pady=10, padx=10)

        ttk.Button(self, text='إضافة زيارة',
                   command=self.add_visit_command).pack(pady=10, padx=10)

    def populate_engineers(self):
        # Get the list of engineers from the database or any other source
        # Assuming you have a function to get employee names
        engineers = get_employee_names(db)
        for engineer in engineers:
            self.engineers_entry.insert(tk.END, engineer)

    def add_visit_command(self):
        name = self.customer_name_entry.get().strip()
        visit_date = get_date(self.date_visit_entry)
        selected_engineers = self.engineers_entry.curselection()
        employees = [self.engineers_entry.get(
            index) for index in selected_engineers]
        if not name:
            messagebox.showerror('خطأ', 'يرجى إدخال اسم العميل')
            return

        if not visit_date:
            messagebox.showerror('خطأ', 'يرجى إدخال تاريخ الزيارة')
            return

        if not selected_engineers:
            messagebox.showerror('خطأ', 'يرجى اختيار المهندسين')
            return

        try:
            create_visit(db, name=name, visit_date=visit_date,
                         employees=employees)
            # Properly close the generator
            messagebox.showinfo("نجاح العملية", "تمت إضافة الزيارة بنجاح")
            self.clear_entries()
            self.update_mntc()
            # Refresh the Combobox values
            self.customer_name_entry['values'] = get_customers

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add visit: {str(e)}")
            self.destroy()

    def clear_entries(self):
        self.customer_name_entry.delete(0, tk.END)
        self.engineers_entry.selection_clear(0, tk.END)


class AddOrderWindow(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)

        self.main_app = main_app
        ttk.Label(self, text='اسم العميل').pack(pady=10, padx=10)
        self.customer_name_entry = ttk.Combobox(
            self, values=self.get_customers())
        self.customer_name_entry.pack(pady=10, padx=10)

        ttk.Label(self, text='المنتج').pack(pady=10, padx=10)
        self.order_entry = tk.Listbox(self)
        self.order_entry.pack(pady=10, padx=10)

        self.add_item_button = ttk.Button(
            self, text="إضافة منتج", command=self.add_item)
        self.add_item_button.pack(pady=10, padx=10)

        self.submit_button = ttk.Button(
            self, text="حفظ", command=self.submit_order)
        self.submit_button.pack(pady=10, padx=10)

        self.print_button = ttk.Button(
            self, text="طباعة الفاتورة", command=self.export_pdf)
        self.print_button.pack(pady=10, padx=10)

        self.current_order = None
        self.item_form = None

        cols = ('اسم العميل', 'عدد المنتجات', 'تاريخ الشراء')
        self.tree = ttk.Treeview(self, bootstyle="primary")
        self.tree['columns'] = cols
        self.tree.heading('#0', text='ID')
        self.tree.column('#0', width=50)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.E)
        self.tree.pack(expand=True, padx=20, pady=20)

        self.populate_treeview()
        ttk.Button(self, text="عرض الفاتورة",
                   command=self.print_receipt).pack(pady=10, padx=10)

    def get_customers(self):
        return [customer.name for customer in db.query(Customer).order_by(Customer.id.desc()).all()]

    def populate_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        orders = db.query(Order).all()
        for order in orders:
            self.tree.insert('', 'end', text=order.id, values=(
                order.customer.name,
                len(order.items),
                order.created_at
            ))

    def add_item(self):
        if not self.item_form or not self.item_form.winfo_exists():
            self.item_form = OrderItemForm(self, self.order_entry)
            self.item_form.protocol(
                "WM_DELETE_WINDOW", self.on_item_form_close)

    def on_item_form_close(self):
        self.item_form.destroy()
        self.item_form = None

    def submit_order(self):
        try:
            customer_name = self.customer_name_entry.get()
            customer = db.query(Customer).filter_by(name=customer_name).first()

            if not customer:
                messagebox.showerror("Error", "Customer not found")
                return

            order = create_order(db, customer.id)
            self.current_order = order

            for item in self.order_entry.get(0, tk.END):
                inventory_id, quantity = item.split(":")
                add_order_item(db, order.id, int(inventory_id), int(quantity))
                deduct_quantity(db, int(inventory_id), int(quantity))
            db.commit()

            messagebox.showinfo("Success", "Order submitted successfully!")
            self.clear_form()
            self.populate_treeview()
        except ValueError as ve:
            messagebox.showerror('error', ve)

    def clear_form(self):
        self.customer_name_entry.set('')
        self.order_entry.delete(0, tk.END)
        self.current_order = None

    def export_pdf(self):
        try:
            selection = self.tree.selection()
            if selection:
                selected_order_id = self.tree.item(selection[0], 'text')
                order = db.query(Order).filter_by(id=selected_order_id).first()
                if not order:
                    messagebox.showerror("Error", "Order not found")
                    return

                company = load_data.company_info
                inventory = get_inventory(order.id)

                title = 'عرض سعر' if order.customer.name == 'عرض سعر' else 'فاتورة ضريبية'
                customer_name_for_file = order.customer.name
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    initialfile=f"{customer_name_for_file}_{timestamp}",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
                )

                if not file_path:
                    return

                product = Product(inventory)
                new_pdf = CreatePdf(file_path)
                new_pdf.draw_header(get_images('logo', load_data),
                                    company.name, 'احد رفيدة', company.phone, 'خميس مشيط')
                new_pdf.draw_footer(
                    account_bankname=company.accounts[0].bank_name, account_fullname=company.accounts[0].account_fullname, account_iban=company.accounts[0].account_iban)
                new_pdf.draw_watermark(
                    get_images('water_mark', load_data))
                new_pdf.add_data(order, title, order.customer.name,
                                 order.customer.address, inventory, product)

                messagebox.showinfo(
                    "Success", f"PDF saved successfully at {file_path}")
                self.clear_form()
        except Exception as e:
            messagebox.showerror(
                "Error", f"An error occurred while exporting the PDF: {e}")

    def print_receipt(self):
        selection = self.tree.selection()
        if selection:
            selected_order_id = self.tree.item(selection[0], 'text')
            customer_name = self.customer_name_entry.get()
            order = db.query(Order).filter_by(id=selected_order_id).first()

            receipt_details = f"Customer: {customer_name}, Order ID: {order.id}\nItems:\n"
            total_price = 0
            for item in order.items:
                product_name = item.inventory.product
                quantity = item.quantity
                price = item.inventory.price
                total_item_price = quantity * price
                total_price += total_item_price
                receipt_details += f"- {product_name}: Quantity: {quantity}, Price: {price}, Total: {total_item_price}\n"

            tax = total_price * 0.15
            total_price_with_tax = total_price + tax
            receipt_details += f"Subtotal: {total_price}\nTax (15%): {tax}\nTotal Price (including tax): {total_price_with_tax}\n\n"

            receipt_window = Toplevel(self)
            receipt_window.title("Receipt")

            receipt_text = tk.Text(
                receipt_window, wrap="word", width=50, height=20)
            receipt_text.pack(fill="both", expand=True)

            receipt_text.insert("1.0", receipt_details)


class OrderItemForm(Toplevel):
    def __init__(self, master, listbox):
        super().__init__(master)
        self.listbox = listbox
        self.create_widgets()

    def create_widgets(self):
        self.search_entry = PlaceholderEntry(
            self, placeholder="البحث عن منتج...")
        self.search_entry.pack(padx=10, pady=10)

        self.inventory_label = ttk.Label(self, text="اختر منتج")
        self.inventory_label.pack(pady=10, padx=10)

        self.inventory_combobox = ttk.Combobox(self)
        self.inventory_items = get_inventory_items(db)
        self.inventory_combobox['values'] = [
            f"{i.id} - {i.product}" for i in self.inventory_items]
        self.inventory_combobox.pack(pady=10, padx=10)

        self.quantity_label = ttk.Label(self, text="الكمية")
        self.quantity_label.pack(pady=10, padx=10)

        self.quantity_entry = tk.Entry(self)
        self.quantity_entry.pack(pady=10, padx=10)

        self.add_button = ttk.Button(self, text="إضافة", command=self.add_item)
        self.add_button.pack(pady=10, padx=10)

        self.search_entry.bind('<KeyRelease>', self.update_list)

    def update_list(self, event):
        search_term = self.search_entry.get()
        filtered_items = [
            f"{item.id} - {item.product}" for item in self.inventory_items if search_term in item.product]
        self.inventory_combobox['values'] = filtered_items
        if filtered_items:
            self.inventory_combobox.current(0)

    def add_item(self):
        inventory_selection = self.inventory_combobox.get()
        if inventory_selection:
            inventory_id, product = inventory_selection.split(" - ", 1)
            quantity = self.quantity_entry.get().strip()
            if quantity.isdigit() and int(quantity) > 0 and quantity:
                self.listbox.insert(tk.END, f"{inventory_id}:{quantity}")
                self.master.item_form = None
                self.destroy()
            else:
                messagebox.showerror("Error", "ادخل كمية صالحة")
        else:
            messagebox.showerror("Error", "Please select an inventory item")


class AddContractWindow(Frame):
    def __init__(self, master, main_app):
        super().__init__(master)

        self.main_app = main_app

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text='اسم العميل').grid(
            row=0, column=1, pady=10, padx=10)
        self.customer_name = ttk.Combobox(
            self, values=self.get_only_customers())
        self.customer_name.grid(row=0, column=0, pady=10, padx=10)

        ttk.Label(self, text='وصف العقد').grid(
            row=1, column=1, pady=10, padx=10)
        self.contract_desc = ttk.Combobox(self, values=['تركيب', 'صيانة'])
        self.contract_desc.grid(row=1, column=0, pady=10, padx=10)

        ttk.Label(self, text='قيمة العقد').grid(
            row=2, column=1, pady=10, padx=10)
        self.total_payment = ttk.Spinbox(
            self, from_=1, to=100000000, format='%02.2f')
        self.total_payment.grid(row=2, column=0, pady=10, padx=10)

        ttk.Label(self, text='تاريخ بداية العقد').grid(
            row=3, column=1, pady=10, padx=10)
        self.contract_start_date = DateEntry(self, startdate=NOW)
        self.contract_start_date.grid(row=3, column=0, pady=10, padx=10)

        ttk.Label(self, text='تاريخ نهاية العقد').grid(
            row=4, column=1, pady=10, padx=10)
        self.contract_end_date = DateEntry(self, startdate=YEAR_AFTER)
        self.contract_end_date.grid(row=4, column=0, pady=10, padx=10)

        ttk.Label(self, text='غرامة التأخير').grid(
            row=5, column=1, pady=10, padx=10)
        self.delay_fine_Entry = ttk.Spinbox(self, from_=1, to=1000000000)
        self.delay_fine_Entry.grid(row=5, column=0, pady=10, padx=10)

        ttk.Label(self, text='مدة التنفيذ').grid(
            row=6, column=1, pady=10, padx=10)
        self.completion_Entry = tk.Entry(self)
        self.completion_Entry.grid(row=6, column=0, pady=10, padx=10)

        ttk.Label(self, text='دورة الزيارات لكل').grid(
            row=7, column=1, pady=10, padx=10)
        self.contract_visits = ttk.Combobox(
            self, values=['اسبوع', 'نصف شهر', 'شهر', 'شهرين', 'ثلاثة أشهر', 'ستة أشهر', 'سنة'])
        self.contract_visits.grid(row=7, column=0, pady=10, padx=10)
        ttk.Button(self, text='إضافة عقد',
                   command=self.add_contract_command).grid(row=8, columnspan=2, pady=10, padx=10)

        cols = ('الوصف', 'قيمة العقد', 'بداية العقد',
                'نهاية العقد', 'دورة الزيارات', 'غرامة التأخير')
        self.tree = ttk.Treeview(self, bootstyle="primary")
        self.tree['columns'] = cols
        self.tree.heading('#0', text='ID')
        self.tree.column('#0', width=50)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.E)
            self.tree.grid(row=9, columnspan=2, padx=20, pady=20)

        # Add Update and Print buttons
        self.update_button = ttk.Button(
            self, text='Update', command=self.update_contract)
        ttk.Button(self, text='طباعة العقد',
                   command=self.print_contract).grid(row=10, column=1, pady=10, padx=10)
        self.update_button.grid(row=10, column=0, padx=10, pady=10)
        self.populate_tree()

    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        contracts = db.query(Contract).all()
        for contract in contracts:
            self.tree.insert('', 'end', text=contract.id, values=(
                contract.description,
                contract.total_payment,
                contract.start_date,
                contract.end_date,
                contract.visit_cycle,
                contract.delay_fine
            ))

    def get_only_customers(self) -> List[str]:
        customers = db.query(Customer.name).filter(
            Customer.name != "عرض سعر").all()
        return [customer.name for customer in customers]

    def print_contract(self):
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "No contract selected")
                return

            selected_contract_id = self.tree.item(selected_item[0], 'text')
            # Debug statement

            contract = db.query(Contract).filter_by(
                id=int(selected_contract_id)).first()
            # Debug statement to check if contract is None

            if not contract:
                messagebox.showerror("Error", "Contract not found")
                return

            if not contract.customer:
                messagebox.showerror(
                    "Error", "Contract does not have an associated customer")
                return

            customer = db.query(Customer).filter_by(
                id=contract.customer.id).first()
            # Debug statement to check if customer is None

            if not customer:
                messagebox.showerror("Error", "Customer not found")
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile=f'{contract.customer.name}',
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if not file_path:
                return

            # Check if the file path is obtained correctly

            # Ensure the parameters passed to create_pdf_contract are correct
            create_setup_conditions(
                id=contract.id,
                condition_type=contract.description,
                output_file=file_path
            )

            messagebox.showinfo("Success", "PDF created successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_contract(self):
        try:
            # Get the selected contract from the Treeview and allow the user to update its details
            selected_item = self.tree.selection()
            if selected_item:
                # Get the contract ID from the selected item
                selected_contract_id = self.tree.item(selected_item[0], 'text')
                contract = db.query(Contract).filter_by(
                    id=int(selected_contract_id)).first()

                if contract:
                    top_level_widget = Toplevel()
                    top_level_widget.title("Update Contract")

                    ttk.Label(top_level_widget, text='اسم العميل').pack(
                        pady=10, padx=10)
                    customer_name_widget = ttk.Combobox(
                        top_level_widget, values=get_customers)
                    # Pre-select the current customer name
                    customer_name_widget.set(contract.customer_id)
                    customer_name_widget.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text='وصف العقد').pack(
                        pady=10, padx=10)
                    contract_desc_widget = ttk.Combobox(
                        top_level_widget, values=['تركيب', 'صيانة'])
                    # Pre-fill with the current description
                    contract_desc_widget.insert(0, contract.description)
                    contract_desc_widget.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text='قيمة العقد').pack(
                        pady=10, padx=10)
                    total_payment_widget = ttk.Spinbox(
                        top_level_widget, from_=1, to=100000000, format='%02.2f')
                    total_payment_widget.delete(0, tk.END)
                    # Pre-fill with the current total payment
                    total_payment_widget.insert(0, contract.total_payment)
                    total_payment_widget.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text='تاريخ بداية العقد').pack(
                        pady=10, padx=10)
                    contract_start_date_widget = DateEntry(
                        top_level_widget, startdate=contract.start_date)
                    # Pre-fill with the current start date
                    contract_start_date_widget.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text='تاريخ نهاية العقد').pack(
                        pady=10, padx=10)
                    contract_end_date_widget = DateEntry(
                        top_level_widget, startdate=contract.end_date)
                    contract_end_date_widget.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text='مدة التنفيذ').pack(
                        pady=10, padx=10)
                    completion_toplevel_Entry = tk.Entry(top_level_widget)
                    completion_toplevel_Entry.delete(0, tk.END)
                    completion_toplevel_Entry.insert(
                        0, contract.completion_period if contract.completion_period else '0')
                    completion_toplevel_Entry.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text='عدد الزيارات').pack(
                        pady=10, padx=10)
                    contract_visits_widget = ttk.Combobox(top_level_widget, values=[
                                                          'اسبوع', 'نصف شهر', 'شهر', 'شهرين', 'ثلاثة أشهر', 'ستة أشهر', 'سنة'])
                    # Pre-fill with the current visit cycle
                    contract_visits_widget.insert(0, contract.visit_cycle)
                    contract_visits_widget.pack(pady=10, padx=10)

                    ttk.Label(top_level_widget, text='غرامة التأخير').pack(
                        pady=10, padx=10)
                    delay_fine_spin = ttk.Spinbox(
                        top_level_widget, from_=1, to=100000000, format='%02.2f')
                    delay_fine_spin.delete(0, tk.END)
                    # Pre-fill with the current total payment
                    delay_fine_spin.insert(
                        0, contract.delay_fine if contract.delay_fine is not None else 0)
                    delay_fine_spin.pack(pady=10, padx=10)

                    def save_updates():
                        customer_id = customer_name_widget.get()
                        description = contract_desc_widget.get()
                        total_payment = float(total_payment_widget.get())
                        start_date = contract_start_date_widget.entry.get()
                        end_date = contract_end_date_widget.entry.get()
                        visit_cycle = contract_visits_widget.get()
                        completion = completion_toplevel_Entry.get()
                        delay_fine = float(delay_fine_spin.get())
                        try:
                            contract_validation = ContractModel(completion_period=int(
                                completion), delay_fine=float(delay_fine), total_payment=float(total_payment))
                            update_contract(db, id=selected_contract_id, customer_id=customer_id, description=description, total_payment=contract_validation.total_payment, start_date=start_date,
                                            end_date=end_date, visit_cycle=visit_cycle, completion_period=contract_validation.completion_period, delay_fine=contract_validation.delay_fine)
                            messagebox.showinfo(
                                "نجاح العملية", "تم تحديث العقد بنجاح")
                            self.populate_tree()  # Refresh the Treeview to show updated data
                        except ValueError:
                            messagebox('خطأ', 'يجب ان يكون رقما صالحا')
                        except Exception as e:
                            db.rollback()
                            messagebox.showerror(
                                "Error", f"Failed to update contract: {str(e)}")

                    ttk.Button(top_level_widget, text='تحديث عقد',
                               command=save_updates).pack(pady=10, padx=10)
                else:
                    messagebox.showerror(
                        "Error", "No contract found for the selected ID")
            else:
                messagebox.showerror("Error", "No contract selected")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def add_contract_command(self):
        customer_name = self.customer_name.get()
        contract_desc = self.contract_desc.get()
        total_payment = self.total_payment.get()
        start_date = get_date(self.contract_start_date)
        end_date = get_date(self.contract_end_date)
        completion = self.completion_Entry.get()
        visits = self.contract_visits.get()
        delay_fine = self.delay_fine_Entry.get()

        customer_name = self.customer_name.get()
        customer = db.query(Customer).filter_by(
            name=customer_name).first()

        try:
            contract_validation = ContractModel(completion_period=int(
                completion), delay_fine=float(delay_fine), total_payment=float(total_payment))
            create_contract(db, customer.id, contract_desc, contract_validation.total_payment, start_date,
                            end_date, contract_validation.completion_period, visits, contract_validation.delay_fine)
            # Properly close the generator
            messagebox.showinfo("نجاح العملية", "تمت إضافة العقد بنجاح")
            self.clear_entries()
            self.populate_tree()
        except ValidationError as e:
            show_validation_errors(e)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add contract: {str(e)}")
            self.destroy()

    def clear_entries(self):
        self.customer_name.delete(0, tk.END)
        self.contract_desc.delete(0, tk.END)
        self.total_payment.delete(0, tk.END)
        self.contract_visits.delete(0, tk.END)
        self.delay_fine_Entry.delete(0, tk.END)


class SalesApplication(Toplevel):
    def __init__(self, main_app):
        super().__init__(main_app)
        self.title("إدارة المبيعات")
        self.main_app = main_app
        self.main_frame = Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.tab_control = ttk.Notebook(self.main_frame, bootstyle="primary")
        self.tab_control.pack(expand=True, fill=tk.BOTH)

        # List of tabs and their associated windows
        tabs = [
            ('اضافة منتج جديد', AddProductWindow),
            ('اضافة عميل', AddCustomerWindow),
            ('إدارة الزيارات', AddVisitsWindow),
            ('إدارة العقود', AddContractWindow),
            ('إدارة الطلبات', AddOrderWindow),
            ('ادارة الصيانة', AddMiantenence)
        ]

        self.windows = {}
        for tab_name, window_class in tabs:
            self.add_tab(tab_name, window_class)

    def add_tab(self, tab_name, window_class):
        tab_frame = Frame(self.tab_control, bootstyle="primary")
        self.tab_control.add(tab_frame, text=tab_name)

        if tab_name == 'اضافة عميل':
            window_instance = window_class(
                tab_frame, self.main_app, self.update_customers)
        elif tab_name == 'إدارة الزيارات':
            window_instance = window_class(
                tab_frame, self.main_app, self.update_mntc)
        else:
            window_instance = window_class(tab_frame, self.main_app)

        window_instance.pack(fill=tk.BOTH, expand=True)
        self.windows[tab_name] = window_instance

    def update_mntc(self):
        visit_window = self.windows.get('ادارة الصيانة')
        if visit_window:
            visit_window.visit_info_combobox['values'] = get_visit(db)

    def update_customers(self):
        # Update customers in AddOrderWindow
        order_window = self.windows.get('إدارة الطلبات')
        if order_window:
            order_window.customer_name_entry['values'] = order_window.get_customers(
            )

        # Update customers in AddContractWindow
        contract_window = self.windows.get('إدارة العقود')
        if contract_window:
            contract_window.customer_name['values'] = contract_window.get_only_customers(
            )

    def get_tab_names(self):
        return [self.tab_control.tab(index, "text") for index in range(self.tab_control.index("end"))]


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
