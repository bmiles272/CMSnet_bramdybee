'''
Python code found online to convert suds object which are produced by the landybee SOAP functions into python dictionaries for easy comparison.
code source: https://gist.github.com/checkaayush/915d2600d696e818349bb1c955ebdcf8 
'''

class SUDS2Dict:

    def __init__(self) -> None:
        pass

    def basic_sobject_to_dict(self, obj):
        """Converts suds object to dict very quickly.
        Does not serialize date time or normalize key case.
        :param obj: suds object
        :return: dict object
        """
        if not hasattr(obj, '__keylist__'):
            return obj
        data = {}
        fields = obj.__keylist__
        for field in fields:
            val = getattr(obj, field)
            if isinstance(val, list):
                data[field] = []
                for item in val:
                    data[field].append(self.basic_sobject_to_dict(item))
            else:
                data[field] = self.basic_sobject_to_dict(val)
        return data


    def sobject_to_dict(self, obj, key_to_lower=False, json_serialize=False):
        """
        Converts a suds object to a dict.
        :param json_serialize: If set, changes date and time types to iso string.
        :param key_to_lower: If set, changes index key name to lower case.
        :param obj: suds object
        :return: dict object
        """
        import datetime

        if not hasattr(obj, '__keylist__'):
            if json_serialize and isinstance(obj, (datetime.datetime, datetime.time, datetime.date)):
                return obj.isoformat()
            else:
                return obj
        data = {}
        fields = obj.__keylist__
        for field in fields:
            val = getattr(obj, field)
            if key_to_lower:
                field = field.lower()
            if isinstance(val, list):
                data[field] = []
                for item in val:
                    data[field].append(self.sobject_to_dict(item, json_serialize=json_serialize))
            else:
                data[field] = self.sobject_to_dict(val, json_serialize=json_serialize)
        return data


    def sobject_to_json(self, obj, key_to_lower=False):
        """
        Converts a suds object to json.
        :param obj: suds object
        :param key_to_lower: If set, changes index key name to lower case.
        :return: json object
        """
        import json
        data = self.sobject_to_dict(obj, key_to_lower=key_to_lower, json_serialize=True)
        return json.dumps(data)