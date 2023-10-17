import re
import ipaddress

class DataValidation():

    def validate_ip_address(self, value):
        try:
            ip = ipaddress.IPv4Address(value)
            return str(ip)
        except ipaddress.AddressValueError:
            raise ValueError("Neplatná IPv4 adresa")

    def validate_frequency_format(self, value):
        pattern = r"^\d+[hmsD](?![hmsD])$"

        if not re.match(pattern, value):
            raise ValueError("Neplatný formát frekvence")
        return value