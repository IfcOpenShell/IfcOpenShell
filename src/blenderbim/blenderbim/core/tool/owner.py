import abc


class Owner(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def set_user(cls, user):
        pass

    @classmethod
    @abc.abstractmethod
    def get_user(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def clear_user(cls):
        pass
