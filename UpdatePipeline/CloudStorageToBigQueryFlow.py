__author__ = 'hungtantran'

import init_app

import datetime
import os

import logger
from Database.bigquery_client import BigQueryClient
from UpdatePipeline.Flow import Flow
from UpdatePipeline.Flow import FlowStatus


class CloudStorageToBigQueryFlow(Flow):
    bigquery_client = None

    def __init__(self, bigquery_client):
        super(CloudStorageToBigQueryFlow, self).__init__("CloudStorageToBigQueryFlow")
        self.bigquery_client = bigquery_client

    def status(self):
        # TODO: implement async and return real status here
        return self.status

    def start(self):
        now = datetime.datetime.now()
        storage_path = "gs://market_data_analysis/csv/%d/%d/%d/result.csv-*" % (now.year, now.month, now.day)
        table_name = "metrics"
        job = self.bigquery_client.load_cloud_storage_into_bigquery(
            storage_path=storage_path,
            table_name=table_name)

        self.status = FlowStatus.SUCCESS

    def rollback(self):
        raise NotImplementedError