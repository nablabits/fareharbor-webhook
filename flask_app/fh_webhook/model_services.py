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


# Customers' services

@attr.s
class CreateCustomerPrototype:
    total = attr.ib(type=int)
    total_including_tax = attr.ib(type=int)
    display_name = attr.ib(type=str)
    note = attr.ib(type=str)

    def run(self):
        new_customer_prototype = models.CustomerPrototype(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            total=self.total,
            total_including_tax=self.total_including_tax,
            display_name=self.display_name,
            note=self.note
        )
        db.session.add(new_customer_prototype)
        db.session.commit()
        return new_customer_prototype


@attr.s
class UpdateCustomerPrototype:
    customer_prototype_id = attr.ib(type=int)
    total = attr.ib(type=int)
    total_including_tax = attr.ib(type=int)
    display_name = attr.ib(type=str)
    note = attr.ib(type=str)

    def run(self):
        customer_prototype = models.CustomerPrototype.query.get(
            self.customer_prototype_id)
        customer_prototype.updated_at = datetime.utcnow()
        customer_prototype.total = self.total
        customer_prototype.total_including_tax = self.total_including_tax
        customer_prototype.display_name = self.display_name
        customer_prototype.note=self.note

        db.session.commit()
        return customer_prototype


@attr.s
class DeleteCustomerPrototype:
    customer_prototype_id = attr.ib(type=int)

    def run(self):
        customer_prototype = models.CustomerPrototype.query.get(
            self.customer_prototype_id
        )
        db.session.delete(customer_prototype)
        db.session.commit()

