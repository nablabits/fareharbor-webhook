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


def test_create_customer_prototype(database):
    service = model_services.CreateCustomerPrototype(
        total=10,
        total_including_tax=10,
        display_name="foo",
        note="bar"
    )
    new_customer_prototype = service.run()
    assert models.CustomerPrototype.query.get(new_customer_prototype.id)


def test_update_customer_prototype(database):
    old_cp = model_services.CreateCustomerPrototype(
        total=10,
        total_including_tax=10,
        display_name="foo",
        note="bar"
    ).run()

    model_services.UpdateCustomerPrototype(
        customer_prototype_id=old_cp.id,
        total=20,
        total_including_tax=20,
        display_name="bar",
        note="baz"
    ).run()

    cp = models.CustomerPrototype.query.get(old_cp.id)
    assert cp.total == 20
    assert cp.total_including_tax == 20
    assert cp.display_name == "bar"
    assert cp.note == "baz"


def test_delete_customer_prototype(database):
    cp = model_services.CreateCustomerPrototype(
        total=10,
        total_including_tax=10,
        display_name="foo",
        note="bar"
    ).run()
    model_services.DeleteCustomerPrototype(cp.id).run()
    cp = models.CustomerPrototype.query.get(cp.id)
    assert cp is None

