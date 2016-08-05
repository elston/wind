/*global app,$SCRIPT_ROOT,alertify*/

app.controller('WindParkDataCtrl', ['$scope', '$http', '$uibModalInstance', 'entity',
    function ($scope, $http, $uibModalInstance, entity) {
        'use strict';

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $scope.windParkName = entity.name;

        $scope.update = function () {
            $http.get($SCRIPT_ROOT + '/windparks/summary/' + entity.id)
                .then(function (response) {
                        if ('error' in response.data) {
                            alertify.error(response.data.error);
                        } else {
                            $scope.summary = response.data.data;
                        }
                    },
                    function (error) {
                        alertify.error(error.statusText);
                    });
        };

        $scope.update();

        $scope.plotGeneration = function (value) {
            $http.get($SCRIPT_ROOT + '/windparks/generation/' + entity.id)
                .then(function (response) {
                        if ('error' in response.data) {
                            alertify.error(response.data.error);
                        } else {
                            $scope.chart = new Highcharts.StockChart({
                                chart: {
                                    renderTo: 'plot-generation',
                                    animation: false
                                },
                                title: {
                                    text: 'Generation'
                                },
                                credits: {
                                    enabled: false
                                },
                                yAxis: [{
                                    title: {
                                        text: 'Power, MW'
                                    }
                                },
                                {
                                    title: {
                                        text: 'Wind speed, km/h'
                                    }
                                }],
                                series: [{
                                    name: 'Generation, MW',
                                    data: response.data.data.power,
                                    animation: false,
                                    tooltip: {
                                        valueDecimals: 3
                                    }
                                },
                                {
                                    name: 'Wind speed, km/h',
                                    data: response.data.data.wind,
                                    animation: false,
                                    yAxis: 1,
                                    tooltip: {
                                        valueDecimals: 1
                                    }
                                }]
                            });
                        }
                    },
                    function (error) {
                        alertify.error(error.statusText);
                    });
        };

        $scope.cleanGenerationPlot = function () {
            $('#plot-generation').empty();
        };

        $scope.plotWindVsPower = function (value) {
            $http.get($SCRIPT_ROOT + '/windparks/windvspower/' + entity.id)
                .then(function (response) {
                        if ('error' in response.data) {
                            alertify.error(response.data.error);
                        } else {
                            $scope.chart = new Highcharts.Chart({
                                chart: {
                                    type: 'scatter',
                                    zoomType: 'xy',
                                    renderTo: 'plot-wind-vs-power',
                                    animation: false
                                },
                                title: {
                                    text: 'Wind vs Power'
                                },
                                credits: {
                                    enabled: false
                                },
                                yAxis: [{
                                    title: {
                                        text: 'Power, MW'
                                    }
                                }],
                                xAxis: [{
                                    title: {
                                        text: 'Wind speed, km/h'
                                    }
                                }],
                                series: [{
                                    name: 'Wind vs Power',
                                    data: response.data.data,
                                    animation: false,
                                    tooltip: {
                                        valueDecimals: 3
                                    },
                                    color: 'rgba(119, 152, 191, .5)'
                                }]
                            });
                        }
                    },
                    function (error) {
                        alertify.error(error.statusText);
                    });
        };

        $scope.cleanWindVsPowerPlot = function () {
            $('#plot-wind-vs-power').empty();
        };


    }]);
