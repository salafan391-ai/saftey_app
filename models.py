from sqlalchemy import (Column,
                        Integer,
                        String,
                        Date,
                        LargeBinary,
                        ForeignKey,
                        func,
                        Numeric,
                        Enum,
                        Boolean,
                        Float,
                        DateTime,
                        Time, Table, Text,
                        )
from sqlalchemy.orm import relationship, declarative_base, backref, Mapped, mapped_column
from typing import List


Base = declarative_base()


visit_employee_association = Table(
    'visit_employee_association',
    Base.metadata,
    Column('visit_id', Integer, ForeignKey('visits.id')),
    # Ensure the table name matches
    Column('employee_id', Integer, ForeignKey('employees.id'))
)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=False)
    employee_id = Column(Integer, ForeignKey(
        'employees.id'), nullable=False, unique=True)
    employee = relationship('Employee', back_populates='user')
    notifications = relationship('Notification', back_populates='user')


association_table = Table('association', Base.metadata,
                          Column('employee_id', Integer,
                                 ForeignKey('employees.id')),
                          Column('document_id', Integer,
                                 ForeignKey('documents.id'))
                          )


class Documents(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_name = Column(String, nullable=True)
    document = Column(LargeBinary, nullable=True)
    employees = relationship('Employee', secondary=association_table,
                             back_populates='document')  # Relationship to Employees


class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fullname = Column(String, nullable=False)
    birthdate = Column(Date, nullable=True)
    phone_number = Column(String, nullable=False)
    document_id = Column(Integer, ForeignKey('documents.id'))
    career = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=True, server_default=func.now())
    salary = Column(Numeric, nullable=False)
    document = relationship(
        'Documents', secondary=association_table, back_populates='employees')
    vacations = relationship("Vacation", back_populates="employee")
    permissions = relationship("Permission", back_populates="employee")
    notifications = relationship("Notification", back_populates="employee")
    tool_requests = relationship("ToolRequest", back_populates="employee")
    tasks = relationship(
        "Task", foreign_keys="[Task.employee_id]", back_populates="employee")
    tasks_assigned = relationship(
        "Task", foreign_keys="[Task.assigned_by_id]", back_populates="assigner")
    withdraw_money = relationship('WithdrawMoney', back_populates='employee')
    visits = relationship(
        'Visits', secondary=visit_employee_association, back_populates='employees')
    # One-to-One relationship
    user = relationship('User', uselist=False, back_populates='employee')
    medical_insurance = relationship(
        'MedicalInsurance', back_populates='employee')


class MedicalInsurance(Base):
    __tablename__ = 'medical_insurance'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    employee = relationship('Employee', back_populates='medical_insurance')


class Vacation(Base):
    __tablename__ = 'vacations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    start_date = Column(Date, nullable=False)
    period = Column(Numeric, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(Enum('معتمد', 'مرفوض'), nullable=True)
    employee = relationship('Employee', back_populates='vacations')

    def __repr__(self):
        return f"طلب إجازة {self.employee.fullname}\n بداية الاجازة {self.start_date}\n المدة {round(self.period)}"


class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    start_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(Enum('معتمد', 'مرفوض'), nullable=True)
    type = Column(Enum('مرض', 'أمر شخصي', 'آخر'), nullable=False)
    employee = relationship('Employee', back_populates='permissions')

    def __repr__(self):
        return f"استئذان {self.employee.fullname}\n بتاريخ {self.start_date}\n من {self.start_time}\n الى {self.end_time}\n السبب {self.reason}"


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    message = Column(String, nullable=False)
    type = Column(Enum('إنذار', 'تذكير', 'آخر'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, nullable=True, server_default=func.now())
    employee = relationship('Employee', back_populates='notifications')
    user = relationship('User', back_populates='notifications')

    def __repr__(self):
        return f"{self.employee.fullname} لقد تم لفت الانتبهاه اليك نوع اللفت {self.type}"


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    description = Column(String, nullable=False)
    due_date = Column(Date, nullable=True)
    priority = Column(Enum('منخفض', 'متوسط', 'عالي'), nullable=False)
    status = Column(Enum('قيد القبول', 'قيد العمل'),
                    nullable=False, default='قيد القبول')
    # Rename the column to avoid ambiguity
    assigned_by_id = Column(Integer, ForeignKey('employees.id'))
    completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=True, server_default=func.now())
    employee = relationship('Employee', foreign_keys=[
                            employee_id], back_populates='tasks')
    assigner = relationship('Employee', foreign_keys=[
                            assigned_by_id], back_populates='tasks_assigned')

    def __repr__(self):
        return f"وصف المهمة {self.description}\n اخر تاريخ للانجاز {self.due_date}\n الاولوية {self.priority}"


class ToolRequest(Base):
    __tablename__ = 'tool_requests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    item = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    cost = Column(Float, nullable=True)  # Added cost field
    status = Column(Enum('معتمد', 'مرفوض'), nullable=True)
    created_at = Column(DateTime, nullable=True, server_default=func.now())
    employee = relationship('Employee', back_populates='tool_requests')

    def __repr__(self):
        return f"{self.employee.fullname}\n المنتج المطلوب {self.item}\n التكلفة {self.cost}\n الكمية {self.quantity}"


class WithdrawMoney(Base):
    __tablename__ = 'withdraw_money'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    amount = Column(Float, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(Enum('معتمد', 'مرفوض'), nullable=True)
    employee = relationship('Employee', back_populates='withdraw_money')

    def __repr__(self):
        return f"طلب مصروف {self.employee.fullname}\n المبلغ المطلوب {self.amount}\n سبب الطلب {self.reason}"


class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    desc = Column(Text, nullable=True)
    barcode = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    business_name = Column(String, nullable=True)
    business_type = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class Maintenence(Base):
    __tablename__ = 'maintenences'
    id = Column(Integer, primary_key=True, autoincrement=True)
    seytem_type = Column(String(50), nullable=False)
    tool = Column(String, nullable=False)
    status = Column(String, nullable=False)
    fixed = Column(Boolean)
    cost = Column(Float, nullable=False)
    visit_id = Column(Integer, ForeignKey('visits.id'))
    visits = relationship('Visits', back_populates='maintenences')


class Visits(Base):
    __tablename__ = 'visits'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    visit_date = Column(Date, nullable=True)
    employees = relationship(
        'Employee', secondary=visit_employee_association, back_populates='visits')
    maintenences = relationship('Maintenence', back_populates='visits')


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    created_at = Column(DateTime, server_default=func.now())
    customer = relationship("Customer", backref="orders")
    # Specify back_populates
    items = relationship("OrderItems", back_populates="order")


class OrderItems(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    inventory_id = Column(Integer, ForeignKey('inventory.id'))
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    # Specify back_populates
    order = relationship("Order", back_populates="items")
    inventory = relationship("Inventory", backref="order_items")


class Contract(Base):
    __tablename__ = 'contracts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    description = Column(Text, nullable=True)
    total_payment = Column(Float, nullable=False)
    delay_fine = Column(Float, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    visit_cycle = Column(String)
    completion_period = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    customer = relationship("Customer", backref="contracts")


class Car(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True, autoincrement=True)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    driving_range = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    plate_letters = Column(String, nullable=False)
    plate_numbers = Column(String, nullable=False)
    buy_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    car_parts_detection = relationship('CarPartsDetection', backref='car')


class CarYearlyDetection(Base):
    __tablename__ = 'yearly_detection'
    id = Column(Integer, primary_key=True, autoincrement=True)
    car_id = Column(Integer, ForeignKey('cars.id'))
    startdate = Column(Date, nullable=False)
    enddate = Column(Date, nullable=False)
    employee = relationship('Car', backref='yearly_detection')


class Insurance(Base):
    __tablename__ = 'insurance'
    id = Column(Integer, primary_key=True, autoincrement=True)
    car_id = Column(Integer, ForeignKey('cars.id'))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    company_name = Column(String, nullable=False)
    car = relationship('Car', backref='insurance')


class CarLisince(Base):
    __tablename__ = 'car_license'
    id = Column(Integer, primary_key=True, autoincrement=True)
    car_id = Column(Integer, ForeignKey('cars.id'))
    serial_number = Column(String, nullable=False)
    lisince_expiry = Column(Date, nullable=False)
    car = relationship('Car', backref='car_parts')


class CarPartsDetection(Base):
    __tablename__ = 'car_parts_detection'
    id = Column(Integer, primary_key=True, autoincrement=True)
    car_id = Column(Integer, ForeignKey('cars.id'))
    driving_range = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    is_valid = Column(Boolean, nullable=True, default=True)


class CarDriver(Base):
    __tablename__ = 'car_drivers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    detection_id = Column(Integer, ForeignKey('car_parts_detection.id'))
    date = Column(Date, nullable=False)
    lisince_expiry_date = Column(Date, nullable=True)
    lisince_number = Column(String, nullable=True)
    employee = relationship('Employee', backref='car_drivers')
    car_parts_detection = relationship(
        'CarPartsDetection', backref='car_driver')


class CarDriverCache(Base):
    __tablename__ = 'car_drivers_cache'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text)
    created_at = Column(Date)
