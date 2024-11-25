from pyglet.shapes import Triangle  # type: ignore[import]
from pyglet.graphics import Batch  # type: ignore[import]

from token_world.drawable.base import DrawableEntityHandler, DrawCallable
from token_world.entity import Entity  # type: ignore[import]


class PhysicalEntityHandler(DrawableEntityHandler):

    class Callback:
        def __init__(self, entity: Entity, batch: Batch):
            self.entity = entity
            props = entity.properties
            x, y = props["x"], props["y"]
            self.shape = Triangle(x, y, x + 10, y, x + 5, y + 10, color=(255, 0, 0), batch=batch)

        def __call__(self):
            self.shape.x = self.entity.properties["x"]
            self.shape.y = self.entity.properties["y"]

    def __init__(self):
        super().__init__("physical")

    def is_applicable(self, entity: Entity) -> bool:
        return entity.properties.get("is_physical", False)

    def new_draw_callback(self, entity: Entity) -> DrawCallable:
        return self.Callback(entity, self._batch)
