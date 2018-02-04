class Field(object):
    def __init__(self, field_type):
        self.field_type = field_type


# class ForeignKeyField(object):
#      pass


class ModelMeta(type):
    all_models = []

    def __iter__(self):
        return self.get_all_instances()

    def __new__(cls, name, bases, attrs):
        class_created = super(ModelMeta, cls).__new__(cls, name, bases, attrs)
        cls.all_models.append((name, class_created))

        fields = []

        for key, val in attrs.items():
            if isinstance(val, Field):
                fields.append(key)
        class_created._fields = fields

        return class_created


class Model(object, metaclass=ModelMeta):
    global__data = {}

    incrementing_pk = 0

    #    def __new__(cls, name, bases):
    #        for key, value in cls.__dict__.items():
    #            if isinstance(value, Field):

    def __init__(self, **kwargs):
        self.id = Model.incrementing_pk
        Model.incrementing_pk += 1
        self.__data()[self.id] = self

        for k, v in kwargs.items():
            setattr(self, k, v)

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
    name = Field(str)


class Workout(Model):
    ride_id = Field(str)
    workout_count = Field(int)


if __name__ == '__main__':
    Ride()
    Ride()
    Workout()

    for ride in Ride:
        print(ride)
    for workout in Workout:
        print(workout)

    print(Ride._fields)
    print(Workout._fields)
