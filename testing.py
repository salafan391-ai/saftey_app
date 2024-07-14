from models import OrderItems, Contract, Maintenence, User


from database import db_session
# from datetime import datetime
db = db_session()
# budget = 0
# item_sales = db.query(OrderItems).all()
# contract_sales = db.query(Contract).all()
# mntc_sales = db.query(Maintenence).all()
# for item, contract, mntc in zip(item_sales, contract_sales, mntc_sales):
#     budget += item.inventory.price
#     budget += contract.total_payment
#     budget += mntc.cost
# print(budget)
# salaries = db.query(Employee).all()
# for salary in salaries:
#     budget -= int(salary.salary)
# print(budget)
# print(datetime.now().month)
user2 = db.query(User).filter_by(id=1).one()
print(user2.employee.vacations)
