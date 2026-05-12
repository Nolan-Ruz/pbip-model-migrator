from .base import BaseOperation

class TableMapper(BaseOperation):
    def apply(self, project, mapping):
        print("Mapping tables...")
        # later: implement logic