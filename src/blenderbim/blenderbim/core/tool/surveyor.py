import abc


class Surveyor(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def get_absolute_matrix(cls, obj):
        pass
