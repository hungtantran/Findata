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

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.concurrent.TimeUnit;


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

  static class FindSuddenPriceMovementPerStock extends DoFn<String, KV<String, String>> {
    String dateString;
    Float threshold;
    Integer timeFrameInDays;

    public FindSuddenPriceMovementPerStock(String dateString, Float threshold, Integer timeFrameInDays) {
      this.dateString = dateString;
      this.threshold = threshold;
      this.timeFrameInDays = timeFrameInDays;
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

    public ArrayList<Date> parseDateString(String[] parts) {
      DateFormat format = new SimpleDateFormat("yyyy-MM-dd");
      ArrayList<Date> values = new ArrayList<Date>();
      for (int i = 0; i < parts.length; ++i) {
        try {
          values.add(format.parse(parts[i]));
        } catch (Exception e) {
          continue;
        }
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
      ArrayList<Date> dates = this.parseDateString(this.dateString.split(","));

      int totalDate = 0;
      int index = 0, i = 0;
      ArrayList<MetricValue> increaseFound = new ArrayList<MetricValue>();
      ArrayList<MetricValue> decreaseFound = new ArrayList<MetricValue>();
      StringBuilder equalStr = new StringBuilder();
      for (i = 0; i < values.size();) {
        if (index >= dates.size()) {
          break;
        }

        if (values.get(i).date.compareTo(dates.get(index)) > 0) {
          index++;
          continue;
        }

        if (values.get(i).date.compareTo(dates.get(index)) < 0) {
          i++;
          continue;
        }

        int diff = 1;
        while (i + diff < values.size()) {
          long diffTime = values.get(i + diff).date.getTime() - values.get(i).date.getTime();
          long diffDays = TimeUnit.DAYS.convert(diffTime, TimeUnit.MILLISECONDS);

          if (diffDays >= this.timeFrameInDays) {
            totalDate++;
            Float priceChange = (values.get(i + diff).value - values.get(i).value) / values.get(i).value * 100;
            if (priceChange > this.threshold) {
              increaseFound.add(new MetricValue(priceChange, values.get(i).date));
            } else if (priceChange < -this.threshold) {
              decreaseFound.add(new MetricValue(priceChange, values.get(i).date));
            }

            break;
          }

          diff++;
        }

        index++;
        i++;
      }

      float percentIncrease = (float)increaseFound.size() / (float)totalDate;
      float percentDecrease = (float)decreaseFound.size() / (float)totalDate;

      KV<String, String> result = KV.of(ticker, "Increase;" + increaseFound.size() + ";" + totalDate + ";" + percentIncrease + ";" + values.size());
      c.output(result);
      KV<String, String> result2 = KV.of(ticker, "Decrease;" + decreaseFound.size() + ";" + totalDate + ";" + percentDecrease + ";" + values.size());
      c.output(result2);
    }
  }

  public static class FormatAsTextFn extends DoFn<KV<String, String>, String> {
    @Override
    public void processElement(ProcessContext c) {
      c.output(c.element().getKey() + ";" + c.element().getValue());
    }
  }

  public static class FindSuddenPriceMovement extends
          PTransform<PCollection<String>, PCollection<KV<String, String>>> {
    String dateString;
    Float threshold;
    Integer timeFrameInDays;

    public FindSuddenPriceMovement(String dateString, Float threshold, Integer timeFrameInDays) {
      this.dateString = dateString;
      this.threshold = threshold;
      this.timeFrameInDays = timeFrameInDays;
    }

    @Override
    public PCollection<KV<String, String>> apply(PCollection<String> lines) {
      PCollection<KV<String, String>> results = lines.apply(ParDo.of(
              new FindSuddenPriceMovementPerStock(this.dateString, this.threshold, this.timeFrameInDays)));
      return results;
    }
  }

  public static interface SqlWordCountOptions extends PipelineOptions {
    @Description("Path of the file to read from")
    @Default.String("/media/hungtantran/HDD1/Users/hungtantran/PycharmProjects/Models/AnalyticPipeline/Dataflow/analyze_sql/src/test/result.txt*")
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
    @Default.Float(0)
    Float getPriceChangePercentageThreshold();
    void setPriceChangePercentageThreshold(Float threshold);

    @Description("The time frame in days to consider")
    @Default.Integer(1)
    Integer getTimeFrameInDays();
    void setTimeFrameInDays(Integer timeFrameInDays);
  }

  public static void main(String[] args) {
    try {
      SqlWordCountOptions options = PipelineOptionsFactory.fromArgs(args).withValidation()
              .as(SqlWordCountOptions.class);

      Pipeline p = Pipeline.create(options);
      p.apply(TextIO.Read.named("ReadLines").from(options.getInputFile()))
              .apply(new FindSuddenPriceMovement(
                      options.getDateString(),
                      options.getPriceChangePercentageThreshold(),
                      options.getTimeFrameInDays()))
              .apply(ParDo.of(new FormatAsTextFn()))
              .apply(TextIO.Write.named("WriteCounts").to(options.getOutputFile()));
      p.run();
    } catch (Exception e) {
      System.out.print(e);
    }
  }
}
