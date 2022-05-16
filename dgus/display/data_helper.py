def value_to_fixed_point(data, decimal_places):
    temp_float = float(data) * pow(10, decimal_places)
    return int(temp_float)
