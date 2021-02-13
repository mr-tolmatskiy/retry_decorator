from functools import wraps
import json
import yaml
import uuid
import xml.etree.ElementTree as ET
import xml.dom.minidom
from io import StringIO
import random
import time


class NothingToRetrieveException(Exception):
    pass


class ProductNotFoundException(Exception):
    pass


class retry:
    def __init__(self, n=3, interval=1, allowed_exceptions=(Exception,), verbose=True):
        self.n = n
        self.interval = interval
        self.allowed_exceptions = allowed_exceptions
        self.verbose = verbose

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            try_num = 1
            for number in range(self.n):
                try:
                    value = func(*args, **kwargs)
                except self.allowed_exceptions:
                    if self.verbose is True:
                        print(f"Retrying <{func.__name__}>. Try #{try_num}")
                else:
                    return value
                try_num += 1
                time.sleep(self.interval)
                if try_num == self.n + 1:
                    raise ProductNotFoundException

        return inner


def retrieve_product():
    product = Product(name="milk", identifier=str(uuid.uuid4()))
    list_of_choice = ["except", "noexcept"]
    choice_of_except = list_of_choice[random.randint(0, len(list_of_choice) - 1)]
    list_of_serialization = ["to_json", "to_yaml", "to_xml"]
    choice_of_serialization = list_of_serialization[random.randint(0, len(list_of_serialization) - 1)]
    result = ""
    if choice_of_except == "except":
        raise NothingToRetrieveException()
    else:
        if choice_of_serialization == "to_json":
            product.to_json()
            result = product.to_json()
        elif choice_of_serialization == "to_yaml":
            product.to_yaml()
            result = product.to_yaml()
        elif choice_of_serialization == "to_xml":
            product.to_xml()
            product_xml = product.to_xml()
            department = ET.Element("department")
            department.append(product_xml)
            xml_str = ET.tostring(department)
            dom = xml.dom.minidom.parseString(xml_str)
            result = dom.toprettyxml()
    print(result)
    return choice_of_serialization, result, product


@retry(n=3, interval=1, allowed_exceptions=(ProductNotFoundException,), verbose=True)
def get_product():
    try:
        result = retrieve_product()
    except NothingToRetrieveException:
        raise ProductNotFoundException()


class Product:

    def __init__(self, name, identifier):
        self.name = name
        self.identifier = identifier

    def to_json(self):
        return json.dumps(self.__dict__)

    def to_yaml(self):
        s = StringIO()
        yaml.dump(self.__dict__, s)
        s.seek(0)
        return s.read()

    def to_xml(self):
        product = ET.Element("product")
        name = ET.SubElement(product, "name")
        name.text = self.name
        identifier = ET.SubElement(product, "identifier")
        identifier.text = self.identifier
        return product


if __name__ == '__main__':
    get_product()
