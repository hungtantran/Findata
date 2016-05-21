/**
 * Created by hungtantran on 5/19/16.
 */
import com.google.cloud.dataflow.sdk.Pipeline;
import com.google.cloud.dataflow.sdk.io.TextIO;
import com.google.cloud.dataflow.sdk.options.Default;
import com.google.cloud.dataflow.sdk.options.Description;
import com.google.cloud.dataflow.sdk.options.PipelineOptions;
import com.google.cloud.dataflow.sdk.options.PipelineOptionsFactory;
import com.google.cloud.dataflow.sdk.transforms.*;
import com.google.cloud.dataflow.sdk.values.KV;
import com.google.cloud.dataflow.sdk.values.PCollection;
import com.google.cloud.dataflow.sdk.values.PCollectionList;

import java.awt.*;
import java.lang.reflect.Array;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.regex.Pattern;
import java.util.regex.Matcher;


public class PriceChangeDetectionFlow {
  public static class MetricValue {
    float value;
    Date date;

    public MetricValue() {}

    public MetricValue(float value, Date date) {
      this.value = value;
      this.date = date;
    }
  }

  static class ExtractValues extends DoFn<String, KV<String, ArrayList<MetricValue>>> {
    @Override
    public void processElement(ProcessContext c) {
      DateFormat format = new SimpleDateFormat("yyyy-MM-dd");
      String line = c.element();
      String[] parts = line.split(";");
      if (parts.length == 0) {
        return;
      }

      String ticker = parts[0];
      if (ticker.length() == 0) {
        return;
      }

      ArrayList<MetricValue> vals = new ArrayList<MetricValue>();
      for (int i = 1; i < parts.length; ++i) {
        MetricValue value = new MetricValue();
        String[] valParts = parts[i].split(",");
        if (valParts.length != 2) {
          continue;
        }

        try {
          value.date = format.parse(valParts[0]);
          value.value = Float.parseFloat(valParts[1]);
        } catch (Exception e) {
          continue;
        }

        vals.add(value);
      }

      c.output(KV.of(ticker, vals));
    }
  }

  static class FindSuddenPriceMovementPerStock extends DoFn<String, KV<String, String>> {
    Date[] dates;
    Float threshold;

    public FindSuddenPriceMovementPerStock(Date[] dates, Float threshold) {
      this.dates = dates;
      this.threshold = threshold;
    }

    public ArrayList<MetricValue> parseLine(String[] parts) {
      DateFormat format = new SimpleDateFormat("yyyy-MM-dd");
      ArrayList<MetricValue> values = new ArrayList<MetricValue>();
      for (int i = 1; i < parts.length; ++i) {
        MetricValue value = new MetricValue();
        String[] valParts = parts[i].split(",");
        if (valParts.length != 2) {
          continue;
        }

        try {
          value.date = format.parse(valParts[0]);
          value.value = Float.parseFloat(valParts[1]);
        } catch (Exception e) {
          continue;
        }

        values.add(value);
      }

      return values;
    }

    @Override
    public void processElement(ProcessContext c) {
      String line = c.element();
      String[] parts = line.split(";");
      if (parts.length == 0) {
        return;
      }

      String ticker = parts[0];
      if (ticker.isEmpty()) {
        return;
      }

      ArrayList<MetricValue> values = this.parseLine(parts);

      int totalDate = 0;
      int index = 0;
      ArrayList<MetricValue> metricFound = new ArrayList<MetricValue>();
      StringBuilder resultStr = new StringBuilder();
      for (int i = 0; i < values.size() - 1; ++i) {
        if (index >= this.dates.length) {
          break;
        }

        if (values.get(i).date.compareTo(this.dates[index]) < 0) {
          continue;
        }

        if (values.get(i).date.compareTo(this.dates[index]) > 0) {
          index++;
          continue;
        }

        totalDate++;
        Float priceChange = (values.get(i + 1).value - values.get(i).value) / values.get(i).value * 100;
        if (priceChange > this.threshold) {
          metricFound.add(new MetricValue(priceChange, values.get(i).date));
          resultStr.append(values.get(i).date.toString() + "," + priceChange + ";");
        }
      }

      //KV<String, String> result = KV.of(ticker, metricFound.size() + ";" + totalDate + ";" + resultStr.toString());
      KV<String, String> result = KV.of(ticker, metricFound.size() + ";" + totalDate);
      c.output(result);
    }
  }

  public static class FormatAsTextFn extends DoFn<KV<String, String>, String> {
    @Override
    public void processElement(ProcessContext c) {
      c.output(c.element().getKey() + ";" + c.element().getValue());
    }
  }

  public static class ParseLine extends PTransform<PCollection<String>,
      PCollection<KV<String, ArrayList<MetricValue>>>> {
    @Override
    public PCollection<KV<String, ArrayList<MetricValue>>> apply(PCollection<String> lines) {
      PCollection<KV<String, ArrayList<MetricValue>>> parsedLines = lines.apply(
          ParDo.of(new ExtractValues()));

      return parsedLines;
    }
  }

  public static class FindSuddenPriceMovement extends
          PTransform<PCollection<String>, PCollection<KV<String, String>>> {
    Date[] dates;
    Float threshold;

    public FindSuddenPriceMovement(Date[] dates, Float threshold) {
      this.dates = dates;
      this.threshold = threshold;
    }

    @Override
    public PCollection<KV<String, String>> apply(PCollection<String> lines) {
      PCollection<KV<String, String>> results = lines.apply(ParDo.of(
              new FindSuddenPriceMovementPerStock(this.dates, this.threshold)));
      return results;
    }
  }

  public static interface SqlWordCountOptions extends PipelineOptions {
    @Description("Path of the file to read from")
    @Default.String("/media/hungtantran/HDD1/Users/hungtantran/PycharmProjects/Models/AnalyticPipeline/Dataflow/analyze_sql/src/test/output.txt*")
    String getInputFile();
    void setInputFile(String value);

    @Description("Path of the file to write to")
    @Default.String("/media/hungtantran/HDD1/Users/hungtantran/PycharmProjects/Models/AnalyticPipeline/Dataflow/analyze_sql/src/test/price_output.txt")
    String getOutputFile();
    void setOutputFile(String value);

    @Description("A comma-seprated list of date string to check")
    String getDateString();
    void setDateString(String dateString);

    @Description("The threshold to consider sudden price movement")
    @Default.Float(1)
    Float getPriceChangePercentageThreshold();
    void setPriceChangePercentageThreshold(Float threshold);
  }

  public static void main(String[] args) {
    try {
      SqlWordCountOptions options = PipelineOptionsFactory.fromArgs(args).withValidation()
              .as(SqlWordCountOptions.class);
      String[] dateArr = options.getDateString().split(",");
      DateFormat format = new SimpleDateFormat("yyyy-MM-dd");
      Date[] dates = new Date[dateArr.length];
      for (int i = 0; i < dateArr.length; ++i) {
        dates[i] = format.parse(dateArr[i]);
      }

      if (dates.length == 0) {
        System.out.println("Found no date");
        return;
      }

      System.out.println("Found " + dates.length + " dates");

      Pipeline p = Pipeline.create(options);
      p.apply(TextIO.Read.named("ReadLines").from(options.getInputFile()))
              .apply(new FindSuddenPriceMovement(dates, options.getPriceChangePercentageThreshold()))
              .apply(ParDo.of(new FormatAsTextFn()))
              .apply(TextIO.Write.named("WriteCounts").to(options.getOutputFile()));
      p.run();
    } catch (Exception e) {
      System.out.print(e);
    }
  }
}
