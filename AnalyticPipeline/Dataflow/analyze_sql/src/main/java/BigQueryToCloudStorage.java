import com.google.api.services.bigquery.model.TableCell;
import com.google.api.services.bigquery.model.TableRow;
import com.google.cloud.dataflow.sdk.Pipeline;
import com.google.cloud.dataflow.sdk.io.BigQueryIO;
import com.google.cloud.dataflow.sdk.io.TextIO;
import com.google.cloud.dataflow.sdk.options.Default;
import com.google.cloud.dataflow.sdk.options.Description;
import com.google.cloud.dataflow.sdk.options.PipelineOptions;
import com.google.cloud.dataflow.sdk.options.PipelineOptionsFactory;
import com.google.cloud.dataflow.sdk.transforms.*;
import com.google.cloud.dataflow.sdk.values.KV;
import com.google.cloud.dataflow.sdk.values.PCollection;

import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;


public class BigQueryToCloudStorage {
  static class ExtractRowFn extends DoFn<TableRow, KV<String,String>> {
    @Override
    public void processElement(ProcessContext c) {
      TableRow row = c.element();
      Object[] cells = row.values().toArray();
      if (cells.length != 3) {
        return;
      }

      String tableName = (String)cells[0];
      Double value = (Double)cells[1];
      String startDate = (String)cells[2];
      c.output(KV.of(tableName, startDate + "," + value.toString()));
    }
  }

  static class SortLineFn extends DoFn<KV<String, String>, KV<String, String>> {
    @Override
    public void processElement(ProcessContext c) {
      String tableName = c.element().getKey();
      String valueStr = c.element().getValue();
      String[] values = valueStr.split(";");

      Arrays.sort(values, Collections.<String>reverseOrder());
      StringBuilder sortedValueStrBuilder = new StringBuilder();
      for (String value : values) {
        sortedValueStrBuilder.append(value + ";");
      }
      c.output(KV.of(tableName, sortedValueStrBuilder.toString()));
    }
  }

  public static class FormatAsTextFn extends DoFn<KV<String, String>, String> {
    @Override
    public void processElement(ProcessContext c) {
      String[] vals = c.element().getValue().split(";");
      Arrays.sort(vals, 0, vals.length);
      StringBuilder outputStr = new StringBuilder();
      for (String value : vals) {
        if (value.length() > 0) {
          outputStr.append(value + ";");
        }
      }

      c.output(c.element().getKey() + ";" + outputStr.toString());
    }
  }

  public static class ParseTableRow extends PTransform<PCollection<TableRow>,
      PCollection<KV<String, String>>> {
    @Override
    public PCollection<KV<String, String>> apply(PCollection<TableRow> lines) {
      PCollection<KV<String, String>> parsedLines = lines.apply(
              ParDo.of(new ExtractRowFn()));
      return parsedLines;
    }
  }

  public static class SortLines extends PTransform<PCollection<KV<String, String>>,
          PCollection<KV<String, String>>> {
    @Override
    public PCollection<KV<String, String>> apply(PCollection<KV<String, String>> lines) {
      PCollection<KV<String, String>> sortedLines = lines.apply(
              ParDo.of(new SortLineFn()));
      return sortedLines;
    }
  }

  public static class CombineLine extends PTransform<PCollection<KV<String, String>>,
          PCollection<KV<String, String>>> {
    public static class MergeString extends Combine.KeyedCombineFn<String, String, String, String> {
      public String createAccumulator(String key) {
        return new String();
      }

      public String addInput(String key, String accum, String input) {
        accum += input + ";";
        return accum;
      }

      public String mergeAccumulators(String key, Iterable<String> accums) {
        String merged = new String();
        for (String accum : accums) {
          merged += accum + ";";
        }
        return merged;
      }

      public String extractOutput(String key, String accum) {
        return accum;
      }
    }

    @Override
    public PCollection<KV<String, String>> apply(PCollection<KV<String, String>> lines) {
      PCollection<KV<String, String>> combineLines = lines.apply(Combine.perKey(new CombineLine.MergeString()));
      return combineLines;
    }
  }

  public static interface BigQueryToCloudStorageOptions extends PipelineOptions {
    @Description("Query String")
    String getQuery();
    void setQuery(String value);

    @Description("Path of the file to write to")
    @Default.String("gs://market_data_analysis/bigquery_output.txt")
    String getOutput();
    void setOutput(String value);
  }

  public static void main(String[] args) {
    BigQueryToCloudStorageOptions options = PipelineOptionsFactory.fromArgs(args).withValidation()
      .as(BigQueryToCloudStorageOptions.class);
    String query = options.getQuery();
    options.setQuery(query.replaceAll("&quot", "'"));

    System.out.println(options.getOutput());
    System.out.println(options.getQuery());

    Pipeline p = Pipeline.create(options);
    p.apply(BigQueryIO.Read.named("BigQueryToCloudStorage")
            .fromQuery(options.getQuery()))
            .apply(new ParseTableRow())
            .apply(new CombineLine())
            .apply(new SortLines())
            .apply(ParDo.of(new FormatAsTextFn()))
            .apply(TextIO.Write.named("WriteCounts").to(options.getOutput()));

    p.run();
  }
}
