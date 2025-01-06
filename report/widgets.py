from django import forms
import json

class PointFieldWidget(forms.TextInput):
    def format_value(self, value):
        if value is None:
            return ''
        if isinstance(value, str):
            try:
                geojson = json.loads(value)
                if geojson.get('type') == 'Point':
                    coordinates = geojson.get('coordinates', [])
                    return f'{coordinates[1]}, {coordinates[0]}'
            except json.JSONDecodeError:
                return value
        elif isinstance(value, dict) and value.get('type') == 'Point':
            coordinates = value.get('coordinates', [])
            return f'{coordinates[1]}, {coordinates[0]}'
        return value

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if value:
            try:
                x, y = map(float, value.split(','))
                return json.dumps({"type": "Point", "coordinates": [y, x]})
            except ValueError:
                pass
        return None