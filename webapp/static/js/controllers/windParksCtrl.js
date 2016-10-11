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
                    order: 210,
                    icon: 'grid-icon-add'
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
                    order: 211,
                    icon: 'grid-icon-remove'
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
                    cellTemplate: '<button type="button" class="btn btn-info btn-xs" ng-click="$emit(\'uploadGeneration\')" ' +
                    'tooltip-append-to-body="true" uib-tooltip="Upload generation data">' +
                    '<span class="glyphicon glyphicon-upload" aria-hidden="true"></span></button>' +
                    '<button type="button" class="btn btn-primary btn-xs" ng-click="$emit(\'openInTab\')">Open</button>',
                    width: 200
                }
            ]
        };

        $scope.autoGridSize = function () {
            if ($scope.gridOptions && $scope.gridOptions.data.length > 0) {
                var rowHeight = $scope.gridOptions.rowHeight;
                var headerHeight = $scope.gridOptions.headerRowHeight;
                var marginHeight = 20;

                var newHeight = $scope.gridOptions.data.length * rowHeight + headerHeight + marginHeight;

                angular.element(document.getElementsByClassName('grid-windparks')[0]).css('height', newHeight + 'px');
            }

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

        $scope.$on('openInTab', function ($event) {
            var windparkData = $event.targetScope.row.entity;
            var tabData = {
                id: windparkData.id,
                title: windparkData.name + ' windpark',
                type: 'windpark',
                data: windparkData
            };
            $scope.$emit('addTab', tabData);
        });

        $scope.deleteWindPark = function (row) {
            windparkService.deleteWindpark(row.entity.id)
                .then(function () {
                        $scope.reload();
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        $scope.reload = function () {
            var windparks = windparkService.getWindparks();
            $scope.gridOptions.data = windparks;
            $scope.noWindParks = windparks.length === 0;
            $scope.autoGridSize();
        };

        windparkService.reload().then(function () {
                $scope.reload();
            },
            function (error) {
                alertify.error(error);
            });


        $scope.reload();

        $scope.$on('reloadWindParks', $scope.reload);

    }]);
