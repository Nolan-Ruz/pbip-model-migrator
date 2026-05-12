class BaseOperation:
    def apply(self, project, mapping):
        raise NotImplementedError("Operation must implement apply method")