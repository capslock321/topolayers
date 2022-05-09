class GenerationException(Exception):
    def __init__(self, layer: object, reason: str):
        self.layer = layer
        self.reason: str = reason


class InvalidThreshold(Exception):
    pass


class InvalidRGB(Exception):
    pass


class LayerRequired(Exception):
    pass
