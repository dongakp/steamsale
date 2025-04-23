// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily =
  '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

// Fetch data from Django API and render the chart
fetch("/api/chart-data/")
  .then(response => response.json())
  .then(data => {
    const ctx = document.getElementById("myBarChart");

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [{
          label: "Downloads", // You can change this label based on your dataset
          backgroundColor: "rgba(2,117,216,1)",
          borderColor: "rgba(2,117,216,1)",
          data: data.data,
        }],
      },
      options: {
        scales: {
          xAxes: [{
            gridLines: {
              display: false
            },
            ticks: {
              maxTicksLimit: 10
            }
          }],
          yAxes: [{
            ticks: {
              min: 0,
              // max: 15000, // You can make this dynamic if needed
              maxTicksLimit: 5
            },
            gridLines: {
              display: true
            }
          }],
        },
        legend: {
          display: false
        }
      }
    });
  })
  .catch(error => {
    console.error("Error loading chart data:", error);
  });
