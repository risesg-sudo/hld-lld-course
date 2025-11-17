from abc import ABC, abstractmethod

class MessageSender(ABC):
    @abstractmethod
    def send(self, msg): pass

class EmailSender(MessageSender):
    def send(self, msg):
        print(f"Email: {msg}")

class SmsSender(MessageSender):
    def send(self, msg):
        print(f"SMS: {msg}")

class NotificationService:
    def __init__(self, sender: MessageSender):
        self.sender = sender
        
    def notify(self, msg):
        self.sender.send(msg)

if __name__ == "__main__":
    email_service = NotificationService(EmailSender())
    email_service.notify("Hello via email")
    
    sms_service = NotificationService(SmsSender())
    sms_service.notify("Hello via SMS")
