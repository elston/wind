/*global app,$SCRIPT_ROOT,alertify*/

app.controller('WindParksCtrl', ['$scope', '$http', '$uibModal',
    function ($scope, $http, $uibModal) {
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
                {field: 'location'},
                {field: 'market'},
                {
                    field: 'action',
                    headerCellTemplate: ' ',
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
            $http.delete($SCRIPT_ROOT + '/windparks/' + row.entity.id)
                .then(function (data) {
                        if ('error' in data.data) {
                            alertify.error(data.data.error);
                        } else {
                            $scope.update();
                        }
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        $scope.update = function () {
            $http.get($SCRIPT_ROOT + '/windparks')
                .then(function (data) {
                        if ('error' in data.data) {
                            alertify.error(data.data.error);
                        } else {
                            $scope.gridOptions.data = data.data.data;
                            $scope.noWindParks = data.data.data.length === 0;
                        }
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        $scope.update();

        $scope.$on('updateWindParks', $scope.update);

    }]);
