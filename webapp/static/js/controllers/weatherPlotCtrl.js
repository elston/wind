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

        $scope.formatLastObservation = function (date) {
            var fetchedDate = new Date(date[0]);
            var year = fetchedDate.getUTCFullYear();
            var month = fetchedDate.getUTCMonth() + 1;
            var day = fetchedDate.getUTCDate();
            var hours = fetchedDate.getUTCHours();
            var minutes = fetchedDate.getUTCMinutes();
            var ampm = hours >= 12 ? 'pm' : 'am';
            hours = hours % 12;
            hours = hours ? hours : 12;
            minutes = minutes < 10 ? '0'+minutes : minutes;
            var strDate = 'Observation updated on: '+day+'-'+month+'-'+year+' '+hours + ':' + minutes + ampm +
                ' ('+ $scope.history_data.tzinfo +')';
            return strDate;
        };

        $scope.updateSeriesSet = function () {
            for (var i = 0; i < $scope.chart.series.length - 1; i += 3) {
                if ($scope.tempmEnabled) {
                    $scope.chart.series[i + 0].show();

                    $scope.chart.series[i + 0].options.showInLegend = true;
                    $scope.chart.legend.renderItem($scope.chart.series[i + 0]);
                    $scope.chart.legend.render();
                } else {
                    $scope.chart.series[i + 0].hide();

                    $scope.chart.series[i + 0].options.showInLegend = false;
                    $scope.chart.series[i + 0].legendItem = null;
                    $scope.chart.legend.destroyItem($scope.chart.series[i + 0]);
                    $scope.chart.legend.render();
                }
                if ($scope.wspdmEnabled) {
                    $scope.chart.series[i + 1].show();

                    $scope.chart.series[i + 1].options.showInLegend = true;
                    $scope.chart.legend.renderItem($scope.chart.series[i + 1]);
                    $scope.chart.legend.render();
                } else {
                    $scope.chart.series[i + 1].hide();

                    $scope.chart.series[i + 1].options.showInLegend = false;
                    $scope.chart.series[i + 1].legendItem = null;
                    $scope.chart.legend.destroyItem($scope.chart.series[i + 1]);
                    $scope.chart.legend.render();
                }
                if ($scope.wdirdEnabled) {
                    $scope.chart.series[i + 2].show();

                    $scope.chart.series[i + 2].options.showInLegend = true;
                    $scope.chart.legend.renderItem($scope.chart.series[i + 2]);
                    $scope.chart.legend.render();
                } else {
                    $scope.chart.series[i + 2].hide();

                    $scope.chart.series[i + 2].options.showInLegend = false;
                    $scope.chart.series[i + 2].legendItem = null;
                    $scope.chart.legend.destroyItem($scope.chart.series[i + 2]);
                    $scope.chart.legend.render();
                }
            }

            for (var i = 0; i < $scope.chart.yAxis.length - 1; i += 3) {
                if ($scope.tempmEnabled) {
                    if($scope.chart.yAxis[i + 0]){
                        $scope.chart.yAxis[i + 0].update({
                            labels: {
                                enabled: true
                            },
                            title: {
                                text: 'Temperature, C'
                            }
                        });
                    }
                } else {
                    if ($scope.chart.yAxis[i + 0]) {
                        $scope.chart.yAxis[i + 0].update({
                            labels: {
                                enabled: false
                            },
                            title: {
                                text: null
                            }
                        });
                    }
                }
                if ($scope.wspdmEnabled) {
                    if ($scope.chart.yAxis[i + 1]){
                        $scope.chart.yAxis[i + 1].update({
                            labels: {
                                enabled: true
                            },
                            title: {
                                text: 'Wind speed, km/h'
                            }
                        });
                    }
                } else {
                    if ($scope.chart.yAxis[i + 1]) {
                        $scope.chart.yAxis[i + 1].update({
                            labels: {
                                enabled: false
                            },
                            title: {
                                text: null
                            }
                        });
                    }
                }
                if ($scope.wdirdEnabled) {
                    if ($scope.chart.yAxis[i + 2]) {
                        $scope.chart.yAxis[i + 2].update({
                            labels: {
                                enabled: true
                            },
                            title: {
                                text: 'Wind direction, degrees'
                            }
                        });
                    }
                } else {
                    if ($scope.chart.yAxis[i + 2]) {
                        $scope.chart.yAxis[i + 2].update({
                            labels: {
                                enabled: false
                            },
                            title: {
                                text: null
                            }
                        });
                    }
                }
            }

        };

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
                    color: 'purple',
                    lineWidth: 3
                }, {
                    name: 'Wind speed, km/h (observation)',
                    data: $scope.history_data.data.wspdm,
                    tooltip: {
                        valueDecimals: 1
                    },
                    yAxis: 1,
                    color: 'purple',
                    lineWidth: 3
                }, {
                    name: 'Wind direction, degrees (observation)',
                    data: $scope.history_data.data.wdird,
                    tooltip: {
                        valueDecimals: 0
                    },
                    yAxis: 2,
                    color: 'purple',
                    lineWidth: 3
                }];

                if ($scope.forecast_data.last_11am) {
                    series.push({
                        name: 'Temperature, C (forecast values from ' + $scope.forecast_data.last_11am.time + ')',
                        data: $scope.forecast_data.last_11am.tempm,
                        tooltip: {
                            valueDecimals: 1
                        },
                        color: 'darkblue',
                        dashStyle: 'dash'
                    });
                    series.push({
                        name: 'Wind speed, km/h (forecast values from ' + $scope.forecast_data.last_11am.time + ')',
                        data: $scope.forecast_data.last_11am.wspdm,
                        tooltip: {
                            valueDecimals: 1
                        },
                        yAxis: 1,
                        color: 'darkblue',
                        dashStyle: 'dash'
                    });
                    series.push({
                        name: 'Wind direction, degrees (forecast values from ' + $scope.forecast_data.last_11am.time + ')',
                        data: $scope.forecast_data.last_11am.wdird,
                        tooltip: {
                            valueDecimals: 1
                        },
                        yAxis: 2,
                        color: 'darkblue',
                        dashStyle: 'dash'
                    });
                }

                if ($scope.forecast_data.last_11pm) {
                    series.push({
                        name: 'Temperature, C (forecast values from ' + $scope.forecast_data.last_11pm.time + ')',
                        data: $scope.forecast_data.last_11pm.tempm,
                        tooltip: {
                            valueDecimals: 1
                        },
                        color: 'lightblue',
                        dashStyle: 'shortdot'
                    });
                    series.push({
                        name: 'Wind speed, km/h (forecast values from ' + $scope.forecast_data.last_11pm.time + ')',
                        data: $scope.forecast_data.last_11pm.wspdm,
                        tooltip: {
                            valueDecimals: 1
                        },
                        yAxis: 1,
                        color: 'lightblue',
                        dashStyle: 'shortdot'
                    });
                    series.push({
                        name: 'Wind direction, degrees (forecast values from ' + $scope.forecast_data.last_11pm.time + ')',
                        data: $scope.forecast_data.last_11pm.wdird,
                        tooltip: {
                            valueDecimals: 1
                        },
                        yAxis: 2,
                        color: 'lightblue',
                        dashStyle: 'shortdot'
                    });
                }

                if ($scope.forecast_data.last) {
                    series.push({
                        name: 'Temperature, C (latest forecast by ' + $scope.forecast_data.last.time + ')',
                        data: $scope.forecast_data.last.tempm,
                        tooltip: {
                            valueDecimals: 1
                        },
                        color: 'darkgrey',
                        dashStyle: 'longdashdot'
                    });
                    series.push({
                        name: 'Wind speed, km/h (latest forecast by ' + $scope.forecast_data.last.time + ')',
                        data: $scope.forecast_data.last.wspdm,
                        tooltip: {
                            valueDecimals: 1
                        },
                        yAxis: 1,
                        color: 'darkgrey',
                        dashStyle: 'longdashdot'
                    });
                    series.push({
                        name: 'Wind direction, degrees (latest forecast by ' + $scope.forecast_data.last.time + ')',
                        data: $scope.forecast_data.last.wdird,
                        tooltip: {
                            valueDecimals: 1
                        },
                        yAxis: 2,
                        color: 'darkgrey',
                        dashStyle: 'longdashdot'
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
                }, function (chart) {
                    setTimeout(function () {
                        $('input.highcharts-range-selector', $($scope.chart.container).parent())
                            .datepicker();
                    }, 1);
                });

                $.datepicker.setDefaults({
                    dateFormat: 'yy-mm-dd',
                    onSelect: function (dateText) {
                        $(this).trigger('change');
                        $(this).trigger('blur');
                    },
                    onClose: function () {
                        $(this).trigger('change');
                        $(this).trigger('blur');
                    }
                });

                $scope.updateSeriesSet();

                $scope.lastObservation = $scope.formatLastObservation(
                    $scope.history_data.data.wspdm[$scope.history_data.data.wspdm.length-1]);
            });

    }
]);
