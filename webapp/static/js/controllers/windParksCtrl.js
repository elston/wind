/*global app,$SCRIPT_ROOT,alertify*/

app.controller('WindParksCtrl', ['$scope', '$uibModal', 'windparkService',
    function ($scope, $uibModal, windparkService) {
        'use strict';

        $scope.gridOptions = {
            enableSorting: false,
            enableGridMenu: true,
            enableRowSelection: true,
            multiSelect: true,
            gridMenuCustomItems: [
                {
                    title: 'Add wind park',
                    action: function ($event) {
                        var modalInstance = $uibModal.open({
                            animation: false,
                            templateUrl: 'new-windpark.html',
                            controller: 'NewWindParkCtrl',
                            size: 'lg'
                        });
                    },
                    order: 210
                },
                {
                    title: 'Delete selected wind parks',
                    action: function ($event) {
                        var rows = this.grid.rows;
                        rows.forEach(function (row) {
                            if (row.isSelected) {
                                $scope.deleteWindPark(row);
                            }
                        });
                    },
                    order: 211
                }
            ],
            columnDefs: [
                {field: 'name'},
                {field: 'location.name', name: 'Location'},
                {field: 'market.name', name: 'Market'},
                {
                    field: 'action',
                    headerCellTemplate: ' ',
                    enableHiding: false,
                    cellTemplate: '<button type="button" class="btn btn-default btn-xs" ng-click="$emit(\'uploadGeneration\')" ' +
                    'tooltip-append-to-body="true" uib-tooltip="Upload generation data">' +
                    '<span class="glyphicon glyphicon-upload" aria-hidden="true"></span></button>' +
                    '<button type="button" class="btn btn-default btn-xs" ng-click="$emit(\'viewData\')" ' +
                    'tooltip-append-to-body="true" uib-tooltip="View data">' +
                    '<span class="glyphicon glyphicon-list-alt" aria-hidden="true"></span></button>',
                    width: 200
                }
            ]
        };

        $scope.$on('uploadGeneration', function ($event) {
            var modalInstance = $uibModal.open({
                animation: false,
                templateUrl: 'upload-generation-modal.html',
                controller: 'UploadGenerationCtrl',
                size: 'lg',
                resolve: {
                    entity: function () {
                        return $event.targetScope.row.entity;
                    }
                }
            });

        });

        $scope.$on('viewData', function ($event) {
            var modalInstance = $uibModal.open({
                animation: false,
                templateUrl: 'windpark-data-modal.html',
                controller: 'WindParkDataCtrl',
                size: 'lg',
                resolve: {
                    entity: function () {
                        return $event.targetScope.row.entity;
                    }
                }
            });

        });

        $scope.deleteWindPark = function (row) {
            windparkService.deleteWindpark(row.entity.id)
                .then(function () {
                        $scope.update();
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        $scope.update = function () {
            var windparks = windparkService.getWindparks();
            $scope.gridOptions.data = windparks;
            $scope.noWindParks = windparks.length === 0;
        };

        windparkService.reload().then(function () {
                $scope.update();
            },
            function (error) {
                alertify.error(error);
            });


        $scope.update();

        $scope.$on('updateWindParks', $scope.update);

    }]);
