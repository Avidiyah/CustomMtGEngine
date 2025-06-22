class GameEvent:
    def __init__(self, event_type: str, metadata: dict):
        self.event_type = event_type
        self.metadata = metadata


class StackResolutionEvent(GameEvent):
    def __init__(self, obj, result):
        super().__init__("StackResolution", {"card": str(obj), "result": result})


class StackFizzleEvent(GameEvent):
    def __init__(self, obj):
        super().__init__("StackFizzle", {"card": str(obj)})


class StackDeclinedEvent(GameEvent):
    def __init__(self, obj):
        super().__init__("StackDeclined", {"card": str(obj)})
