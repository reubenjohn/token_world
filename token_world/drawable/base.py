from abc import ABC, abstractmethod
from typing import Callable, Dict
from pyglet.graphics import Batch  # type: ignore[import]


from token_world.entity import Entity, EntityDict

DrawableEntityHandlerId = str
DrawCallable = Callable[[], None]


class DrawableEntityHandler(ABC):
    def __init__(self, id: DrawableEntityHandlerId):
        self.id = id
        self._entities: EntityDict = {}
        self._batch = Batch()

    @abstractmethod
    def is_applicable(self, entity: Entity) -> bool:
        pass  # pragma: no cover

    @abstractmethod
    def new_draw_callback(self, entity: Entity) -> DrawCallable:
        pass  # pragma: no cover

    def draw(self):
        self._batch.draw()


DrawableEntityHandlerDict = Dict[DrawableEntityHandlerId, DrawableEntityHandler]
