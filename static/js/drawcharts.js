
    function chart(){


     //$nic = "324324324V"

     $nic = $('#nic').val();

     chartWeightLable = [];

     chartWeightData = [];

     chartHeightLable = [];

     chartHeightData = [];

     chartChestLable = [];

     chartChestData = [];

     chartFatLable = [];

     chartFatData = [];

     $.post("/getprogress" ,{nic : $nic} , function (data) {


         $.each(data.out, function(index, value) {

          //  console.log(index + ': ' + value.fat);

             chartWeightLable.push(value.date);
             chartHeightLable.push(value.date);
             chartFatLable.push(value.date);
             chartChestLable.push(value.date);

             chartWeightData.push(parseInt(value.weight));
             chartHeightData.push(parseInt(value.height));
             chartFatData.push(parseInt(value.fat));
             chartChestData.push(parseInt(value.chest));

              weightCharts();
              heightCharts();
              chestCharts();
              fatCharts();

        });


        //console.log(data);

     });


    };


     function weightCharts() {

     var ctx = document.getElementById("weightChart");

     var myChart = new Chart(ctx, {

     type: 'line',

     data: {

        labels: chartWeightLable,

        datasets: [{

            label: 'Weight',

            data: chartWeightData,

            backgroundColor: [
                '#ff0006',
            ],
            borderColor: [
                'rgba(255,99,132,1)',

            ],
            borderWidth: 1
        }]
    },

        options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero:true
                }
            }]
        },

        legend: {
            display: true,
            labels: {
                fontColor: 'rgb(255, 99, 132)',
                fontSize:20,
            }
        },

          }

        });

     }

     function heightCharts() {

     var ctx = document.getElementById("heightChart");

     var myChart = new Chart(ctx, {

     type: 'line',

     data: {

        labels: chartHeightLable,

        datasets: [{

            label: 'Height',

            data: chartHeightData,

            backgroundColor: [
                '#00e8ff',
            ],
            borderColor: [
                'rgba(255,99,132,1)',

            ],
            borderWidth: 1
        }]
    },

        options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero:true
                }
            }]
        },

        legend: {
            display: true,
            labels: {
                fontColor: 'rgb(255, 99, 132)',
                fontSize:20,
            }
        },

          }

        });

     }

     function chestCharts() {

     var ctx = document.getElementById("chestChart");

     var myChart = new Chart(ctx, {

     type: 'line',

     data: {

        labels: chartChestLable,

        datasets: [{

            label: 'Chest',

            data: chartChestData,

            backgroundColor: [
               '#00ff64',
            ],
            borderColor: [
                'rgba(255,99,132,1)',

            ],
            borderWidth: 1
        }]
    },

        options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero:true
                }
            }]
        },

        legend: {
            display: true,
            labels: {
                fontColor: 'rgb(255, 99, 132)',
                fontSize:20,
            }
        },

          }

        });

     }

     function fatCharts() {

     var ctx = document.getElementById("fatChart");

     var myChart = new Chart(ctx, {

     type: 'line',

     data: {

        labels: chartFatLable,

        datasets: [{

            label: 'Fat',

            data: chartFatData,

            backgroundColor: [
                '#C3FF03',
            ],
            borderColor: [
                'rgba(255,99,132,1)',

            ],
            borderWidth: 1
        }]
    },

        options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero:true
                }
            }]
        },

        legend: {
            display: true,
            labels: {
                fontColor: 'rgb(255, 99, 132)',
                fontSize:20,
            }
        },

          }

        });

     }

