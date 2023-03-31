from datetime import date, datetime, timedelta, timezone
from random import randint
from uuid import uuid4

import pytest
from conftest import randomizer

from fh_webhook.bike_tracker_services import DailyActivities
from fh_webhook.model_services import CreateBikeUsages
from fh_webhook.models import Booking


@pytest.mark.parametrize(
    "item_id",
    [
        159053,
        159055,
        159056,
        159057,
        159058,
        159060,
    ],
)
def test_daily_activities_success_for_tours(
    item_id,
    client,
    database,
    booking_factory,
    item_factory,
    availability_factory,
    bike_factory,
):

    ts0 = datetime.now()
    ts1 = ts0 + timedelta(hours=1)
    ts2 = ts1 + timedelta(hours=1)

    # Create a valid tour item
    s = item_factory
    s.item_id = item_id
    s.name = "item 1"
    item = s.run()

    # Create the booking that will appear in the results
    b0, b0_id = randomizer(booking_factory.run())
    b0.customer_count = 10
    b0.availability.start_at = ts0
    b0.availability.end_at = ts1
    b0.availability.headline = "service 1"
    b0.availability.item = item
    b0.rebooked_to = None
    database.session.commit()

    # Create another booking to test the group by
    s = availability_factory
    s.availability_id = randint(1, 10000)
    s.start_at = ts1
    s.end_at = ts2
    s.headline = "service 2"
    av = s.run()

    av.item = item
    av.item.name = "item 2"
    b1, b1_id = randomizer(booking_factory.run())
    b1.customer_count = 20
    b1.availability = av
    b1.rebooked_to = None
    database.session.commit()

    # create another booking that should not appear in the results due to the assignment
    s = availability_factory
    s.availability_id = randint(1, 10000)
    s.start_at = ts1
    s.end_at = ts2
    s.headline = "service 3"
    av3 = s.run()

    av3.item = item
    av3.item.name = "item 3"
    b2, b2_id = randomizer(booking_factory.run())
    b2.customer_count = 20
    b2.availability = av3
    b2.rebooked_to = None

    bikes = [
        bike_factory(uuid=uuid4().hex, readable_name=f"red bike{n}") for n in range(3)
    ]
    bike_uuids = [b.uuid for b in bikes]

    database.session.commit()

    CreateBikeUsages(
        timestamp=datetime.now(timezone.utc),
        instance_id=av3.id,
        bike_uuids=bike_uuids[:2],
    ).run()

    d = DailyActivities(for_date=date.today()).run()

    assert len(d) == 2

    for n, booking_id in enumerate((b0_id, b1_id)):
        b = Booking.get(booking_id)
        tss = [ts0, ts1]
        expected0 = {
            "availability_id": b.availability_id,
            "headline": b.availability.headline,
            "timestamp": str(tss[n].time()).split(".")[0],
            "no_of_bikes": b.customer_count + 1,
            "duration": "1.0",
        }

        assert d[n] == expected0


@pytest.mark.parametrize(
    "item_id",
    [
        159068,
        159074,
        159100,
        159103,
        235262,
    ],
)
def test_daily_activities_success_for_rental_items(
    item_id,
    client,
    database,
    item_factory,
    customer_factory,
    customer_type_rate_factory,
    customer_type_factory,
    editable_contact,
):
    ts0 = datetime.now()
    ts1 = ts0 + timedelta(hours=1)

    # Create Item
    item_name = "item 1"
    s = item_factory
    s.item_id = item_id
    s.name = item_name
    item = s.run()

    # Create customer type
    ct = customer_type_factory(customer_type_id=314997)  # 2h

    s = customer_type_rate_factory
    s.ctr_id = randint(1, 10_000_000)
    ctr = s.run()

    # create customer
    s = customer_factory
    c = s.run()

    ctc = editable_contact(booking_id=c.booking_id)

    # tweak the elements
    c.booking.customer_count = 1
    ctr.customer_type_id = ct.id
    c.customer_type_rate_id = ctr.id
    c.booking.availability.item = item
    c.booking.availability.start_at = ts0
    c.booking.availability.end_at = ts1
    c.booking.rebooked_to = None
    database.session.commit()

    d = DailyActivities(for_date=date.today()).run()
    expected = [
        {
            "availability_id": c.booking_id,
            "headline": f"{ctc.name}-{item_name}",
            "timestamp": str(ts0.time()).split(".")[0],
            "no_of_bikes": c.booking.customer_count,
            "duration": "2.0",
        }
    ]

    assert d == expected


@pytest.mark.parametrize(
    "ct_id, expected_duration",
    (
        (314997, "2.0"),
        (314998, "4.0"),
        (314999, "8.0"),
        (763051, "8.0"),
        (763050, "4.0"),
        (315000, "24.0"),
        (315001, "24.0"),
        (315002, "24.0"),
        (690082, "24.0"),
    ),
)
def test_daily_activities_success_for_rental_durations(
    ct_id,
    expected_duration,
    client,
    database,
    item_factory,
    customer_factory,
    customer_type_rate_factory,
    customer_type_factory,
    editable_contact,
):
    ts0 = datetime.now()
    ts1 = ts0 + timedelta(hours=1)

    # Create Item
    item_name = "item 1"
    s = item_factory
    s.item_id = 159068
    s.name = item_name
    item = s.run()

    # Create customer type
    ct = customer_type_factory(customer_type_id=ct_id)  # 2h

    s = customer_type_rate_factory
    s.ctr_id = randint(1, 10_000_000)
    ctr = s.run()

    # create customer
    s = customer_factory
    c = s.run()

    ctc = editable_contact(booking_id=c.booking_id)

    # tweak the elements
    c.booking.customer_count = 1
    ctr.customer_type_id = ct.id
    c.customer_type_rate_id = ctr.id
    c.booking.availability.item = item
    c.booking.availability.start_at = ts0
    c.booking.availability.end_at = ts1
    c.booking.rebooked_to = None
    database.session.commit()

    d = DailyActivities(for_date=date.today()).run()
    expected = [
        {
            "availability_id": c.booking_id,
            "headline": f"{ctc.name}-{item_name}",
            "timestamp": str(ts0.time()).split(".")[0],
            "no_of_bikes": c.booking.customer_count,
            "duration": expected_duration,
        }
    ]

    assert d == expected


@pytest.mark.parametrize("delta, expected", ((0, True), (1, False)))
def test_daily_activities_does_not_show_any_tour_when_availability_is_some_other_day(
    delta, expected, client, database, booking_factory, item_factory
):
    ts0 = datetime.now()

    # Create Item
    item_id = client.application.config["BIKE_TRACKER_ITEMS"]["regular_tours"][0]
    s = item_factory
    s.item_id = item_id
    s.name = "item 2"
    item = s.run()

    # Create a booking and tweak the availability to fit the test
    b, _ = randomizer(booking_factory.run())
    b.availability.item = item
    b.availability.start_at = ts0 + timedelta(days=delta)
    b.availability.end_at = ts0 + timedelta(days=delta)
    b.rebooked_to = None
    database.session.commit()

    d = DailyActivities(for_date=date.today()).run()
    assert bool(d) is expected


@pytest.mark.parametrize("status, expected", (("cancelled", False), ("ok", True)))
def test_daily_activities_does_not_show_any_tour_when_booking_is_cancelled(
    status, expected, client, database, booking_factory, item_factory
):
    ts0 = datetime.now()

    # Create Item
    item_id = client.application.config["BIKE_TRACKER_ITEMS"]["regular_tours"][0]
    s = item_factory
    s.item_id = item_id
    s.name = "item 2"
    item = s.run()

    # Create a booking and tweak the availability to fit the test
    b, _ = randomizer(booking_factory.run())
    b.availability.start_at = ts0
    b.availability.item = item
    b.rebooked_to = None
    b.status = status
    database.session.commit()

    d = DailyActivities(for_date=date.today()).run()
    assert bool(d) is expected


@pytest.mark.parametrize(
    "rebooked_to, expected", (("some_other_booking_id", False), (None, True))
)
def test_daily_activities_does_not_show_any_tour_when_booking_is_rebooked(
    rebooked_to,
    expected,
    client,
    database,
    booking_factory,
    item_factory,
    availability_factory,
):
    ts0 = datetime.now()

    # Create Item
    item_id = client.application.config["BIKE_TRACKER_ITEMS"]["regular_tours"][0]
    s = item_factory
    s.item_id = item_id
    s.name = "item 2"
    item = s.run()

    # Create a booking and tweak the availability to fit the test
    b, _ = randomizer(booking_factory.run())
    b.availability.start_at = ts0
    b.availability.item = item
    b.rebooked_to = rebooked_to
    database.session.commit()

    d = DailyActivities(for_date=date.today()).run()
    assert bool(d) is expected


@pytest.mark.parametrize("item_id, expected", ((111111, False), (159053, True)))
def test_daily_activities_does_not_show_any_tour_when_item_is_not_valid(
    item_id,
    expected,
    client,
    database,
    booking_factory,
    item_factory,
):
    ts0 = datetime.now()

    # Create Item
    s = item_factory
    s.item_id = item_id
    s.name = "item 2"
    item = s.run()

    # Create a booking and tweak the availability to fit the test
    b, _ = randomizer(booking_factory.run())
    b.availability.start_at = ts0
    b.availability.item = item
    b.rebooked_to = None
    database.session.commit()

    d = DailyActivities(for_date=date.today()).run()
    assert bool(d) is expected
