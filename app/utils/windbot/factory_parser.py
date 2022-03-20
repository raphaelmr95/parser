import abc

# Factory XML and JSON parser
class FactoryParser(metaclass=abc.ABCMeta):
    """
    Abstract Factory Parser class
    """
    @abc.abstractmethod
    def parse(self, file_path):
        """
        Parse a file
        """
        pass