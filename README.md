# Fareharbor webhook
This is a simple app written in flask to process the webhooks provided by [Fareharbor](https://github.com/FareHarbor) which is a booking engine for activities.

# Motivation
Fareharbor app provides a great interface to deal with bookings for activities and a powerful reporting tool. However, it lacks visualizations about how the business is performing so usually one has to download the report for a given period and then manipulate the data.

With this webhook we have access to the booking instances in the moment they are produced or modified which allows to have live data to pull from a database and then make some visualizations using a tool for that purpose, like [redash](https://redash.io/)


# Installation
## Virtual environment
Create a virtual environment using your preferred approach
```shell
cd flask_app
python -m venv venv
source venv/bin/activate
```

Install the requirements
```shell
pip install --upgrade pip
pip install -r requirements.txt
```

## Create a db
You will need a couple of postgres dbs running under the hood, one for the data and the other for the tests as pytest does not create temp databases (or at least I didn't find how)

```shell
createdb webhook-sample
createdb webhook-tests
```

## Fill .env vars
Now head to .env-sample, clone to .env and replace the values with your local details:
```shell
cp .env-sampe .env
vim .env  # or your favourite editor
```

## Migrate the db
Once you have ready the details relative to the db you can migrate the models:
```shell
export FLASK_APP=fh_webhook  # you can also use export FLASK_APP=run.py
flask db migrate  # build the migration files
flask db upgrade  # apply the migrations in the db
```

## Run the server
With above, everything is in place to store requests, so spin up the server:
```shell
export FLASK_APP=fh_webhook
export FLASK_ENV=development
flask run
```

Finally you can just curl it from another terminal:
```shell
curl localhost:5000/test
# Hello from Flask
```

## Posting a sample file
With the server running you can record your first request in the db making use of the sample used in the tests
```shell
cd flask_app/tests
curl -H "Content-Type: application/json" -X POST \
--data @1626842330.051856.json \
fareharbor:FH_PASSWORD@localhost:5000/
```

Then on postgres you should have the sample
```sql
SELECT * FROM booking;
```

## Accessing the flask shell
An ipython shell is included in the requirements
```shell
export FLASK_APP=fh_webhook  # as always remember to say where flask lives
flask shell
```

## Run the test suite
```shell
export FLASK_APP=fh_webhook  # as always remember to say where flask lives
python -m pytest tests
```

# Database schema
The following charts are written in [mermaid](https://mermaidjs.github.io/) which is a very cool tool to draw diagrams using just the keyboard. Github doesn't display them out of the box and although there are [nice addons](https://github.com/BackMarket/github-mermaid-extension) for browsers, they are not that updated to mermaid's last version. Happily, there's an [online mermaid editor](https://mermaid-js.github.io/mermaid-live-editor/) that after creating offers a url that can be used as an image. 

## Per group
To easily understand the underlying structure, we can split the models in groups, these are:
* **Availability group:** this includes the availabilty model and the item model. Items are the products in the Fareharbor account, whereas availability controls the spots where activities can be allocated.
* **Booking group:** stores all the booking details along with some 1:1 fields: contact, that stores the booker contact data, and the cancellation policy.
It also contains the company models that is reached twice by two fields in the booking model: company, namely webhook owner company, and affiliate company, that points affiliates if any.
* **Custom Field group:** stores all the information related to custom fields: Each availability has several custom field instances whereas each booking stores the selected data in the custom field values model. Both effectivelly make a m2m to predefined custom fields.
* **Customer group:** Finally the customer group registers all the data relative to pricing for each availability and the checkin status

[![](https://mermaid.ink/img/eyJjb2RlIjoiZmxvd2NoYXJ0IExSXG5cdHN1YmdyYXBoIGcxXG5cdFx0ZGlyZWN0aW9uIEJUXG5cdFx0c3ViZ3JhcGggY2ZnIFtDdXN0b20gRmllbGQgR3JvdXBdXG5cdFx0XHRjZnZbY3VzdG9tIGZpZWxkIHZhbHVlc10tLWZrLS0-Y2ZbY3VzdG9tIGZpZWxkXVxuXHRcdFx0Y2ZpW2N1c3RvbSBmaWVsZCBpbnN0YW5jZXNdLS1may0tPmNmW2N1c3RvbSBmaWVsZF1cblx0XHRcdGNmW2N1c3RvbSBmaWVsZCBpbnN0YW5jZXNdLS1leHRlbmRlZCBvcHRpb25zIGZrLS0-Y2ZbY3VzdG9tIGZpZWxkXVxuXHRcdGVuZFxuXHRcdHN1YmdyYXBoIGNyZyBbQ3VzdG9tZXIgR3JvdXBdXG5cdFx0XHRkaXJlY3Rpb24gVEJcblx0XHRcdGNbY3VzdG9tZXJdLS1may0tPmNzdFtjaGVja2luIHN0YXR1c11cblx0XHRcdGNbY3VzdG9tZXJdLS1may0tPmN0cltjdXN0b21lciB0eXBlIHJhdGVdXG5cdFx0XHRjdHJbY3VzdG9tZXIgdHlwZSByYXRlXS0tZmstLT5jdHBbY3VzdG9tZXIgcHJvdG90eXBlXVxuXHRcdFx0Y3RyW2N1c3RvbWVyIHR5cGUgcmF0ZV0tLWZrLS0-Y3R0W2N1c3RvbWVyIHR5cGVdXG5cdFx0ZW5kXG5cdGVuZFxuXHRzdWJncmFwaCBnMFxuXHRcdHN1YmdyYXBoIGF2ZyBbQXZhaWxhYmlsaXR5IEdyb3VwXVxuXHRcdFx0ZGlyZWN0aW9uIExSXG5cdFx0XHRhdlthdmFpbGFiaWxpdHldLS1may0tPml0W2l0ZW1dXG5cdFx0ZW5kXG5cdFx0c3ViZ3JhcGggYmcgW0Jvb2tpbmcgR3JvdXBdXG5cdFx0XHRkaXJlY3Rpb24gVEJcblx0XHRcdGJbYm9va2luZ108LS0xOjEtLT5jdFtjb250YWN0XVxuXHRcdFx0Yltib29raW5nXTwtLTE6MS0tPmVjcFtlZmZlY3RpdmUgY2FuY2VsYXRpb25cXG5wb2xpY3ldXG5cdFx0XHRiW2Jvb2tpbmddLS1may0tPmN5W2NvbXBhbnldXG5cdFx0XHRiW2Jvb2tpbmddLS1may0tPmN5W2NvbXBhbnldXG5cdFx0ZW5kXG5cdGVuZFxuXHRzdHlsZSBjZmcgZmlsbDpsaWdodHllbGxvdztcblx0Y2xhc3NEZWYgbGlnaHRncmV5IGZpbGw6I0QwREVFNTtcblx0Y2xhc3NEZWYgZ3JlZW4gZmlsbDojQjJFMEQyO1xuXHRjbGFzc0RlZiB0cmFuc3BhcmVudCBmaWxsOiNmZmYsY29sb3I6I2ZmZixzdHJva2U6I2ZmZjtcblx0Y2xhc3MgY2ZnLGNyZyBsaWdodGdyZXk7XG5cdGNsYXNzIGF2ZyxiZyBncmVlbjtcblx0Y2xhc3MgZzAsZzEgdHJhbnNwYXJlbnQ7IiwibWVybWFpZCI6eyJ0aGVtZSI6ImRlZmF1bHQifSwidXBkYXRlRWRpdG9yIjpmYWxzZSwiYXV0b1N5bmMiOnRydWUsInVwZGF0ZURpYWdyYW0iOmZhbHNlfQ)](https://mermaid-js.github.io/mermaid-live-editor/edit##eyJjb2RlIjoiZ3JhcGggVERcbiAgICBBW0NocmlzdG1hc10gLS0-fEdldCBtb25leXwgQihHbyBzaG9wcGluZylcbiAgICBCIC0tPiBDe0xldCBtZSB0aGlua31cbiAgICBDIC0tPnxPbmV8IERbTGFwdG9wXVxuICAgIEMgLS0-fFR3b3wgRVtpUGhvbmVdXG4gICAgQyAtLT58VGhyZWV8IEZbZmE6ZmEtY2FyIENhcl1cbiAgIiwibWVybWFpZCI6IntcbiAgXCJ0aGVtZVwiOiBcImRlZmF1bHRcIlxufSIsInVwZGF0ZUVkaXRvciI6ZmFsc2UsImF1dG9TeW5jIjp0cnVlLCJ1cGRhdGVEaWFncmFtIjpmYWxzZX0)

## InterGroups relationships
At a higher level each booking can have several customers and each availability can have several bookings. There are also some connections that provide effectively m2m relationships:
* **Custom field values** make the m2m relationship between predefined custom fields and the chosen values for and specific booking or a customer. Note that there are custom fields that are booking level and some other custom fields at customer level.
* **Custom field:** Likewise, we have custom field instances for either availabilities or customer type rates that define which custom fields are available prior to choose a value by the contact.

[![](https://mermaid.ink/img/eyJjb2RlIjoiZmxvd2NoYXJ0IExSXG5cdHN1YmdyYXBoIGcxXG5cdFx0ZGlyZWN0aW9uIEJUXG5cdFx0c3ViZ3JhcGggY2ZnIFtDdXN0b20gRmllbGQgR3JvdXBdXG5cdFx0XHRjZnZbY3VzdG9tIGZpZWxkIHZhbHVlc11cblx0XHRcdGNmaVtjdXN0b20gZmllbGQgaW5zdGFuY2VzXVxuXHRcdGVuZFxuXHRcdHN1YmdyYXBoIGNyZyBbQ3VzdG9tZXIgR3JvdXBdXG5cdFx0XHRkaXJlY3Rpb24gVEJcblx0XHRcdGNbY3VzdG9tZXJdXG5cdFx0XHRjdHJbY3VzdG9tZXIgdHlwZSByYXRlXVxuXHRcdGVuZFxuXHRlbmRcblx0c3ViZ3JhcGggZzBcblx0XHRzdWJncmFwaCBhdmcgW0F2YWlsYWJpbGl0eSBHcm91cF1cblx0XHRcdGRpcmVjdGlvbiBMUlxuXHRcdFx0YXZbYXZhaWxhYmlsaXR5XVxuXHRcdGVuZFxuXHRcdHN1YmdyYXBoIGJnIFtCb29raW5nIEdyb3VwXVxuXHRcdFx0ZGlyZWN0aW9uIFRCXG5cdFx0XHRiW2Jvb2tpbmddXG5cdFx0ZW5kXG5cdGVuZFxuXHRjZmkgLS1may0tPiBjdHJcblx0Y2ZpLS1may0tPmF2XG5cdGItLWZrLS0-YXZcblx0Yy0tZmstLT5iXG5cdGNmdiAtLT4gYlxuXHRzdHlsZSBjZmcgZmlsbDpsaWdodHllbGxvdztcblx0Y2xhc3NEZWYgbGlnaHRncmV5IGZpbGw6I0QwREVFNTtcblx0Y2xhc3NEZWYgZ3JlZW4gZmlsbDojQjJFMEQyO1xuXHRjbGFzc0RlZiB0cmFuc3BhcmVudCBmaWxsOiNmZmYsY29sb3I6I2ZmZixzdHJva2U6I2ZmZjtcblx0Y2xhc3MgY2ZnLGNyZyBsaWdodGdyZXk7XG5cdGNsYXNzIGF2ZyxiZyBncmVlbjtcblx0Y2xhc3MgZzAsZzEgdHJhbnNwYXJlbnQ7IiwibWVybWFpZCI6eyJ0aGVtZSI6ImRlZmF1bHQifSwidXBkYXRlRWRpdG9yIjpmYWxzZSwiYXV0b1N5bmMiOnRydWUsInVwZGF0ZURpYWdyYW0iOmZhbHNlfQ)](https://mermaid-js.github.io/mermaid-live-editor/edit##eyJjb2RlIjoiZmxvd2NoYXJ0IExSXG5cdHN1YmdyYXBoIGcxXG5cdFx0ZGlyZWN0aW9uIEJUXG5cdFx0c3ViZ3JhcGggY2ZnIFtDdXN0b20gRmllbGQgR3JvdXBdXG5cdFx0XHRjZnZbY3VzdG9tIGZpZWxkIHZhbHVlc11cblx0XHRcdGNmaVtjdXN0b20gZmllbGQgaW5zdGFuY2VzXVxuXHRcdGVuZFxuXHRcdHN1YmdyYXBoIGNyZyBbQ3VzdG9tZXIgR3JvdXBdXG5cdFx0XHRkaXJlY3Rpb24gVEJcblx0XHRcdGNbY3VzdG9tZXJdXG5cdFx0XHRjdHJbY3VzdG9tZXIgdHlwZSByYXRlXVxuXHRcdGVuZFxuXHRlbmRcblx0c3ViZ3JhcGggZzBcblx0XHRzdWJncmFwaCBhdmcgW0F2YWlsYWJpbGl0eSBHcm91cF1cblx0XHRcdGRpcmVjdGlvbiBMUlxuXHRcdFx0YXZbYXZhaWxhYmlsaXR5XVxuXHRcdGVuZFxuXHRcdHN1YmdyYXBoIGJnIFtCb29raW5nIEdyb3VwXVxuXHRcdFx0ZGlyZWN0aW9uIFRCXG5cdFx0XHRiW2Jvb2tpbmddXG5cdFx0ZW5kXG5cdGVuZFxuXHRjZmkgLS1may0tPiBjdHJcblx0Y2ZpLS1may0tPmF2XG5cdGItLWZrLS0-YXZcblx0Yy0tZmstLT5iXG5cdGNmdiAtLT4gYlxuXHRzdHlsZSBjZmcgZmlsbDpsaWdodHllbGxvdztcblx0Y2xhc3NEZWYgbGlnaHRncmV5IGZpbGw6I0QwREVFNTtcblx0Y2xhc3NEZWYgZ3JlZW4gZmlsbDojQjJFMEQyO1xuXHRjbGFzc0RlZiB0cmFuc3BhcmVudCBmaWxsOiNmZmYsY29sb3I6I2ZmZixzdHJva2U6I2ZmZjtcblx0Y2xhc3MgY2ZnLGNyZyBsaWdodGdyZXk7XG5cdGNsYXNzIGF2ZyxiZyBncmVlbjtcblx0Y2xhc3MgZzAsZzEgdHJhbnNwYXJlbnQ7IiwibWVybWFpZCI6IntcbiAgXCJ0aGVtZVwiOiBcImRlZmF1bHRcIlxufSIsInVwZGF0ZUVkaXRvciI6dHJ1ZSwiYXV0b1N5bmMiOnRydWUsInVwZGF0ZURpYWdyYW0iOmZhbHNlfQ)

