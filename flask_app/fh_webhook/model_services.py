from datetime import datetime

import attr

from . import models
from .models import db


@attr.s
class CreateItem:
    name = attr.ib()

    def run(self):
        new_item = models.Item(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            name=self.name
        )
        db.session.add(new_item)
        db.session.commit()
        return new_item

@attr.s
class UpdateItem:
    item_id = attr.ib(type=int)
    name = attr.ib()

    def run(self):
        item = models.Item.query.get(self.item_id)
        item.name = self.name
        item.updated_at = datetime.utcnow()
        db.session.commit()
        return item

@attr.s
class DeleteItem:
    item_id = attr.ib(type=int)

    def run(self):
        item = models.Item.query.get(self.item_id)
        db.session.delete(item)
        db.session.commit()


