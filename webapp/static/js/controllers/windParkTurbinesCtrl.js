/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('WindparkTurbinesCtrl', ['$scope', '$rootScope', '$timeout', '$uibModal', 'windparkService',
    function ($scope, $rootScope, $timeout, $uibModal, windparkService) {
        'use strict';

        $scope.actualListOptions = {
            enableGridMenu: true,
            enableRowSelection: true,
            enableFullRowSelection: true,
            multiSelect: true,
            minRowsToShow: 5,
            gridMenuShowHideColumns: false,
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
                                    return $scope.windpark;
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
                                windparkService.deleteTurbine($scope.windpark.id, row.entity.relationship_id)
                                    .then(function (windparkList) {
                                            $rootScope.$broadcast('reloadWindParks');
                                            $scope.actualListOptions.data = windparkList.find(function (el) {
                                                return el.id === $scope.windpark.id;
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

        $scope.actualListOptions.data = $scope.windpark.turbines;

        var reloadTotalPowerCurve = function () {
            windparkService.getTotalPowerCurve($scope.windpark.id)
                .then(function (curve) {
                        $timeout(function () {
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
                                    tooltip: {
                                        valueDecimals: 3
                                    },
                                    animation: false
                                }]
                            });
                        });
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        reloadTotalPowerCurve();

        $scope.$on('reloadTurbinesList', function () {
            $scope.actualListOptions.data = windparkService.getWindparks().find(function (el) {
                return el.id === $scope.windpark.id;
            }).turbines;
            reloadTotalPowerCurve();
        });

    }]);
