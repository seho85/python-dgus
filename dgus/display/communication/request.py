from dataclasses import dataclass

@dataclass
class Request:
    get_request_data = []
    response_callback = []
    name = "undef"

    def __init__(self, request_data_func, response_callback, name) -> None:
        self.get_request_data = request_data_func
        self.response_callback = response_callback
        self.name = name
        