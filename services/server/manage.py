from flask.cli import FlaskGroup
from google.cloud import bigquery
from project import create_app, client
from project.upload2bigquery import *
from project.api.models import covid_data_schema
from project.config import *

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command('build_dataset')
def build_dataset():
    dataset_id = "{}.{}".format(client.project, dataset_name)
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "asia-east1"

    # Send the dataset to the API for creation.
    # Raises google.api_core.exceptions.Conflict if the Dataset already
    # exists within the project.
    dataset = client.create_dataset(dataset)  # Make an API request.
    print("Created dataset {}.{}".format(client.project, dataset.dataset_id))


@cli.command('build_table')
def build_table():

    table_id = "{}.{}.{}".format(client.project, dataset_name, table_name)
    table = bigquery.Table(table_id, schema=covid_data_schema)
    table = client.create_table(table)  # Make an API request.
    print(
        "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
    )


@cli.command('update_today')
def update_today():
    get_latest_covid_data()


if __name__ == '__main__':
    cli()
