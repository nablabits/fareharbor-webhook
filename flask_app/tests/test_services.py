from fh_webhook import models, model_services, create_app


def test_create_item(database):
    service = model_services.CreateItem(name="foo")
    new_item = service.run()
    assert models.Item.query.get(new_item.id)


def test_update_item(database):
    old_item = model_services.CreateItem(name="foo").run()
    s = model_services.UpdateItem(item_id=old_item.id, name="bar")
    new_item = s.run()
    item = models.Item.query.get(old_item.id)
    assert item.name == "bar"


def test_delete_item(database):
    item = model_services.CreateItem(name="foo").run()
    model_services.DeleteItem(item.id).run()
    item = models.Item.query.get(item.id)
    assert item is None



