# menu/page.py

class Page:
    def __init__(self, data):
        self.data = data

    def render(self):
        raise NotImplementedError("Subclasses should implement this!")
