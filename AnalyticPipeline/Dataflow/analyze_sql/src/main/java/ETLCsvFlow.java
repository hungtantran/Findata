import com.google.cloud.dataflow.sdk.Pipeline;
import com.google.cloud.dataflow.sdk.io.TextIO;
import com.google.cloud.dataflow.sdk.options.Default;
import com.google.cloud.dataflow.sdk.options.Description;
import com.google.cloud.dataflow.sdk.options.PipelineOptions;
import com.google.cloud.dataflow.sdk.options.PipelineOptionsFactory;
import com.google.cloud.dataflow.sdk.transforms.*;
import com.google.cloud.dataflow.sdk.values.KV;
import com.google.cloud.dataflow.sdk.values.PCollection;

import java.util.HashMap;
import java.util.regex.Pattern;
import java.util.regex.Matcher;


public class ETLCsvFlow {
  static class ExtractWordsFn extends DoFn<String, String> {
    private String extractTableName(String line) {
      String tablename = "";

      int startIndex = line.indexOf("`");
      if (startIndex <= 0) {
        return tablename;
      }

      int endIndex = line.indexOf("`", startIndex + 1);
      if (endIndex <= 0) {
        return tablename;
      }

      tablename = line.substring(startIndex + 1, endIndex);
      return tablename;
    }

    @Override
    public void processElement(ProcessContext c) {
      String line = c.element();
      if (!line.startsWith("INSERT INTO")) {
        return;
      }

      String tablename = this.extractTableName(line);
      if (!tablename.endsWith("_metrics")) {
        return;
      }

      String ticker = tablename.substring(0, tablename.length() - 8);
      StringBuilder outputStr = new StringBuilder();
      HashMap<String, StringBuilder> nameToMetrics;

      int numValue = 0;
      Pattern pattern = Pattern.compile("([0-9]+),'(.+)',(.+),'(.+)','(.+)','(.+)',(.+)\\),");
      String[] values = line.split("\\(");
      for (String value : values) {
        Matcher matcher = pattern.matcher(value);
        while (matcher.find()) {
          StringBuilder strBuilder = new StringBuilder();
          // Append ticker
          strBuilder.append(tablename + ",");
          // Append row id
          strBuilder.append(matcher.group(1) + ",");
          // Append metric name
          strBuilder.append("" + matcher.group(2) + ",");
          // Append metric value
          strBuilder.append(matcher.group(3) + ",");
          // Append metric unit
          strBuilder.append("" + matcher.group(4) + ",");
          // Append start date
          strBuilder.append("" + matcher.group(5) + ",");
          // Append end date
          strBuilder.append("" + matcher.group(6) + ",");
          // Append metadata
          strBuilder.append("" + matcher.group(7));
          c.output(strBuilder.toString());
        }
      }
    }
  }

  public static class ParseLine extends PTransform<PCollection<String>, PCollection<String>> {
    @Override
    public PCollection<String> apply(PCollection<String> lines) {
      PCollection<String> parsedLines = lines.apply(
          ParDo.of(new ExtractWordsFn()));

      return parsedLines;
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

  public static interface SqlWordCountOptions extends PipelineOptions {
    @Description("Path of the file to read from")
    @Default.String("/media/hungtantran/HDD1/Users/hungtantran/PycharmProjects/Models/AnalyticPipeline/Dataflow/analyze_sql/src/test/test_sql_dump.txt")
    String getInputFile();
    void setInputFile(String value);

    @Description("Path of the file to write to")
    @Default.String("/media/hungtantran/HDD1/Users/hungtantran/PycharmProjects/Models/AnalyticPipeline/Dataflow/analyze_sql/src/test/outputcsv.txt")
    String getOutput();
    void setOutput(String value);
  }

  public static void main(String[] args) {
    SqlWordCountOptions options = PipelineOptionsFactory.fromArgs(args).withValidation()
      .as(SqlWordCountOptions.class);
    Pipeline p = Pipeline.create(options);

    p.apply(TextIO.Read.named("ReadLines").from(options.getInputFile()))
     .apply(new ParseLine())
     .apply(TextIO.Write.named("WriteCounts").to(options.getOutput()));

    p.run();
  }
}
