class Graph {

  constructor() { }

  draw(element) {
    var data = new google.visualization.DataTable();

    data.addColumn('date', 'Date');
    data.addColumn('number', 'Value');
    data.addColumn('number', 'Value 2');

    var initTime = Date.now();

    const dayOffset = 1000 * 60 * 60 * 24; // sec, min, hour, day

    for(var i = 0; i < 100; i++)
    {
      data.addRow([new Date(initTime + i * dayOffset), Math.random(), Math.random()]);
    }

    var options = {
      chart: {
        title: 'Some Metrics',
        subtitle: 'a subtitle',
      },
      width: 900,
      height: 500,
      hAxis: { format: 'M/d/yy'}
    };

    var chart = new google.charts.Line(element);
    chart.draw(data, google.charts.Line.convertOptions(options));
  }
}

export default Graph;
