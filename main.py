class ModelMeta(type):
    all_models = []

    def __iter__(self):
        return self.get_all_instances()

    def __new__(cls, name, bases, attrs):
        class_created = super(ModelMeta, cls).__new__(cls, name, bases, attrs)
        cls.all_models.append((name, class_created))
        print(cls.all_models)
        return class_created


# class Field(object):
#    def __init__(self, field_type):
#        self.field_type = field_type


# class ForeignKeyField(object):
#    pass


class Model(object, metaclass=ModelMeta):
    global__data = {}

    #    def __new__(cls, name, bases):
    #        for key, value in cls.__dict__.items():
    #            if isinstance(value, Field):

    def __init__(self, id):
        self.id = id
        self.__data()[id] = self

    def __str__(self):
        return "<%s %s>" % (type(self), self.id)

    def __repr__(self):
        return "<%s %s>" % (type(self), self.id)

    @classmethod
    def __data(cls):
        return cls.global__data.setdefault(cls, {})

    @classmethod
    def get_all_instances(cls):
        return iter(cls.__data().values())


class Ride(Model):
    pass


class Workout(Model):
    pass


if __name__ == '__main__':
    Ride(3)
    Ride(4)
    Workout(3)

    print(list(Ride))
    print(list(Workout))
