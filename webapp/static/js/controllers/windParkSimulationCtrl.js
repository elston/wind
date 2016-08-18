/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('WindParkSimulationCtrl', ['$scope', '$timeout', 'windparkService',
    function ($scope, $timeout, windparkService) {
        'use strict';

        $scope.status = {isDetailsOpen: false};
        $scope.timeSpan = 24;
        $scope.nSamples = 100;

        $scope.showDetails = function () {
        };

        $scope.updateWindSimulation = function () {
            windparkService.getSimulation($scope.windpark.id, $scope.timeSpan, $scope.nSamples)
                .then(function (data) {
                    var wind_series = [];
                    data.wind_speed.forEach(function (sample) {
                        wind_series.push({
                            data: sample
                        });
                    });
                    var power_series = [];
                    data.power.forEach(function (sample) {
                        power_series.push({
                            data: sample
                        });
                    });
                    $timeout(function () {
                        $scope.chart1 = new Highcharts.Chart({
                            chart: {
                                renderTo: 'wind-sim',
                                animation: false
                            },
                            title: {
                                text: 'Wind simulation'
                            },
                            credits: {
                                enabled: false
                            },
                            legend: {
                                enabled: false
                            },
                            plotOptions: {
                                line: {
                                    animation: false,
                                    marker: {
                                        enabled: false
                                    },
                                    color: 'rgba(119, 152, 191, .5)'
                                }
                            },
                            yAxis: [{
                                title: {
                                    text: 'Wind speed, m/s'
                                }
                            }],
                            series: wind_series
                        });
                        $scope.chart2 = new Highcharts.Chart({
                            chart: {
                                renderTo: 'power-sim',
                                animation: false
                            },
                            title: {
                                text: 'Power simulation'
                            },
                            credits: {
                                enabled: false
                            },
                            legend: {
                                enabled: false
                            },
                            plotOptions: {
                                line: {
                                    animation: false,
                                    marker: {
                                        enabled: false
                                    },
                                    color: 'rgba(119, 152, 191, .5)'
                                }
                            },
                            yAxis: [{
                                title: {
                                    text: 'Power, MW'
                                }
                            }],
                            series: power_series
                        })
                    });

                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

    }]);
