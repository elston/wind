/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('WindParkDataCtrl', ['$scope', '$rootScope', '$uibModal', 'locationService',
    'marketService', 'windparkService',
    function ($scope, $rootScope, $uibModal, locationService, marketService, windparkService) {
        'use strict';

        var windpark = $scope.tab.data;

        $scope.name = windpark.name;
        $scope.dataSource = windpark.data_source;
        $scope.locations = locationService.getLocations();
        $scope.markets = marketService.getMarkets();
        $scope.location = windpark.location;
        $scope.market = windpark.market;

        windparkService.getSummary(windpark.id)
            .then(function (result) {
                    $scope.summary = result;
                },
                function (error) {
                    alertify.error(error);
                });

        $scope.actualListOptions = {
            enableGridMenu: true,
            enableRowSelection: true,
            enableFullRowSelection: true,
            multiSelect: true,
            gridMenuCustomItems: [
                {
                    title: 'Add turbine',
                    action: function ($event) {
                        var modalInstance = $uibModal.open({
                            animation: false,
                            templateUrl: 'add-turbine.html',
                            controller: 'AddTurbineCtrl',
                            size: 'lg',
                            resolve: {
                                windpark: function () {
                                    return windpark;
                                }
                            }
                        });
                    },
                    order: 210
                },
                {
                    title: 'Delete selected turbines',
                    action: function ($event) {
                        var rows = this.grid.rows;
                        rows.forEach(function (row) {
                            if (row.isSelected) {
                                windparkService.deleteTurbine(windpark.id, row.entity.relationship_id)
                                    .then(function (windparkList) {
                                            $rootScope.$broadcast('reloadWindParks');
                                            $scope.actualListOptions.data = windparkList.find(function (el) {
                                                return el.id === windpark.id;
                                            }).turbines;
                                            reloadTotalPowerCurve();
                                        },
                                        function (error) {
                                            alertify.error(error);
                                        });
                            }
                        });
                    },
                    order: 211
                }
            ],
            columnDefs: [
                {field: 'name'},
                {field: 'count'},
                {field: 'rated_power', 'name': 'Rated power, MW'}
//                {
//                    field: 'action',
//                    headerCellTemplate: '<div>&nbsp;</div>',
//                    enableHiding: false,
//                    cellTemplate: '<button type="button" class="btn btn-default btn-xs" ng-click="$emit(\'viewTurbineData\')" ' +
//                'tooltip-append-to-body="true" uib-tooltip="View data">' +
//                '<span class="glyphicon glyphicon-list-alt" aria-hidden="true"></span></button>',
//                    width: 200
//                }
            ]
        };

        $scope.actualListOptions.data = windpark.turbines;

        var reloadTotalPowerCurve = function () {
            windparkService.getTotalPowerCurve(windpark.id)
                .then(function (curve) {
                    $scope.chart = new Highcharts.Chart({
                        chart: {
                            renderTo: 'total-power-curve-container',
                            animation: false
                        },
                        title: {
                            text: 'Total power curve'
                        },
                        credits: {
                            enabled: false
                        },
                        legend: {
                            enabled: false
                        },
                        yAxis: [{
                            title: {
                                text: 'Power, MW'
                            }
                        }],
                        xAxis: [{
                            title: {
                                text: 'Wind speed, m/s'
                            }
                        }],
                        series: [{
                            name: 'Power curve',
                            data: curve,
                            animation: false
                        }]
                    });
                },
                function (error) {
                    alertify.error(error);
                });
        };

        reloadTotalPowerCurve();

        $scope.$on('reloadTurbinesList', function () {
            $scope.actualListOptions.data = windparkService.getWindparks().find(function (el) {
                return el.id === windpark.id;
            }).turbines;
            reloadTotalPowerCurve();
        });

        $scope.update = function () {
            windparkService.updateWindpark({
                    id: windpark.id,
                    name: $scope.name,
                    location_id: $scope.location.id,
                    market_id: $scope.market.id,
                    data_source: $scope.dataSource
                })
                .then(function (data) {
                        alertify.success('OK');
                        $rootScope.$broadcast('reloadWindParks');
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        $scope.plotGeneration = function () {
            windparkService.getGeneration(windpark.id)
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
            windparkService.getWindVsPower(windpark.id)
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
