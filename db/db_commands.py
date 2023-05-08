from sqlalchemy import extract, func
from sqlalchemy.exc import IntegrityError
from datetime import date, timedelta

from db.db_connect import session
from services import RawService, AddService


def get_all_raw_services_name(id: int):
    """Получаем список услуг сотрудника для вывода кнопок клавиатуры"""
    res = session.query(RawService).filter(RawService.id_employee == id)
    names = [row.service_name for row in res]
    return names


def add_complite_service(data: dict):
    """Добовляем оказанную услугу"""
    res = session.query(RawService).filter(
        RawService.id_employee == data['id_employee'],
        RawService.service_name == data['service_name']
    )

    if int(data['discount']) >= 0:
        sum_after_discount = int(data['price']) / 100 * (100-int(data['discount']))
        sum_for_employee = sum_after_discount / 100 * res[0].fix_percent
    else:
        sum_for_employee = int(data['price']) / 100 * res[0].fix_percent

    service = AddService(
        service=res[0].id,
        price=data['price'],
        sum_for_employee=sum_for_employee,
        discount=data['discount'],
        id_employee=data['id_employee']
    )
    session.add(service)

    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()  # откатываем
        return False


def add_raw_service(data: dict):
    """Добавляем новый вид услуги с индивидуальным процентом"""
    raw_service = RawService(
        service_name=data['service_name'],
        fix_percent=data['fix_percent'],
        id_employee=data['id_employee']
    )
    session.add(raw_service)

    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()  # откатываем
        return False


def get_services_for_day(day: str, id_employee: int):
    def result(set_day):
        res = session.query(
            AddService.id,
            RawService.service_name,
            AddService.sum_for_employee,
            AddService.discount,
            AddService.date_add
        ).filter(
            RawService.id == AddService.service,
            AddService.date_add == set_day,
            AddService.id_employee == id_employee
        )
        return res
    if day == 'Сегодня':
        return result(date.today())
    elif day == 'Вчера':
        return result(date.today() - timedelta(days=1))


def get_services_for_month(num_month: int, id_employee: int):
    res = session.query(
        AddService.id,
        RawService.service_name,
        AddService.sum_for_employee,
        AddService.discount,
        AddService.date_add
    ).filter(
        RawService.id == AddService.service,
        extract('month', AddService.date_add) == num_month,
        AddService.id_employee == id_employee
    )
    return res


def get_last_notes(id_employee: int):
    res = session.query(
        AddService.id,
        RawService.service_name,
        AddService.sum_for_employee,
        AddService.discount,
        AddService.date_add
    ).filter(
        RawService.id == AddService.service,
        AddService.id_employee == id_employee
    )[:10]
    return res


def get_money_for_month(id: int, month: int):
    res = session.query(
        func.sum(AddService.sum_for_employee)
    ).filter(
        AddService.id_employee == id,
        extract('month', AddService.date_add) == month
    ).one()[0] or 0
    return res
