__author__ = 'hungtantran'

import init_app

import datetime
import os

import logger
from Database.bigquery_client import BigQueryClient
from UpdatePipeline.Flow import Flow
from UpdatePipeline.Flow import FlowStatus


class BigQueryToCloudStorageFlow(Flow):
    bigquery_client = None

    def __init__(self, bigquery_client):
        super(BigQueryToCloudStorageFlow, self).__init__("BigQueryToCloudStorageFlow")
        self.bigquery_client = bigquery_client

    def status(self):
        # TODO: implement async and return real status here
        return self.status

    def start(self):
        # Dataflow command
        local_project_root = ''
        dataflow_cmd = 'mvn compile -f %sAnalyticPipeline/Dataflow/analyze_sql/pom.xml exec:java -Dexec.mainClass=BigQueryToCloudStorage -Dexec.args=' % local_project_root

        # Project
        project = '--project=%s' % 'model-1256'

        # Query String
        query_string = "SELECT ticker, value, start_date FROM model.metrics WHERE metric_name = 'adj_close'"
        query_string = query_string.replace("'", "&quot")
        query = '--query=%s' % query_string

        # Staging location
        staging_location = '--stagingLocation=%s' % ('gs://market_data_analysis_staging/')

        # Runner
        runner = '--runner=%s' % 'BlockingDataflowPipelineRunner'

        # Output file location
        now = datetime.datetime.now()
        output_filename = 'bigquery/%s/%s/%s/adj_close.txt' % (now.year, now.month, now.day)
        output_file = '--output=gs://%s/%s' % ('market_data_analysis', output_filename)

        dataflow_cmd = '%s"%s %s %s %s %s"' % (
            dataflow_cmd, project, staging_location, query, output_file, runner)

        # Run the dataflow command
        logger.Logger.info(dataflow_cmd)
        os.system(dataflow_cmd)

        self.status = FlowStatus.SUCCESS

    def rollback(self):
        raise NotImplementedError