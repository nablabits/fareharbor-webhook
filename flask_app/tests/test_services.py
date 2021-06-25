import json
from datetime import date
import pytest

from fh_webhook import services, models


def test_populate_db_creates_item(database, app):
    # TODO: use this function to test populate db just the ids of the obj
    # created
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()
    items = models.Item.query.all()
    assert len(items) == 1
    assert items[0].id == 159068
    assert items[0].name == "Alquiler Urbana"


def test_populate_db_creates_availability(database, app, item_factory):
    """
    Although the first test actually saves all the data contained in
    sample_data, we split the tests into manageable chunks for readability.
    """
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()
    availabilities = models.Availability.query.all()
    assert len(availabilities) == 1
    av = availabilities[0]
    assert av.id == 619118440
    assert av.capacity == 49
    assert av.minimum_party_size == 1
    assert av.maximum_party_size is None
    assert av.start_at.isoformat() == "2021-04-05T12:30:00+02:00"
    assert av.end_at.isoformat() == "2021-04-05T13:00:00+02:00"


def test_delete_item(database, item_factory):
    item = item_factory()
    model_services.DeleteItem(item.id).run()
    with pytest.raises(DoesNotExist):
        models.Item.get(item.id)


def test_create_availabilty(database, item_factory):
    item = item_factory()
    availability = model_services.CreateAvailability(
        capacity=10,
        minimum_party_size=11,
        maximum_party_size=12,
        start_at=datetime.now(),
        end_at=datetime.now(),
        item_id=item.id,
    ).run()
    assert models.Availability.get(availability.id)



