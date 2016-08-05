/*global app,$SCRIPT_ROOT,alertify*/

app.controller('MarketsCtrl', ['$scope', '$uibModal', 'marketService',
    function ($scope, $uibModal, marketService) {
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
                    enableHiding: false,
                    cellTemplate: '<button type="button" class="btn btn-default btn-xs" ng-click="$emit(\'uploadPrices\')" ' +
                    'tooltip-append-to-body="true" uib-tooltip="Upload prices">' +
                    '<span class="glyphicon glyphicon-upload" aria-hidden="true"></span></button>' +
                    '<button type="button" class="btn btn-default btn-xs" ng-click="$emit(\'viewData\')" ' +
                    'tooltip-append-to-body="true" uib-tooltip="View data">' +
                    '<span class="glyphicon glyphicon-list-alt" aria-hidden="true"></span></button>',
                    width: 200
                }
            ]
        };

        $scope.$on('uploadPrices', function ($event) {
            var modalInstance = $uibModal.open({
                animation: false,
                templateUrl: 'upload-prices-modal.html',
                controller: 'UploadPricesCtrl',
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
                templateUrl: 'market-data-modal.html',
                controller: 'MarketDataCtrl',
                size: 'lg',
                resolve: {
                    entity: function () {
                        return $event.targetScope.row.entity;
                    }
                }
            });

        });

        $scope.deleteMarket = function (row) {
            marketService.deleteMarket(row.entity.id)
                .then(function (data) {
                        $scope.update();
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        $scope.update = function () {
            var markets = marketService.getMarkets();
            $scope.gridOptions.data = markets;
            $scope.noMarkets = markets.length === 0;
        };

        marketService.reload().then(function () {
                $scope.update();
            },
            function (error) {
                alertify.error(error);
            });

        $scope.$on('updateMarkets', $scope.update);
    }]);
