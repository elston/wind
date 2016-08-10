/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('WindParkDataCtrl', ['$scope', '$rootScope', 'locationService',
    'marketService', 'windparkService',
    function ($scope, $rootScope, locationService, marketService, windparkService) {
        'use strict';

        $scope.name = $scope.tab.data.name;
        $scope.locations = locationService.getLocations();
        $scope.markets = marketService.getMarkets();
        $scope.location = $scope.tab.data.location;
        $scope.market = $scope.tab.data.market;
        $scope.dataSource = 'historical';

        windparkService.getSummary($scope.tab.id)
            .then(function (result) {
                    $scope.summary = result;
                },
                function (error) {
                    alertify.error(error);
                });

        $scope.actualListOptions = {
            enableGridMenu: true,
            enableRowSelection: true,
            multiSelect: true,
            gridMenuCustomItems: [
                {
                    title: 'Add turbine',
                    action: function ($event) {
                        var modalInstance = $uibModal.open({
                            animation: false,
                            templateUrl: 'add-turbine.html',
                            controller: 'AddTurbineCtrl',
                            size: 'lg'
                        });                    },
                    order: 210
                },
                {
                    title: 'Delete selected turbines',
                    action: function ($event) {
                        var rows = this.grid.rows;
                        rows.forEach(function (row) {
                            if (row.isSelected) {
                                windparkService.deleteTurbine(row.entity.id)
                                    .then(function () {
                                            $scope.update();
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
                {field: 'rated_power', 'name': 'Rated power, MW'},
                {
                    field: 'action',
                    headerCellTemplate: '<div>&nbsp;</div>',
                    enableHiding: false,
                    cellTemplate: '<button type="button" class="btn btn-default btn-xs" ng-click="$emit(\'viewTurbineData\')" ' +
                'tooltip-append-to-body="true" uib-tooltip="View data">' +
                '<span class="glyphicon glyphicon-list-alt" aria-hidden="true"></span></button>',
                    width: 200
                }
            ]
        };

        $scope.update = function () {
            windparkService.updateWindpark({
                    id: $scope.tab.id,
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
            windparkService.getGeneration($scope.tab.id)
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
            windparkService.getWindVsPower($scope.tab.id)
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
