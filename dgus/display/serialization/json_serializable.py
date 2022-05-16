import abc


class JsonSerializable:
    @abc.abstractmethod
    def from_json(self, json_data : dict):
        pass

    @abc.abstractmethod
    def to_json(self):
        pass
    