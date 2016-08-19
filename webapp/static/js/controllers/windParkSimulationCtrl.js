/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('WindParkSimulationCtrl', ['$scope', '$timeout', 'windparkService',
    function ($scope, $timeout, windparkService) {
        'use strict';

        $scope.status = {isDetailsOpen: false};
        $scope.timeSpan = 24;
        $scope.nSamples = 100;
        $scope.dayStart = 22;

        $scope.showDetails = function () {
        };

        $scope.updateWindSimulation = function () {
            windparkService.getWindSimulation($scope.windpark.id, $scope.timeSpan, $scope.nSamples)
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

        $scope.updateMarketSimulation = function () {
            windparkService.getMarketSimulation($scope.windpark.id, $scope.dayStart, $scope.timeSpan, $scope.nSamples)
                .then(function (data) {
                    var lambdaD_series = [];
                    data.lambdaD.forEach(function (sample) {
                        lambdaD_series.push({
                            data: sample
                        });
                    });
                    var MAvsMD_series = [];
                    data.MAvsMD.forEach(function (sample) {
                        MAvsMD_series.push({
                            data: sample
                        });
                    });
                    var sqrt_r_series = [];
                    data.sqrt_r.forEach(function (sample) {
                        sqrt_r_series.push({
                            data: sample
                        });
                    });
                    $timeout(function () {
                        $scope.chart1 = new Highcharts.Chart({
                            chart: {
                                renderTo: 'lambdad-sim',
                                animation: false
                            },
                            title: {
                                text: 'Day ahead prices'
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
                                    text: 'Price'
                                }
                            }],
                            series: lambdaD_series
                        });

                        $scope.chart2 = new Highcharts.Chart({
                            chart: {
                                renderTo: 'mavsmd-sim',
                                animation: false
                            },
                            title: {
                                text: 'MAvsMD'
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
                                    text: 'Price'
                                }
                            }],
                            series: MAvsMD_series
                        });

                        $scope.chart3 = new Highcharts.Chart({
                            chart: {
                                renderTo: 'sqrtr-sim',
                                animation: false
                            },
                            title: {
                                text: 'sqrt(r)'
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
                                    text: 'Price'
                                }
                            }],
                            series: sqrt_r_series
                        });
                    });

                    },
                    function (error) {
                        alertify.error(error);
                    });
        };
    }]);
