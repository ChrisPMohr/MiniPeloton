class DoesNotExist(BaseException):
    pass


class Field(object):
    def __init__(self, field_type):
        self.field_type = field_type

    def __set__(self, instance, value):
        foreign_key_id = value.id
        setattr(instance, self.field_name, foreign_key_id)
        return self.model_class[foreign_key_id]


class ForeignKeyField(Field):
    def __init__(self, model):
        if not isinstance(model, (ModelMeta, str)):
            raise TypeError("Invalid foreign key", model)
        self._model = model

    @property
    def model_class(self):
        if isinstance(self._model, ModelMeta):
            return self._model
        elif isinstance(self._model, str):
            return ModelMeta.all_models[self._model]
        else:
            raise TypeError("Invalid foreign key model", self._model)

    @property
    def field_name(self):
        if isinstance(self._model, ModelMeta):
            return "_" + self._model.__name__
        elif isinstance(self._model, str):
            return "_" + self._model
        else:
            raise TypeError("Invalid foreign key model", self._model)

    def __get__(self, instance, owner):
        foreign_key_id = getattr(instance, self.field_name)
        return self.model_class[foreign_key_id]

    def __set__(self, instance, value):
        foreign_key_id = value.id
        setattr(instance, self.field_name, foreign_key_id)
        return self.model_class[foreign_key_id]


class ModelMeta(type):
    all_models = {}

    def __new__(cls, name, bases, attrs):
        class_created = super(ModelMeta, cls).__new__(cls, name, bases, attrs)
        cls.all_models[name] = class_created

        fields = []

        for key, val in attrs.items():
            if isinstance(val, Field):
                fields.append(key)
        class_created._fields = fields

        return class_created

    def __iter__(self):
        return self.get_all_instances()

    def __getitem__(self, key):
        return self.get_item(key)


class Model(object, metaclass=ModelMeta):
    global__data = {}
    incrementing_pk = 0

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
    def get_item(cls, key):
        result = cls.__data().get(key)
        if result is None:
            raise DoesNotExist
        return result

    @classmethod
    def get_all_instances(cls):
        return iter(cls.__data().values())

# ------ORM ends here-------


from datetime import datetime

class Ride(Model):
    name = Field(str)
    start_time = Field(datetime)


class Workout(Model):
    ride = ForeignKeyField(Ride)


if __name__ == '__main__':
    r1 = Ride(name="Cody's Rock Ride")
    r2 = Ride(name="Jess's Pop Ride")
    w1 = Workout(ride=r1)

    print('Ride 1', r1.id, r1.name)
    print('Workout', w1.id, w1.ride.name)
    w1.ride.name = "New Name"
    print('Updated name', r1.name)

    print('All Rides')
    for ride in Ride:
        print(ride)
    print('All Workouts')
    for workout in Workout:
        print(workout)

    print(Ride._fields)
    print(Workout._fields)
