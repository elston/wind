/*global app,$SCRIPT_ROOT,alertify,Highcharts,google*/

app.controller('AddTurbineCtrl', ['$scope', '$rootScope', '$uibModalInstance', 'turbineService', 'windparkService',
    'windpark',
    function ($scope, $rootScope, $uibModalInstance, turbineService, windparkService, windpark) {
        'use strict';

        $scope.count = 1;
        $scope.selectedTurbine = null;

        $scope.allTurbinesListOptions = {
            enableSorting: true,
            enableFiltering: true,
            enableRowSelection: true,
            enableFullRowSelection: true,
            multiSelect: false,
            columnDefs: [
                {field: 'name'},
                {field: 'vertical_axis'},
                {field: 'v_cutin'},
                {field: 'v_cutoff'},
                {field: 'rated_power', name: 'Rated power, MW'}
            ]
        };

        turbineService.reload()
            .then(function (data) {
                    $scope.allTurbinesListOptions.data = data;
                },
                function (error) {
                    alertify.error(error);
                });

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $scope.allTurbinesListOptions.onRegisterApi = function (gridApi) {
            //set gridApi on scope
            $scope.gridApi = gridApi;
            gridApi.selection.on.rowSelectionChanged($scope, function (row) {
                if (row.isSelected) {
                    $scope.selectedTurbine = row.entity;
                    turbineService.getPowerCurve(row.entity.id)
                        .then(function (data) {
                                $scope.drawPowerCurve(data);
                            },
                            function (error) {
                                alertify.error(error);
                            });
                } else {
                    $scope.selectedTurbine = null;
                }
            });

        };

        $scope.drawPowerCurve = function (data) {
            $scope.chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'selected-power-curve-container',
                    animation: false
                },
                title: {
                    text: 'Power curve'
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
                    data: data,
                    animation: false
                }]
            });
        };

        $scope.addTurbine = function () {
            $uibModalInstance.close();
            windparkService.addTurbine(windpark.id, $scope.selectedTurbine.id, $scope.count)
                .then(function () {
                        $rootScope.$broadcast('reloadWindParks');
                        $rootScope.$broadcast('reloadTurbinesList');
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

    }]);
