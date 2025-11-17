from abc import ABC, abstractmethod

class Printer(ABC):
    @abstractmethod
    def print(self, doc): pass

class Scanner(ABC):
    @abstractmethod
    def scan(self, doc): pass

class SimplePrinter(Printer):
    def print(self, doc):
        print(f"Printing: {doc}")

class MultiFunctionDevice(Printer, Scanner):
    def print(self, doc):
        print(f"Printing: {doc}")
    def scan(self, doc):
        print(f"Scanning: {doc}")

if __name__ == "__main__":
    printer = SimplePrinter()
    printer.print("Document")
    
    mfd = MultiFunctionDevice()
    mfd.print("Doc1")
    mfd.scan("Doc2")
