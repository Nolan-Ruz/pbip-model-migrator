class MigrationEngine:
    def __init__(self, operations):
        self.operations = operations

    def run(self, project, mapping):
        for operation in self.operations:
            operation.apply(project, mapping)