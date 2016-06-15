__author__ = 'hungtantran'

import init_app

import datetime
import os

import logger
from UpdatePipeline.Flow import Flow
from UpdatePipeline.Flow import FlowStatus


class ETLFlow(Flow):
    dataflow_local = False

    def __init__(self, dataflow_local):
        super(ETLFlow, self).__init__("ETLFlow")
        self.dataflow_local = dataflow_local

    def status(self):
        # TODO: implement async and return real status here
        return self.status

    def start(self):
        now = datetime.datetime.now()
        local_project_root = ''
        dataflow_cmd = 'mvn compile -f %sAnalyticPipeline/Dataflow/analyze_sql/pom.xml exec:java -Dexec.mainClass=ETLCsvFlow -Dexec.args=' % local_project_root

        # Project
        project = '--project=%s' % 'model-1256'

        # Staging location
        staging_location = '--stagingLocation=%s%s' % (
            local_project_root,
            'AnalyticPipeline/Dataflow/analyze_sql/src/test/')
        if not self.dataflow_local:
            staging_location = '--stagingLocation=%s' % (
                'gs://market_data_analysis_staging/')

        # Input file location
        input_file = '--inputFile=%s%s' % (
            local_project_root,
            'AnalyticPipeline/Dataflow/analyze_sql/src/test/result.txt')
        if not self.dataflow_local:
            input_file = '--inputFile=gs://market_data_analysis/%s/%s/%s/total' % (now.year, now.month, now.day)

        # Output file location
        output_file = '--outputFile=%s%s' % (
            local_project_root,
            'AnalyticPipeline/Dataflow/analyze_sql/src/test/price_output.txt')
        if not self.dataflow_local:
            output_file = '--output=gs://market_data_analysis/csv/%d/%d/%d/result.csv' % (now.year, now.month, now.day)

        # Runner
        runner = '--runner=%s' % 'DirectPipelineRunner'
        if not self.dataflow_local:
            runner = '--runner=%s' % 'BlockingDataflowPipelineRunner'

        dataflow_cmd = '%s"%s %s %s %s %s"' % (
            dataflow_cmd, project, staging_location, input_file, output_file, runner)

        # Run the dataflow command
        logger.Logger.info(dataflow_cmd)
        os.system(dataflow_cmd)

        self.status = FlowStatus.SUCCESS

    def rollback(self):
        raise NotImplementedError