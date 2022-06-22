class OnScreenKeyBoard:
    
    @staticmethod
    def decode_numeric_oskbd_value(data : bytes):
        # The data entered with the onscreen keyboard arives ascii coded.
        # And 0xff is appended to terminate the string.
        # But 0xff is not ascii decodable to we just use the data before
        # the first appearance of 0xff
        new_data = bytearray()
        for byte in data:
            if byte != 0xff:
                new_data.append(byte)
            else:
                break

        temperature_str = str(new_data, encoding='ascii')
        temperature_str = temperature_str.replace(",",".")

        return temperature_str