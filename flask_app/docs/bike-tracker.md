## Motivation
Due to the nature of the business we built the application for, a bike rental company, we found that it would be useful to measure the bike usage as just computing how old the bikes are would be misleading since some of them could have less usage than the others.

Given that FH provides the start and the end of the service, we can just assign bikes to availabilities and therefore know how long have they been riden.

## Process
By means of a mobile app a user scans a QR code that is on the bike and assign it to certain availability (sometimes called service in the code). This is done in two steps:
* Request the services of the day
* Add bikes to availability

### Request services of the day
The mobile app needs to get beforehand the services of the day to be able to assign the bikes. That request is performed through the endpoint `/bike-tracker/get-services/` that returns a dict like this encoded in a JWT:

```json
{
	"availabilities": [
		{
			"availability_id": 123,
			"headline": "13:30 rental service",
			"timestamp":  "13:30",
			"no_of_bikes": 5
		}
	],
    "bike_uuids" [
        {
            "uuid": "some_uuid",
            "display_name": "human_readable_name"
        }
    ]
}
```

### Add bikes to availability
Once the user scans as much bikes as the availability needs, the app calls the endpoint `/bike-tracker/add-bikes/` that will check this schema:
```json
{
	"availability_id": 123,
	"bikes": [
		"some_uuid",
		"some_other_uuid",
	]
}
```
Likewise, it will require the data encoded in a JWT otherwise it will return a `401`

**Possible errors:**
* 400 `Validation failed for add-bike request`: this should display the field that is failing.
* 404 `{"bike_uuid_error": "There were bikes that didn't match an entry in the db."}`
* 404 `{"availability_error": "The availability was not found."}`

### Replacing bikes
Additionally we include a service to replace the bike as sometimes a customer comes back to change it. In that case the app calls the `/bike-tracker/replace-bike/` that will check this schema:

```json
{
	"availability_id": 123,
	"bike_picked": "some_uuid",
	"bike_returned": "some_other_uuid"
}
```
**Possible errors:**
* 400 `Validation failed for add-bike request`: this should also display the field that is failing.

If the service fails to retrieve an entity from the database it will return a 404
* 404 `{"availability_error": "This instance of Availability model does not exist."}`
* 404 `{"bike_returned_error": "This instance of Bike model does not exist."}`
* 404 `{"bike_picked_error": "This instance of Bike model does not exist."}`
* 404 `{"bike_picked_error": "This instance of Bike model does not exist."}`

Also if it detects that the bike returned was not in the availability:
* 404 `{"bike_not_in_availability": "The bike some_uuid was not in the availability 123"}`
This is because although in the availability there's an end date it might happen that the user returns the bike before the time is over and the same bike can be used several times the same day so we need to include the `availability_id` in the request.
