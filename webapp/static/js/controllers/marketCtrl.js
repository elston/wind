/*global app,$SCRIPT_ROOT,alertify*/

app.controller('MarketsCtrl', ['$scope', '$http', '$log', '$uibModal',
    function ($scope, $http, $log, $uibModal) {
        'use strict';

        $scope.gridOptions = {
            enableSorting: false,
            enableGridMenu: true,
            enableRowSelection: true,
            multiSelect: true,
            gridMenuCustomItems: [
                {
                    title: 'Add market',
                    action: function ($event) {
                        $('#new-market-dialog').modal('show');
                    },
                    order: 210
                },
                {
                    title: 'Delete selected markets',
                    action: function ($event) {
                        var rows = this.grid.rows;
                        rows.forEach(function (row) {
                            if (row.isSelected) {
                                $scope.deleteMarket(row);
                            }
                        });
                    },
                    order: 211
                }
            ],
            columnDefs: [
                {field: 'name'},
                {
                    field: 'action',
                    headerCellTemplate: ' ',
                    cellTemplate: '<button type="button" class="btn btn-default btn-xs" ng-click="$emit(\'uploadPrices\')" ' +
                    'tooltip-append-to-body="true" uib-tooltip="Upload prices">' +
                    '<span class="glyphicon glyphicon-upload" aria-hidden="true"></span></button>' +
                    '<button type="button" class="btn btn-default btn-xs" ' +
                    'tooltip-append-to-body="true" uib-tooltip="View data">' +
                    '<span class="glyphicon glyphicon-list-alt" aria-hidden="true"></span></button>',
                    width: 200
                }
            ]
        };

        $scope.$on('uploadPrices', function ($event) {
            var modalInstance = $uibModal.open({
                animation: false,
                templateUrl: 'static/partials/upload-prices-modal.html',
                controller: 'UploadPricesCtrl',
                size: 'lg',
                resolve: {
                    entity: function () {
                        return $event.targetScope.row.entity;
                    }
                }
            });

        });

        $scope.deleteMarket = function (row) {
            $http.delete($SCRIPT_ROOT + '/markets/' + row.entity.id)
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
            $http.get($SCRIPT_ROOT + '/markets')
                .then(function (data) {
                        if ('error' in data.data) {
                            alertify.error(data.data.error);
                        } else {
                            $scope.gridOptions.data = data.data.data;
                            $scope.noMarkets = data.data.data.length === 0;
                        }
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        $scope.update();

        $scope.$on('updateMarkets', $scope.update);
    }]);
