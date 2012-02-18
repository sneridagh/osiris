from osiris.errorhandling import OAuth2ErrorHandler


class MADDict(dict):
    """
        A simple vitaminated dict for holding a MongoBD arbitrary object
    """
    schema = {}

    def __getitem__(self, key):
        val = dict.__getitem__(self, key)
        return val

    def __setitem__(self, key, val):
        """
            Allow only fields defined in schema to be inserted in the dict
            ignore non schema values
        """
        if key in self.schema.keys():
            dict.__setitem__(self, key, val)
        else:
            pass

    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dictrepr)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).iteritems():
            self[k] = v

    def __setattr__(self, key, value):
        """
            Enables setting values of dict's items trough attribute assignment,
            while preserving default setting of class attributes
        """
        if hasattr(self, key):
            dict.__setattr__(self, key, value)
        else:
            self.__setitem__(key, value)

    def __getattr__(self, key):
        """
            Maps dict items access to attributes, while preserving access to class attributes
        """
        try:
            return self.__getattribute__(key)
        except AttributeError:
            return self.__getitem__(key)

    def checkParameterExists(self, fieldname):
        """
            Checks if a parameter 'fieldname' exists in the data dict, accepts fieldnames
            in the form object.subobject, in one level depth
        """

        parts = fieldname.split('.')

        base = self.data
        for part in parts:
            if part in base.keys():
                base = base[part]
            else:
                return False
        return True

    def validate(self):
        """
            Checks if all the required schema fields (request=1) are present in
            the collected data
        """
        for fieldname in self.schema:
            if self.schema.get(fieldname).get('request', 0):
                if not self.checkParameterExists(fieldname):
                    return OAuth2ErrorHandler.error_invalid_request('Required paramer "%s" not found in the request' % fieldname)
        return True


class MDBObject(MADDict):
    """
        Base Class for objects determining arbitrary mongoDB objects,
        provides the base for validating the object by subclassing it
        and specifing an schema with required values
    """
    data = {}
    schema = {}

    def __init__(self, data):
        """
        """
        self.data = data
        self.validate()
        self.update(data)
