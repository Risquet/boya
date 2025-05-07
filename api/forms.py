from django import forms
from api.models import Buoy


# form for buoy
class BuoyForm(forms.ModelForm):
    class Meta:
        model = Buoy
        fields = ['name', 'lat', 'lon', 'gsm', 'model', 'manufacturer', 'depth', 'img', 'plans', 'active']
        labels = {
            'name': 'Nombre (Obligatorio)',
            'lat': 'Latitud (Obligatorio)',
            'lon': 'Longitud (Obligatorio)',
            'gsm': "Formato GSM: 00(°) 00(\') 00.0(\") N/S | 00(°) 00(\') 00.0(\") E/W",
            'model': 'Modelo',
            'manufacturer': 'Fabricante',
            'depth': 'Profundidad',
            'img': 'Imagen',
            'plans': 'Planos de Instalación',
            'active': 'Activa'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'lat': forms.TextInput(attrs={'class': 'form-control'}),
            'lon': forms.TextInput(attrs={'class': 'form-control'}),
            'gsm': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'depth': forms.NumberInput(attrs={'class': 'form-control'}),
            'img': forms.FileInput(attrs={'class': 'form-control'}),
            'plans': forms.FileInput(attrs={'class': 'form-control'})
        }

    # get only the decimal part of the coordinates
    def get_decimal_part(self, minutes):
        minutes_string = str(minutes)
        return minutes_string.split('.')[1]

    # convert from gsm to decimal
    def convert_to_decimal(self, gsm):
        values = gsm.split(' ')
        s = float(values[2].replace('\"', ''))
        md = float(s / 60) 
        m = values[1]
        if (m.__contains__("'")):
            m = m.replace("'", '')
        elif (m.__contains__("’")):
            m = m.replace('’', '')
        m = float(m) + md
        dd = self.get_decimal_part(float(m / 60))
        d = values[0].replace('°', '') + '.' + dd
        h = values[3]
        if h == 'S' or h == 'W':
            d = '-' + d
        return d

    def check_gsm_format(self, gsm):
        values = gsm.split(' ')
        if len(values) < 4:
            return False
        try:
            d = float(values[0])
            m = float(values[1])
            s = float(values[2])
        except Exception as e:
            return False
        p = values[3]
        if (p == 'N' or p == 'S' or p == 'E' or p == 'W' or p == 'O'):
            return True
        return False

    # if gsm is checked convert from gsm to decimal coordinates and always save both values as float
    def clean(self):
        cleaned_data = super().clean()
        gsm = cleaned_data.get('gsm')
        lat = cleaned_data.get('lat')
        lon = cleaned_data.get('lon')
        if lat != None and lon != None:
            if gsm:
                if self.check_gsm_format(lat) and self.check_gsm_format(lon):
                    lat = self.convert_to_decimal(lat)
                    lon = self.convert_to_decimal(lon)
                else:
                    raise forms.ValidationError("El formato de coordenadas es incorrecto, debe ser: 00(°) 00(\') 00.0(\") N/S | 00(°) 00(\') 00.0(\") E/W")
            else:
                try:
                    lat = float(lat)
                    lon = float(lon)
                except Exception as e:
                    raise forms.ValidationError("Las coordenadas deben ser decimales o debe marcar el formato GSM.")
            cleaned_data['lat'] = float(lat)
            cleaned_data['lon'] = float(lon)
        cleaned_data['gsm'] = False
        return cleaned_data
