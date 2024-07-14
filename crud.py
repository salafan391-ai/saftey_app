import hashlib
from sqlalchemy.orm import Session
from models import Customer, User, Employee, Vacation, Visits, Car, CarDriver, Task, Maintenence, MedicalInsurance, Notification, ToolRequest, Permission, Documents, WithdrawMoney, Order, OrderItems, Insurance, Inventory, CarDriverCache, CarPartsDetection, CarLisince, CarYearlyDetection, Contract
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from database import get_db
from typing import List


def create_employee(db: Session, fullname: str, birthdate: str, phone_number: str, career: str, salary: float):
    employee = Employee(fullname=fullname, birthdate=birthdate,
                        phone_number=phone_number, career=career, salary=salary)
    db.add(employee)
    db.commit()


def create_task(db: Session, employee_id: int, description: str, due_date: str, priority: str, assigned_by_id: int):
    task = Task(employee_id=employee_id, description=description,
                due_date=due_date, priority=priority, assigned_by_id=assigned_by_id)
    db.add(task)
    db.commit()


def create_vacation(db: Session, employee_id: int, start_date: str, period: int, reason: str):
    vacation = Vacation(employee_id=employee_id,
                        start_date=start_date, period=period, reason=reason)
    db.add(vacation)
    db.commit()


def create_notification(db: Session, employee_id: int, message: str, type: str, user_id: int):
    notification = Notification(
        employee_id=employee_id, message=message, type=type, user_id=user_id)
    db.add(notification)
    db.commit()


def create_request_tool(db: Session, employee_id: int, item: str, quantity: int, cost: float):
    request = ToolRequest(employee_id=employee_id,
                          item=item, quantity=quantity, cost=cost)
    db.add(request)
    db.commit()


def create_permission(db: Session, employee_id: int, start_date: str, start_time: str, end_time: str, reason: str, type: str):
    permission = Permission(employee_id=employee_id, start_date=start_date,
                            start_time=start_time, end_time=end_time, reason=reason, type=type)
    db.add(permission)
    db.commit()


def create_document(db: Session, employee_name, doc_name, document_data):
    employee = db.query(Employee).filter(
        Employee.fullname == employee_name).first()
    if not employee:
        raise ValueError(f"Employee with name {employee_name} does not exist.")
    new_document = Documents(doc_name=doc_name, document=document_data)
    employee.document.append(new_document)
    db.add(new_document)
    db.commit()


def create_withdraw(db: Session, employee_id: int, amount: float, reason: str):
    new_withdraw = WithdrawMoney(
        employee_id=employee_id,
        amount=amount,
        reason=reason,
    )
    db.add(new_withdraw)
    db.commit()


def create_employee_insurance(session: Session, employee_id: int, start_date: datetime, end_date: datetime):
    new_insurance = MedicalInsurance(employee_id=employee_id,
                                     start_date=start_date,
                                     end_date=end_date)
    session.add(new_insurance)
    session.commit()


def get_employee_documents(db: Session, employee_name):
    """
    Retrieve documents associated with a specific employee.
    :param db: Database session.
    :param employee_name: Name of the employee.
    :return: List of documents associated with the employee.
    """
    employee = db.query(Employee).filter(
        Employee.fullname == employee_name).first()
    if employee:
        return employee.document
    else:
        return []

# You can also modify the function to accept employee ID instead of name if you prefer.


def update_withdraw(db: Session, id: int, employee_id: int, amount: int, reason: str):
    try:
        # Fetch the contract by ID
        contract = db.query(WithdrawMoney).filter_by(id=id).first()

        if contract is None:
            raise ValueError("Contract not found")

        # Update contract fields
        contract.employee_id = employee_id
        contract.amount = amount
        contract.reason = reason

        # Commit changes
        db.commit()

    except ValueError as ve:
        db.rollback()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        return None


def fetch_employee_documents(employee_name):
    with get_db() as db:
        documents = get_employee_documents(db, employee_name)
        return documents


def get_employee_names(db: Session):
    employees = db.query(Employee).all()
    db.close()  # Close the session after use
    return [employee.fullname for employee in employees]


def create_product(db: Session, product: str, quantity: int, price: float, desc: str, barcode: str):
    new_product = Inventory(
        product=product, quantity=quantity, price=price, desc=desc, barcode=barcode)
    db.add(new_product)
    db.commit()


def create_customer(db: Session, name: str, business_name: str, business_type: str, phone_number: str, address: str):
    new_customer = Customer(name=name, business_name=business_name,
                            business_type=business_type, phone_number=phone_number, address=address)
    db.add(new_customer)
    db.commit()


def create_visit(db: Session, name: str, visit_date: str, employees: List[str]):
    # First, find the customer by name
    customer = db.query(Customer).filter(Customer.name == name).first()

    if customer:
        # Create the visit and associate it with the customer
        new_visit = Visits(customer_id=customer.id, visit_date=visit_date)

        # Retrieve the employee objects based on their names
        visit_employees = db.query(Employee).filter(
            Employee.fullname.in_(employees)).all()

        # Associate the visit with the employees
        new_visit.employees.extend(visit_employees)
        # Add the visit to the database
        db.add(new_visit)
        db.commit()
    else:
        raise ValueError(f"Customer with name '{name}' not found.")


def create_order(session: Session, customer_id):
    try:
        new_order = Order(customer_id=customer_id)
        session.add(new_order)
        session.commit()
        return new_order
    except Exception as e:
        session.rollback()
        return None


def add_order_item(db: Session, order_id: int, inventory_id: int, quantity: int):
    order_item = OrderItems(
        order_id=order_id, inventory_id=inventory_id, quantity=quantity)
    db.add(order_item)
    db.commit()


def get_customers(session: Session):
    costumer = session.query(Customer).order_by(Customer.id.desc()).all()
    print(costumer)
    return costumer


def get_only_customers(session: Session) -> List[str]:
    customers = session.query(Customer.name).filter(
        Customer.name != "عرض سعر").all()
    return [customer.name for customer in customers]


def get_inventory_items(session: Session):
    return session.query(Inventory).all()


def get_order_details(session: Session, id: int):
    return session.query(Order).filter_by(id=id).first()


def create_contract(db: Session,
                    customer_id: int,
                    description: str,
                    total_payment: float,
                    start_date: str,
                    end_date: str,
                    completion_period: str,
                    visit_cycle: str,
                    delay_fine: float):
    contract = Contract(customer_id=customer_id,
                        description=description,
                        total_payment=total_payment,
                        start_date=start_date,
                        end_date=end_date,
                        completion_period=completion_period,
                        visit_cycle=visit_cycle,
                        delay_fine=delay_fine)
    db.add(contract)
    db.commit()


def update_contract(db: Session,
                    id: int,
                    customer_id: int,
                    description: str,
                    total_payment: float,
                    start_date: str,
                    end_date: str,
                    visit_cycle: str,
                    completion_period: str,
                    delay_fine: float
                    ):
    try:
        # Fetch the contract by ID
        contract = db.query(Contract).filter_by(id=id).first()

        if contract is None:
            raise ValueError("Contract not found")

        # Update contract fields
        contract.customer_id = customer_id
        contract.description = description
        contract.total_payment = total_payment
        contract.start_date = start_date
        contract.end_date = end_date
        contract.visit_cycle = visit_cycle
        contract.completion_period = completion_period
        contract.delay_fine = delay_fine

        # Commit changes
        db.commit()
    except ValueError as ve:
        db.rollback()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        return None


def get_customer_names(session: Session):
    customers = session.query(Customer).all()
    return [customer.name for customer in customers]


def get_contracts(db: Session):
    return db.query(Contract).all()


def update_product(db: Session, id: int, product: str, quantity: int, price: float, desc: str, barcode: str):
    try:
        # Fetch the contract by ID
        update_product = db.query(Inventory).filter_by(id=id).first()

        if product is None:
            raise ValueError("Contract not found")
        # Update contract fields
        update_product.product = product
        update_product.quantity = quantity
        update_product.price = price
        update_product.desc = desc
        update_product.barcode = barcode
        # Commit changes
        db.commit()
    except ValueError as ve:
        db.rollback()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        return None


def get_visit(session: Session):
    visits = session.query(Visits).all()
    return [f"{visit.id}-{visit.visit_date}" for visit in visits]


def create_maintenance(session: Session, visit_id: int, seytem_type: str, tool: str, status: str, fixed: bool, cost: float):
    maintenance = Maintenence(
        visit_id=visit_id,
        seytem_type=seytem_type,
        tool=tool,
        status=status,
        fixed=fixed,
        cost=cost
    )
    session.add(maintenance)
    session.commit()


def update_maintenence(db: Session, id: int, status: str, cost: float, fixed: bool):
    try:
        # Fetch the contract by ID
        m = db.query(Maintenence).filter_by(id=id).first()

        if m is None:
            raise ValueError("Maintenence not found")

        # Update contract fields
        m.status = status
        m.cost = cost
        m.fixed = fixed

        # Commit changes
        db.commit()
    except ValueError as ve:
        db.rollback()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        return None


def customers_have_contracts(db: Session) -> List[str]:
    """Returns a list of customer names who have contracts."""
    return [contract.customer.name for contract in db.query(Contract).all()]


def get_employee_id(db: Session, employee):
    employee_id = db.query(Employee).filter_by(fullname=employee).first().id
    return employee_id


def get_employee_details(db: Session):
    employees = db.query(Employee).all()
    return [(employee.fullname, employee.career) for employee in employees]


def get_none_users(session: Session):
    employees = session.query(Employee).all()
    return [i.fullname for i in employees if i.user is None]


def create_car(db: Session,
               make: str,
               model: str,
               year: int,
               driving_range: int,
               cost: float,
               plate_letters: str,
               plate_numbers: str,
               buy_date: str):
    try:
        # Ensure the buy_date is a date object
        car = Car(
            make=make,
            model=model,
            year=year,
            driving_range=driving_range,
            cost=cost,
            plate_letters=plate_letters,
            plate_numbers=plate_numbers,
            buy_date=buy_date,
        )

        db.add(car)
        db.commit()

    except Exception as e:
        db.rollback()
        raise e


def create_car_yearly_detection(db: Session, car_id: int, startdate: datetime, enddate: datetime):
    try:
        car_yearly_detection = CarYearlyDetection(
            car_id=car_id,
            startdate=startdate,
            enddate=enddate
        )
        db.add(car_yearly_detection)
        db.commit()

    except Exception as e:
        db.rollback()
        raise e


def create_car_insurance(db: Session, car_id: int, start_date: datetime, end_date: datetime, company_name: str):
    try:
        insurance = Insurance(
            car_id=car_id,
            start_date=start_date,
            end_date=end_date,
            company_name=company_name
        )
        db.add(insurance)
        db.commit()

    except Exception as e:
        db.rollback()
        raise e


def create_car_license(db: Session, car_id: int, serial_number: str, lisince_expiry: datetime):
    try:
        car_license = CarLisince(
            car_id=car_id,
            serial_number=serial_number,
            lisince_expiry=lisince_expiry
        )
        db.add(car_license)
        db.commit()

    except Exception as e:
        db.rollback()
        raise e


def create_car_parts_detection(db: Session, car_id: int, driving_range: int, notes: str, status: str, is_valid: bool):
    try:
        car_parts_detection = CarPartsDetection(
            car_id=car_id,
            driving_range=driving_range,
            notes=notes,
            status=status,
            is_valid=is_valid
        )
        db.add(car_parts_detection)
        db.commit()

    except Exception as e:
        db.rollback()
        raise e


def create_car_driver(db: Session, employee_id: int, date: datetime, lisince_expiry_date: datetime, lisince_number: str, detection_id: int):
    try:
        car_driver = CarDriver(
            employee_id=employee_id,
            date=date,
            lisince_number=lisince_number,
            lisince_expiry_date=lisince_expiry_date,
            detection_id=detection_id
        )
        db.add(car_driver)
        db.commit()

    except Exception as e:
        db.rollback()
        raise e


def car_detection_false(db: Session, id: int):
    try:
        valid = db.query(CarPartsDetection).filter_by(id=id).first()
        valid.is_valid = False
        db.commit()
    except Exception as e:
        db.rollback()
        raise e


def get_cars(db: Session):
    cars = db.query(Car).all()
    return [f"{c.id}-{c.make}-{c.year}" for c in cars]


def create_car_drivers_cache(db: Session, text: str):
    caches = CarDriverCache(
        text=text
    )
    db.add(caches)
    db.commit()


def delete_driver_crud(db: Session, id: int):
    try:
        # Query the driver
        driver = db.query(CarDriver).get(id)

        # Check if the driver exists
        if driver is None:
            return {"error": "Driver not found"}

        # Delete the driver
        db.delete(driver)

        # Commit the transaction
        db.commit()

        return {"message": "Driver deleted successfully"}

    except SQLAlchemyError as e:
        # Handle database errors
        db.rollback()
        return {"error": str(e)}

    except Exception as e:
        # Handle any other unexpected errors
        db.rollback()
        return {"error": str(e)}


def update_car_driver(db: Session, id: int, employee_id: int, date: datetime, lisince_expiry_date: str, lisince_number: str, detection_id: int):
    try:
        # Fetch the contract by ID
        car_driver = db.query(CarDriver).filter_by(id=id).first()

        if car_driver is None:
            raise ValueError("Contract not found")

        # Update contract fields
        car_driver.employee_id = employee_id
        car_driver.date = date
        car_driver.lisince_expiry_date = lisince_expiry_date
        car_driver.lisince_number = lisince_number
        car_driver.detection_id = detection_id

        # Commit changes
        db.commit()
    except ValueError as ve:
        db.rollback()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        return None


def get_detection_id(db: Session):
    detection = db.query(CarPartsDetection).all()
    return [f"{d.id}-{d.car.make}-{d.car.model}" for d in detection if d.is_valid == True]


def create_customer(db: Session, name: str, business_name: str, business_type: str, phone_number: str, address: str):
    new_customer = Customer(name=name, business_name=business_name,
                            business_type=business_type, phone_number=phone_number, address=address)
    db.add(new_customer)
    db.commit()


def update_customer(db: Session, id: int, name: str, business_name: str, business_type: str, phone_number: str, address: str):
    try:
        # Fetch the contract by ID
        customer = db.query(Customer).filter_by(id=id).first()

        if customer is None:
            raise ValueError("Contract not found")

        # Update contract fields
        customer.name = name
        customer.business_name = business_name
        customer.business_type = business_type
        customer.phone_number = phone_number
        customer.address = address

        # Commit changes
        db.commit()
    except ValueError as ve:
        db.rollback()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        return None


def hash_password(password):
    """
    Hashes the password using SHA-256 algorithm.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(input_password, stored_hashed_password):
    """
    Checks if the input password matches the stored hashed password.
    """
    input_password_hash = hash_password(input_password)
    return input_password_hash == stored_hashed_password


def create_users(session: Session, username: str, email: str, password_hash: str, employee_id: int):
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        employee_id=employee_id
    )

    session.add(user)
    session.commit()


def get_active_cars(session: Session):
    cars = session.query(Car).all()
    current_date = datetime.now().date()
    active_cars = []
    for car in cars:
        if car.car_parts and car.insurance and car.yearly_detection:
            if car.car_parts[-1].lisince_expiry > current_date and car.insurance[-1].end_date > current_date and car.yearly_detection[-1].enddate > current_date:
                active_cars.append(f"{car.id}-{car.make}-{car.year}")
    return active_cars


def deduct_quantity(db: Session, inventory_id: int, quantity: int):
    try:
        # Query the inventory item
        inventory = db.query(Inventory).filter_by(id=inventory_id).one()
        if inventory.quantity < quantity:
            raise ValueError(
                f"{inventory.product} غير متوفر . المتوفر فقط:  {inventory.quantity}, المطلوب: {quantity}")

        # Update the quantity
        inventory.quantity -= quantity

    except Exception as e:
        db.rollback()
        raise e
