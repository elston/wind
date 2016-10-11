/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('WeatherPlotCtrl', ['$scope', '$q', '$uibModalInstance', 'entity', 'locationService',
    function ($scope, $q, $uibModalInstance, entity, locationService) {
        'use strict';

        var locationId = entity.id;
        $scope.locationName = entity.name;
        $scope.tempmEnabled = false;
        $scope.wspdmEnabled = true;
        $scope.wdirdEnabled = false;

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $scope.updateSeriesSet = function () {
            for (var i = 0; i < $scope.chart.series.length - 1; i += 3) {
                if ($scope.tempmEnabled) {
                    $scope.chart.series[i + 0].show();
                } else {
                    $scope.chart.series[i + 0].hide();
                }
                if ($scope.wspdmEnabled) {
                    $scope.chart.series[i + 1].show();
                } else {
                    $scope.chart.series[i + 1].hide();
                }
                if ($scope.wdirdEnabled) {
                    $scope.chart.series[i + 2].show();
                } else {
                    $scope.chart.series[i + 2].hide();
                }
            }
        };

        $scope.formatAMPM = function (date) {
            var hours = date.getHours();
            var minutes = date.getMinutes();
            var ampm = hours >= 12 ? 'pm' : 'am';
            hours = hours % 12;
            hours = hours ? hours : 12; // the hour '0' should be '12'
            minutes = minutes < 10 ? '0'+minutes : minutes;
            var strTime = hours + ':' + minutes + ' ' + ampm;
            return strTime;
        }

        $q.all([
                locationService.getHistory(locationId)
                    .then(function (result) {
                            $scope.history_data = result;
                        },
                        function (error) {
                            alertify.error('Error while getting history for location "' + $scope.locationName +
                                '": ' + error);
                        }),
                locationService.getForecast(locationId)
                    .then(function (result) {
                            $scope.forecast_data = result;
                        },
                        function (error) {
                            alertify.error('Error while getting forecast for location "' + $scope.locationName +
                                '": ' + error);
                        })
            ])
            .then(function () {
                $('#weather-chart-container').empty();
                var series = [{
                    name: 'Temperature, C (observation)',
                    data: $scope.history_data.data.tempm,
                    tooltip: {
                        valueDecimals: 1
                    },
                    color: 'red'
                }, {
                    name: 'Wind speed, km/h (observation)',
                    data: $scope.history_data.data.wspdm,
                    tooltip: {
                        valueDecimals: 1
                    },
                    yAxis: 1,
                    color: 'blue'
                }, {
                    name: 'Wind direction, degrees (observation)',
                    data: $scope.history_data.data.wdird,
                    tooltip: {
                        valueDecimals: 0
                    },
                    yAxis: 2,
                    color: 'darkgrey'
                }];

                if ($scope.forecast_data.last_11am) {
                    series.push({
                        name: 'Temperature, C (forecast values from ' + $scope.forecast_data.last_11am.time.replace(/:00.*$/, 'am') + ')',
                        data: $scope.forecast_data.last_11am.tempm,
                        tooltip: {
                            valueDecimals: 1
                        },
                        color: 'red',
                        dashStyle: 'Dash'
                    });
                    series.push({
                        name: 'Wind speed, km/h (forecast values from ' + $scope.forecast_data.last_11am.time.replace(/:00.*$/, 'am') + ')',
                        data: $scope.forecast_data.last_11am.wspdm,
                        tooltip: {
                            valueDecimals: 1
                        },
                        yAxis: 1,
                        color: 'blue',
                        dashStyle: 'Dash'
                    });
                    series.push({
                        name: 'Wind direction, degrees (forecast values from ' + $scope.forecast_data.last_11am.time.replace(/:00.*$/, 'am') + ')',
                        data: $scope.forecast_data.last_11am.wdird,
                        tooltip: {
                            valueDecimals: 1
                        },
                        yAxis: 2,
                        color: 'darkgrey',
                        dashStyle: 'Dash'
                    });
                }

                if ($scope.forecast_data.last_11pm) {
                    series.push({
                        name: 'Temperature, C (forecast values from ' + $scope.forecast_data.last_11pm.time.replace(/:00.*$/, 'pm') + ')',
                        data: $scope.forecast_data.last_11pm.tempm,
                        tooltip: {
                            valueDecimals: 1
                        },
                        color: 'red',
                        dashStyle: 'Dot'
                    });
                    series.push({
                        name: 'Wind speed, km/h (forecast values from ' + $scope.forecast_data.last_11pm.time.replace(/:00.*$/, 'pm') + ')',
                        data: $scope.forecast_data.last_11pm.wspdm,
                        tooltip: {
                            valueDecimals: 1
                        },
                        yAxis: 1,
                        color: 'blue',
                        dashStyle: 'Dot'
                    });
                    series.push({
                        name: 'Wind direction, degrees (forecast values from ' + $scope.forecast_data.last_11pm.time.replace(/:00.*$/, 'pm') + ')',
                        data: $scope.forecast_data.last_11pm.wdird,
                        tooltip: {
                            valueDecimals: 1
                        },
                        yAxis: 2,
                        color: 'darkgrey',
                        dashStyle: 'Dot'
                    });
                }

                if ($scope.forecast_data.last) {
                    series.push({
                        name: 'Temperature, C (latest forecast by ' + $scope.forecast_data.last.time + ')',
                        data: $scope.forecast_data.last.tempm,
                        tooltip: {
                            valueDecimals: 1
                        },
                        color: 'red',
                        dashStyle: 'DashDot'
                    });
                    series.push({
                        name: 'Wind speed, km/h (latest forecast by ' + $scope.forecast_data.last.time + ')',
                        data: $scope.forecast_data.last.wspdm,
                        tooltip: {
                            valueDecimals: 1
                        },
                        yAxis: 1,
                        color: 'blue',
                        dashStyle: 'DashDot'
                    });
                    series.push({
                        name: 'Wind direction, degrees (latest forecast by ' + $scope.forecast_data.last.time + ')',
                        data: $scope.forecast_data.last.wdird,
                        tooltip: {
                            valueDecimals: 1
                        },
                        yAxis: 2,
                        color: 'darkgrey',
                        dashStyle: 'DashDot'
                    });
                }

                $scope.chart = new Highcharts.StockChart({
                    chart: {
                        renderTo: 'weather-chart-container',
                        animation: false
                    },
                   rangeSelector: {
                       selected: 0,
                       buttons: [
                           {
                               type: 'hour',
                               count: 24,
                               text: '24h'

                           }, {
                               type: 'hour',
                               count: 36,
                               text: '36h'
                           }, {
                               type: 'month',
                               count: 1,
                               text: '1m'
                           }, {
                               type: 'all',
                               text: 'All'
                           }
                       ],
                       inputDateFormat: '%b %e, %Y %H:%M',
                       inputEditDateFormat: '%Y-%m-%d %H:%M',
                       inputBoxWidth: 150,
                   },
                    tooltip: {
                        xDateFormat: '%b %e, %Y, %H:%M'
                    },
                    credits: {
                        enabled: false
                    },
                    legend: {
                        enabled: true,
                    },
                    xAxis: {
                        title: {
                            text: 'Time (' + $scope.history_data.tzinfo + ')'
                        },
                        min: new Date(Date.UTC(new Date().getUTCFullYear(), new Date().getUTCMonth(), new Date().getUTCDate())).setUTCHours(0, 0, 0, 0),
                        max: new Date(Date.UTC(new Date().getUTCFullYear(), new Date().getUTCMonth(), new Date().getUTCDate())).setUTCHours(0, 0, 0, 0) + 24 * 3600000,
                        events : {
                            afterSetExtremes: function(e) {
                                if (e.trigger == "rangeSelectorButton" &&
                                    e.rangeSelectorButton.text == "24h"){
                                    setTimeout(function(){
                                        $scope.chart.xAxis[0].setExtremes(
                                            new Date(Date.UTC(new Date().getUTCFullYear(), new Date().getUTCMonth(), new Date().getUTCDate())).setUTCHours(0, 0, 0, 0),
                                            new Date(Date.UTC(new Date().getUTCFullYear(), new Date().getUTCMonth(), new Date().getUTCDate())).setUTCHours(0, 0, 0, 0) + 24 * 3600000);
                                    }, 1);
                                } else if (e.trigger == "rangeSelectorButton" &&
                                    e.rangeSelectorButton.text == "36h"){
                                    setTimeout(function(){
                                        $scope.chart.xAxis[0].setExtremes(
                                            new Date(Date.UTC(new Date().getUTCFullYear(), new Date().getUTCMonth(), new Date().getUTCDate())).setUTCHours(12, 0, 0, 0),
                                            new Date(Date.UTC(new Date().getUTCFullYear(), new Date().getUTCMonth(), new Date().getUTCDate())).setUTCHours(12, 0, 0, 0) + 36 * 3600000);
                                    }, 1);
                                } else if (e.trigger == "rangeSelectorButton" &&
                                    e.rangeSelectorButton.text == "1m") {
                                    setTimeout(function(){
                                        $scope.chart.xAxis[0].setExtremes(
                                            new Date(Date.UTC(new Date().getUTCFullYear(), new Date().getUTCMonth(), new Date().getUTCDate())).setUTCHours(0, 0, 0, 0),
                                            new Date(new Date(Date.UTC(new Date().getUTCFullYear(), new Date().getUTCMonth(), new Date().getUTCDate())).setUTCHours(0, 0, 0, 0)).setUTCMonth(new Date().getMonth()+1));
                                    }, 1);
                                }
                            }
                        }
                    },
                    yAxis: [{
                        title: {
                            text: 'Temperature, C'
                        }
                    }, {
                        title: {
                            text: 'Wind speed, km/h'
                        }
                    }, {
                        title: {
                            text: 'Wind direction, degrees'
                        }
                    }],
                    series: series
                });

                $scope.updateSeriesSet();
            });

    }
]);
