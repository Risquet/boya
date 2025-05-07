from django.db.utils import IntegrityError
from api.models import Parameter, Data, Buoy, ActionItems
from datetime import datetime
from pytz import timezone
from math import isnan
import os


def isNoneOrEmpty(value):
    """
    Check if a value is None or empty
    """
    return value is None or value == ""

def formatUTCDateTime(milliseconds):
    """
    Format date and time in UTC timezone
    """
    dt_object = datetime.fromtimestamp(milliseconds / 1000)
    return dt_object.strftime("%d/%m/%Y %H:%M")

def formatLocalDateTime(milliseconds):
    """
    Format date and time in Havana timezone
    """
    havana_tz = timezone('Cuba')
    havana_time = havana_tz.localize(datetime.utcfromtimestamp(milliseconds / 1000))
    return havana_time.strftime('%d/%m/%Y %H:%M')

def value_is_in_range(value, timestamp, parameter, buoy, errors):
    """
    Check if values are in range
    """
    if parameter.min is None or parameter.max is None:
        return True
    if value < parameter.min or value > parameter.max:
        result = ActionItems.objects.create(
            timestamp=timestamp, error="El valor del parámetro está fuera del rango.", parameter_id=parameter.id, buoy_id=buoy.id)
        errors.append(result)
        return False
    return True

def value_is_a_number(value, timestamp, parameter, buoy, errors):
    """
    Check if value is a number
    """
    if isnan(value):
        result = ActionItems.objects.create(
            timestamp=timestamp, error="El valor del parámetro no es un número.", parameter_id=parameter.id, buoy_id=buoy.id)
        errors.append(result)
        return True
    return False


def save_data_individual(values, buoy, parameter):
    """
    Save data individually
    """
    created_count = 0
    updated_count = 0
    for i in values.items():
        try:
            [data, created] = Data.objects.update_or_create(timestamp=i[0], value=i[1], parameter_id=parameter.id, buoy_id=buoy.id)
            # if inserted successfully increment count
            if created:
                created_count = created_count + 1
            else:
                updated_count = updated_count + 1
        except Exception as error:
            result = ActionItems.objects.create(
                timestamp=i[0], error=f"Error al intentar insertar los datos: {error}", parameter_id=parameter.id, buoy_id=buoy.id)
    return [created_count, updated_count]


def save_data(data, buoy_id, job):
    """
    Receive data from the ui in a json file and insert it into the database
    """
    create_count = 0
    update_count = 0
    buoy = Buoy.objects.get(id=buoy_id)
    errors = []
    for key, values in data.items():
        description = key.split(" ")
        # special case because data is not in the same format
        if (description[0] == "waterTempMultiprobe"):
            name = description[0]
            # unit of measure is the last parameter
            uom = [description.pop(), description.pop()]
            uom.reverse()
            uom = " ".join(uom)
        else:
            # unit of measure is the last parameter
            uom = description.pop()
            # name is the rest of the parameters joined by a space
            name = " ".join(description)
        parameter = Parameter.objects.filter(name=name).first()
        if parameter is None:
            parameter = Parameter.objects.create(name=name, fullname=name, description=name, uom=uom)
        buoy.parameters.add(parameter)
        objects = []
        for i in values.items():
            errors = ""
            isNanN = value_is_a_number(i[1], i[0], parameter, buoy, errors)
            if not isNanN:
                value_is_in_range(i[1], i[0], parameter, buoy, errors)
            else:
                errors = errors + "NaN"
            objects.append(Data(timestamp=i[0], value=i[1], parameter_id=parameter.id, buoy_id=buoy_id, errors=errors))
        try:
            # get batch size from environment
            batch_size = int(os.environ.get('BATCH_SIZE', 100))
            result = Data.objects.bulk_create(objects, batch_size, ignore_conflicts=False, update_conflicts=True, update_fields=['value'], unique_fields=['parameter_id', 'buoy_id', 'timestamp'])
            # if inserted successfully increment count
            create_count = create_count + len(result)
            job.current = create_count
            job.save()
        except IntegrityError as error:
            result = ActionItems.objects.create(timestamp=None, error=f"Error al intentar insertar los datos: {error}", parameter_id=parameter.id, buoy_id=buoy.id)
            [created, updated] = save_data_individual(values, buoy, parameter)
            create_count = create_count + created
            update_count = update_count + updated
            job.current = create_count + update_count
            job.save()
    return [create_count, update_count, errors]
