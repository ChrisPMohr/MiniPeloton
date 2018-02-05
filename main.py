class DoesNotExist(BaseException):
    pass


class Field(object):
    def __init__(self, field_type):
        if not isinstance(field_type, (type, str)):
            raise TypeError("Invalid field type", field_type)
        self.field_type = field_type
        self.is_relation = isinstance(field_type, (ModelMeta, str))

    @property
    def model_class(self):
        if not self.is_relation:
            raise Exception()
        if isinstance(self.field_type, ModelMeta):
            return self.field_type
        elif isinstance(self.field_type, str):
            return ModelMeta.all_models[self.field_type]
        else:
            raise TypeError("Invalid foreign key model", self.field_type)

    def __set__(self, instance, value):
        if self.is_relation:
            field_type = self.model_class
        else:
            field_type = self.field_type
        if not isinstance(value, field_type):
            raise TypeError("%s is not of type %s" % (str(value), str(field_type)))
        if self.is_relation:
            instance._vals_[self] = value.id
        else:
            instance._vals_[self] = value

    def __get__(self, instance, owner):
        if self.is_relation:
            foreign_key_id = instance._vals_[self]
            return self.model_class[foreign_key_id]
        else:
            return instance._vals_[self]


class Set(object):
    def __init__(self, field_type, backref=None):
        if not isinstance(field_type, (ModelMeta, str)):
            raise TypeError("Invalid type for set", field_type)
        self.field_type = field_type
        self.backref = backref

    def __get__(self, instance, owner):
        backref = self.backref or type(instance).__name__.lower()
        if isinstance(self.field_type, ModelMeta):
            related_type = self.field_type
        elif isinstance(self.field_type, str):
            related_type = ModelMeta.all_models[self.field_type]
        return [el for el in related_type if getattr(el, backref).id == instance.id]


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
        self._vals_ = {}
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


class Instructor(Model):
    name = Field(str)


class Ride(Model):
    name = Field(str)
    instructor = Field(Instructor)
    workout_set = Set('Workout')


class Workout(Model):
    ride = Field(Ride)
    user = Field('User')
    start_time = Field(datetime)


class User(Model):
    username = Field(str)
    workout_set = Set(Workout)


if __name__ == '__main__':
    cody = Instructor(name="Cody")
    jess = Instructor(name="Jess")
    r1 = Ride(name="Cody's Rock Ride", instructor=cody)
    r2 = Ride(name="Cody's Disco Ride", instructor=cody)
    r3 = Ride(name="Jess's Pop Ride", instructor=jess)

    me = User(username='me')
    w1 = Workout(ride=r1, user=me, start_time=datetime(2017, 1, 1, 7))
    w2 = Workout(ride=r2, user=me, start_time=datetime(2017, 1, 1, 8))
    w3 = Workout(ride=r3, user=me, start_time=datetime(2017, 1, 1, 9))

    print('User workouts', len(me.workout_set))
    print('Ride 1 workouts', len(r1.workout_set))

    from collections import Counter
    counts = Counter(workout.ride.instructor.name for workout in me.workout_set)
    print("Workout count by instructor", counts)

    latest_workout_by_instructor = {}
    for workout in me.workout_set:
        instructor = workout.ride.instructor
        if instructor not in latest_workout_by_instructor:
            latest_workout_by_instructor[instructor] = workout
        elif latest_workout_by_instructor[instructor].start_time < workout.start_time:
            latest_workout_by_instructor[instructor] = workout
    latest_ride_by_instructor = {instructor.name: workout.ride.name for (instructor, workout)
                                 in latest_workout_by_instructor.items()}
    print("Latest ride by instructor", latest_ride_by_instructor)
