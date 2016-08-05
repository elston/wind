/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('WeatherPlotCtrl', ['$scope', '$q', '$uibModalInstance', 'entity', 'locationService',
    function ($scope, $q, $uibModalInstance, entity, locationService) {
        'use strict';

        var locationId = entity.id;
        $scope.locationName = entity.name;
        $scope.tempmEnabled = true;
        $scope.wspdmEnabled = true;
        $scope.wdirdEnabled = false;

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $scope.updateSeriesSet = function () {
            if ($scope.tempmEnabled) {
                $scope.chart.series[0].show();
            } else {
                $scope.chart.series[0].hide();
            }
            if ($scope.wspdmEnabled) {
                $scope.chart.series[1].show();
            } else {
                $scope.chart.series[1].hide();
            }
            if ($scope.wdirdEnabled) {
                $scope.chart.series[2].show();
            } else {
                $scope.chart.series[2].hide();
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
                $scope.chart = new Highcharts.StockChart({
                    chart: {
                        renderTo: 'weather-chart-container',
                        animation: false
                    },
                    rangeSelector: {
                        selected: 5,
                        buttons: [
                            {
                                type: 'day',
                                count: 1,
                                text: '24h'
                            }, {
                                type: 'day',
                                count: 7,
                                text: '7d'
                            }, {
                                type: 'month',
                                count: 1,
                                text: '1m'
                            }, {
                                type: 'month',
                                count: 3,
                                text: '3m'
                            }, {
                                type: 'month',
                                count: 6,
                                text: '6m'
                            }, {
                                type: 'all',
                                text: 'All'
                            }
                        ]
                    },
                    tooltip: {
                        xDateFormat: '%b %e, %Y, %H:%M'
                    },
                    credits: {
                        enabled: false
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
                    series: [{
                        name: 'Temperature, C',
                        data: $scope.history_data.tempm.concat($scope.forecast_data.tempm),
                        zoneAxis: 'x',
                        zones: [{
                            value: $scope.forecast_data.tempm[0][0]
                        }, {
                            dashStyle: 'dot'
                        }],
                        tooltip: {
                            valueDecimals: 1
                        },
                        color: 'red'
                    }, {
                        name: 'Wind speed, km/h',
                        data: $scope.history_data.wspdm.concat($scope.forecast_data.wspdm),
                        zoneAxis: 'x',
                        zones: [{
                            value: $scope.forecast_data.wspdm[0][0]
                        }, {
                            dashStyle: 'dot'
                        }],
                        tooltip: {
                            valueDecimals: 1
                        },
                        yAxis: 1,
                        color: 'blue'
                    }, {
                        name: 'Wind direction, degrees',
                        data: $scope.history_data.wdird.concat($scope.forecast_data.wdird),
                        zoneAxis: 'x',
                        zones: [{
                            value: $scope.forecast_data.wdird[0][0]
                        }, {
                            dashStyle: 'dot'
                        }],
                        tooltip: {
                            valueDecimals: 0
                        },
                        yAxis: 2,
                        color: 'darkgrey'
                    }]
                });

                $scope.updateSeriesSet();
            });

    }
]);
