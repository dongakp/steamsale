// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

// Area Chart Example
var ctx = document.getElementById("myAreaChart");
var myLineChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: ["anything", "something", "go", "for", "lets", "see", "the", "limit", "of", "this", "entire", "page", "im", "curious"],
    datasets: [{
      label: "Sessions",
      lineTension: 0.3,
      backgroundColor: "rgba(2,117,216,0.2)",
      borderColor: "rgba(2,117,216,1)",
      pointRadius: 5,
      pointBackgroundColor: "rgba(2,117,216,1)",
      pointBorderColor: "rgba(255,255,255,0.8)",
      pointHoverRadius: 5,
      pointHoverBackgroundColor: "rgba(2,117,216,1)",
      pointHitRadius: 50,
      pointBorderWidth: 2,
      data: [5000, 12000, 9000, 15000, 18000, 21000, 17000, 14000, 16000, 22000, 25000, 23000, 24000, 0],
    }],
  },
  options: {
    scales: {
      xAxes: [{
        ticks: {
          autoSkip: false,           // 👈 Don't skip any labels
          maxRotation: 45,           // 👈 Rotate for readability
          minRotation: 45
        },
        gridLines: {
          display: false
        }
      }],
      yAxes: [{
        ticks: {
          min: 0,
          max: 30000,
          maxTicksLimit: 6
        },
        gridLines: {
          color: "rgba(0, 0, 0, .125)",
        }
      }],
    },
    legend: {
      display: false
    }
  }
});
