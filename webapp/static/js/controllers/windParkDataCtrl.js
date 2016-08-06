/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('WindParkDataCtrl', ['$scope', '$rootScope', '$uibModalInstance', 'entity', 'locationService',
    'marketService', 'windparkService',
    function ($scope, $rootScope, $uibModalInstance, entity, locationService, marketService, windparkService) {
        'use strict';

        $scope.name = entity.name;
        $scope.locations = locationService.getLocations();
        $scope.markets = marketService.getMarkets();
        $scope.location = entity.location;
        $scope.market = entity.market;
        $scope.dataSource = 'historical';

        $scope.close = function () {
            $uibModalInstance.close();
        };

        windparkService.getSummary(entity.id)
                .then(function (result) {
                        $scope.summary = result;
                    },
                    function (error) {
                        alertify.error(error);
                    });

        $scope.update = function () {
            windparkService.updateWindpark({
                    id: entity.id,
                    name: $scope.name,
                    location_id: $scope.location.id,
                    market_id: $scope.market.id,
                    data_source: $scope.dataSource
                })
                .then(function (data) {
                        alertify.success('OK');
                        $rootScope.$broadcast('updateWindParks');
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        $scope.plotGeneration = function () {
            windparkService.getGeneration(entity.id)
                .then(function (result) {
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
                                data: result.power,
                                animation: false,
                                tooltip: {
                                    valueDecimals: 3
                                }
                            },
                                {
                                    name: 'Wind speed, km/h',
                                    data: result.wind,
                                    animation: false,
                                    yAxis: 1,
                                    tooltip: {
                                        valueDecimals: 1
                                    }
                                }]
                        });
                    },
                    function (error) {
                        alertify.error(error.statusText);
                    });
        };

        $scope.cleanGenerationPlot = function () {
            $('#plot-generation').empty();
        };

        $scope.plotWindVsPower = function () {
            windparkService.getWindVsPower(entity.id)
                .then(function (result) {
                        $scope.beta = result.beta;
                        $scope.sd_beta = result.sd_beta;
                        $scope.chart = new Highcharts.Chart({
                            chart: {
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
                                type: 'scatter',
                                name: 'Wind vs Power',
                                data: result.scatterplot,
                                animation: false,
                                tooltip: {
                                    valueDecimals: 3
                                },
                                color: 'rgba(119, 152, 191, .5)'
                            },
                                {
                                    type: 'line',
                                    name: 'Wind vs Power model',
                                    data: result.model,
                                    animation: false,
                                    tooltip: {
                                        valueDecimals: 3
                                    }
                                }]
                        });
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        $scope.cleanWindVsPowerPlot = function () {
            $('#plot-wind-vs-power').empty();
        };


    }]);
