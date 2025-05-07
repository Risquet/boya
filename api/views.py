from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.views import APIView
from rest_framework import status, viewsets, pagination
from django import forms
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from api.serializers import ParameterSerializer, DataSerializer, BuoySerializer
from api.models import Parameter, Data, Buoy, UploadDataJob
from api.helpers import isNoneOrEmpty, formatLocalDateTime, formatUTCDateTime, save_data
from datetime import datetime
from math import isnan
import csv, json
import numpy  as np


TWELVE_HOURS_IN_MILLISECONDS = 12 * 60 * 60 * 1000

class ResponseInfo(object):
    """
    Response object
    """

    def __init__(self, user=None, **args):
        self.response = {
            "data": args.get("data", []),
            "message": args.get("message", ""),
            "messageType": args.get("messageType", "success"),
        }

class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Permission class to allow only authenticated users to perform write operations
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

class UploadFileForm(forms.Form):
    """
    Form to upload a file
    """
    file = forms.FileField()


def userView(request):
    """
    View to check if user is authenticated
    """
    if not request.user.is_authenticated:
        return JsonResponse({"message": "User is not authenticated."}, status=401)
    return JsonResponse({"message": "User is authenticated."}, status=200)


@login_required(login_url='/login')
def roleView(request):
    """
    View to check if user is superuser
    """
    if request.user.is_staff:
        return JsonResponse({"message": "staff"}, status=200)
    if request.user.is_superuser:
        return JsonResponse({"message": "superuser"}, status=200)
    return JsonResponse({"message": "client"}, status=200)


@login_required(login_url='/login')
def insertDataView(request, buoy_id):
    """
    View to upload a file
    """
    # check if user is authenticated and is superuser
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({"message": "No tiene permiso para realizar esta acción."}, status=403)
    try:
        # check if there is an existing job
        job = UploadDataJob.objects.filter(buoy_id=buoy_id, status="In Progress").last()
        if (job is not None):
            message = "Ya hay un proceso de carga de datos en progreso. Por favor espere a que termine."
            response = {
                "data": [],
                "message": message,
                "messageType": "error",
            }
            return JsonResponse(response)

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = request.FILES.get("file")
                data = json.loads(file.read())
                total_data = sum([len(values) for (_, values) in data.items()])
                job = UploadDataJob.objects.create(
                    buoy_id=buoy_id, current=0, total=total_data, status="In Progress", start_time=datetime.now())
                [created, updated, errors] = save_data(data, buoy_id, job)
                message = "Se han insertado " + \
                    str(created) + " datos correctamente."
                if updated > 0:
                    message = message + " Se han actualizado " + \
                        str(updated) + " datos correctamente."
                if len(errors) > 0:
                    message = message + " Se han encontrado " + \
                        str(len(errors)) + " posibles errores en los datos. Por favor revisar la pestaña de errores."
                response = {
                    "data": [],
                    "message": message,
                    "messageType": "success",
                }
                job.status = "Completed"
                job.end_time = datetime.now()
                job.save()
                return JsonResponse(response)

            except Exception as e:
                job.status = "Failed"
                job.save()
                message = "Ha ocurrido un error desconocido: " + str(e)
                response = {
                    "data": [],
                    "message": message,
                    "messageType": "error",
                }
                return JsonResponse(response)

        else:
            message = "Ha ocurrido un error desconocido: " + str(e)
            response = {
                "data": [],
                "message": message,
                "messageType": "error",
            }
            return JsonResponse(response)

    except Exception as e:
        job = UploadDataJob.objects.filter(buoy_id=buoy_id, status="In Progress").last()
        job.status = "Failed"
        job.save()
        message = "Ha ocurrido un error desconocido: " + str(e)
        response = {
            "data": [],
            "message": message,
            "messageType": "error",
        }
        return JsonResponse(response)


@login_required(login_url='/login')
def exportDataView(request, buoy_id, parameter_id):
    """
    Export data from the database
    """
    response_format = {}
    try:
        # check if date parameters exists in url
        startdate = request.GET.get('startdate')
        starttime = request.GET.get('starttime')
        enddate = request.GET.get('enddate')
        endtime = request.GET.get('endtime')

        # if no date or time is passeed return last 12 hours
        if (isNoneOrEmpty(startdate) and isNoneOrEmpty(enddate)):
            lastParameterEntry = Data.objects.filter(buoy_id=buoy_id, parameter_id=parameter_id).last()
            if lastParameterEntry is not None:
                start = lastParameterEntry.timestamp - TWELVE_HOURS_IN_MILLISECONDS
                end = lastParameterEntry.timestamp
                data = Data.objects.filter(buoy_id=buoy_id, parameter_id=parameter_id, timestamp__gte=start, timestamp__lte=end).all()
        elif (isNoneOrEmpty(startdate)):
            if (isNoneOrEmpty(endtime)):
                endtime = '00:00'
            end = datetime.strptime(f'{enddate} {endtime}', '%Y-%m-%d %H:%M').timestamp() * 1000
            data = Data.objects.filter(buoy_id=buoy_id, parameter_id=parameter_id, timestamp__lte=end).all()
        elif (isNoneOrEmpty(enddate)):
            if (isNoneOrEmpty(starttime)):
                starttime = '00:00'
            start = datetime.strptime(f'{startdate} {starttime}', '%Y-%m-%d %H:%M').timestamp() * 1000
            data = Data.objects.filter(buoy_id=buoy_id, parameter_id=parameter_id, timestamp__gte=start).all()
        else:
            if (isNoneOrEmpty(endtime)):
                endtime = '00:00'
            if (isNoneOrEmpty(starttime)):
                starttime = '00:00'
            start = datetime.strptime(f'{startdate} {starttime}', '%Y-%m-%d %H:%M').timestamp() * 1000
            end = datetime.strptime(f'{enddate} {endtime}', '%Y-%m-%d %H:%M').timestamp() * 1000
            data = Data.objects.filter(buoy_id=buoy_id, parameter_id=parameter_id, timestamp__gte=start, timestamp__lte=end).all()

        parameter = Parameter.objects.get(id=parameter_id)
        filename = f'datos_boya_{buoy_id}_{parameter.name}.csv'

        # export data as csv
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            status=200,
        )
        writer = csv.writer(response)
        writer.writerow(['Fecha y Hora Local', 'Fecha y Hora GMT', 'Valor'])
        for d in data:
            writer.writerow([formatLocalDateTime(d.timestamp), formatUTCDateTime(d.timestamp), d.value])
        return response


    except Exception as e:
        response_format["messageType"] = "error"
        response_format["message"] = str(e)
        return Response(response_format, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def getBuoyParametersView(request, buoy_id):
    response_format = {}
    try:
        buoy = Buoy.objects.filter(id=buoy_id).first()
        # get the parameter data from the database based on the buoy id passed
        serializer = ParameterSerializer(buoy.parameters.filter(active=True), many=True)
        response_format["data"] = serializer.data
        response_format["messageType"] = "success"
        if not serializer.data:
            response_format["message"] = "Empty"
        return Response(response_format)
    except Exception as e:
        response_format["messageType"] = "error"
        response_format["message"] = str(e)
        return Response(response_format, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def dataByBuoyAndParameterView(request, buoy_id, parameter_id):
    response_format = {}
    try:
        # check if date parameters exists in url
        startdate = request.GET.get('startdate')
        starttime = request.GET.get('starttime')
        enddate = request.GET.get('enddate')
        endtime = request.GET.get('endtime')

        # get the first and last date recorder in the database using the timestamp field
        first = Data.objects.filter(buoy_id=buoy_id, parameter_id=parameter_id).order_by('timestamp').first()
        last = Data.objects.filter(buoy_id=buoy_id, parameter_id=parameter_id).order_by('timestamp').last()

        # if no date or time is passeed return last 12 hours
        if ((request.user == None or not request.user.is_authenticated) or (isNoneOrEmpty(startdate) and isNoneOrEmpty(enddate))):
            lastParameterEntry = Data.objects.filter(buoy_id=buoy_id, parameter_id=parameter_id).last()
            if lastParameterEntry is not None:
                start = lastParameterEntry.timestamp - TWELVE_HOURS_IN_MILLISECONDS
                end = lastParameterEntry.timestamp
                data = Data.objects.filter(buoy_id=buoy_id, parameter_id=parameter_id, timestamp__gte=start, timestamp__lte=end).all()
        elif (isNoneOrEmpty(startdate)):
            if (isNoneOrEmpty(endtime)):
                endtime = '00:00'
            end = datetime.strptime(f'{enddate} {endtime}', '%Y-%m-%d %H:%M').timestamp() * 1000
            data = Data.objects.filter(buoy_id=buoy_id, parameter_id=parameter_id, timestamp__lte=end).all()
        elif (isNoneOrEmpty(enddate)):
            if (isNoneOrEmpty(starttime)):
                starttime = '00:00'
            start = datetime.strptime(f'{startdate} {starttime}', '%Y-%m-%d %H:%M').timestamp() * 1000
            data = Data.objects.filter(buoy_id=buoy_id, parameter_id=parameter_id, timestamp__gte=start).all()
        else:
            if (isNoneOrEmpty(endtime)):
                endtime = '00:00'
            if (isNoneOrEmpty(starttime)):
                starttime = '00:00'
            start = datetime.strptime(f'{startdate} {starttime}', '%Y-%m-%d %H:%M').timestamp() * 1000
            end = datetime.strptime(f'{enddate} {endtime}', '%Y-%m-%d %H:%M').timestamp() * 1000
            data = Data.objects.filter(buoy_id=buoy_id, parameter_id=parameter_id, timestamp__gte=start, timestamp__lte=end).all()
        try:
            serializer = DataSerializer(data, many=True)
            if (len(serializer.data) > 0):
                for d in serializer.data:
                    if isnan(d["value"]):
                        d["value"] = None
                values = np.array([d["value"] for d in serializer.data if d["value"] is not None])
                vals, counts = np.unique(values, return_counts=True)
                mode_value = np.argwhere(counts == np.max(counts))
                mode = vals[mode_value].flatten()
                if (mode.any()):
                    mode = mode[0]
                else:
                    mode = None
                data = { 
                    'data': serializer.data, 
                    'mean': np.mean(values), 
                    'median': np.median(values), 
                    'mode': mode,
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'min_date': first.timestamp,
                    'max_date': last.timestamp
                }
            else:
                data = {
                    'data': [],
                    'mean': None,
                    'median': None,
                    'mode': None,
                    'std': None,
                    'min': None,
                    'max': None,
                    'min_date': first.timestamp,
                    'max_date': last.timestamp
                }
            response_format["data"] = data
            response_format["messageType"] = "success"
            if not serializer.data:
                response_format["message"] = "Empty"
            return Response(response_format)
        except Exception as e:
            response_format["messageType"] = "error"
            response_format["message"] = str(e)
            return Response(response_format, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        response_format["messageType"] = "error"
        response_format["message"] = str(e)
        return Response(response_format, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def getUploadJobStatusView(request, buoy_id):
    response_format = {}
    try:
        job = UploadDataJob.objects.filter(
            buoy_id=buoy_id).last()
        response_format["data"] = {
            "current": job.current,
            "total": job.total,
            "status": job.status
        }
        response_format["messageType"] = "success"
        return Response(response_format)
    except Exception as e:
        response_format["messageType"] = "error"
        response_format["message"] = str(e)
        return Response(response_format, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def getDateRangeForParametersView(request):
    response_format = {}
    try:
        first = Data.objects.order_by('timestamp').first()
        last = Data.objects.order_by('timestamp').last()
        response_format["data"] = {
            "first": first.timestamp,
            "last": last.timestamp
        }
        response_format["messageType"] = "success"
        return Response(response_format)
    except Exception as e:
        response_format["messageType"] = "error"
        response_format["message"] = str(e)
        return Response(response_format, status=status.HTTP_400_BAD_REQUEST)

class BuoyViewSet(viewsets.ModelViewSet):
    """
    Retrieves all buoys data from the database
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Buoy.objects.all()
    serializer_class = BuoySerializer

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(BuoyViewSet, self).__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        response_data = super(BuoyViewSet, self).list(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["messageType"] = "success"
        if not response_data.data:
            self.response_format["message"] = "List empty"
        return Response(self.response_format)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return Response({
                "message": "No tiene permiso para realizar esta acción."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        response_data = super(BuoyViewSet, self).create(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["messageType"] = "success"
        return Response(self.response_format)

    def retrieve(self, request, *args, **kwargs):
        response_data = super(BuoyViewSet, self).retrieve(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["messageType"] = "success"
        if not response_data.data:
            self.response_format["message"] = "Empty"
        return Response(self.response_format)

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return Response({
                "message": "No tiene permiso para realizar esta acción."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        response_data = super(BuoyViewSet, self).update(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["messageType"] = "success"
        return Response(self.response_format)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return Response({
                "message": "No tiene permiso para realizar esta acción."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        response_data = super(BuoyViewSet, self).destroy(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["messageType"] = "success"
        return Response(self.response_format)


class ParameterViewSet(viewsets.ModelViewSet):
    """ 
    Retrieves all parameter data from the database
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(ParameterViewSet, self).__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        response_data = super(ParameterViewSet, self).list(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["messageType"] = 'success'
        if not response_data.data:
            self.response_format["message"] = "List empty"
        return Response(self.response_format)

    def retrieve(self, request, *args, **kwargs):
        response_data = super(ParameterViewSet, self).retrieve(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["messageType"] = 'success'
        if not response_data.data:
            self.response_format["message"] = "Empty"
        return Response(self.response_format)

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return Response({
                "message": "No tiene permiso para realizar esta acción."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        response_data = super(ParameterViewSet, self).update(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["messageType"] = 'success'
        return Response(self.response_format)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({
                "message": "No tiene permiso para realizar esta acción."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        response_data = super(ParameterViewSet, self).destroy(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["messageType"] = 'success'
        return Response(self.response_format)


class DataViewSet(viewsets.ModelViewSet):
    """ 
    Retrieves all data from the database
    """
    queryset = Data.objects.all()
    serializer_class = DataSerializer

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(DataViewSet, self).__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        response_data = super(DataViewSet, self).list(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["messageType"] = 'success'
        if not response_data.data:
            self.response_format["message"] = "Lista vacía."
        return Response(self.response_format)
