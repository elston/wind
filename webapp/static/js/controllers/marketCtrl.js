/*global app,$SCRIPT_ROOT,alertify*/

app.controller('MarketsCtrl', ['$scope', '$uibModal', 'marketService',
    function ($scope, $uibModal, marketService) {
        'use strict';

        $scope.gridOptions = {
            enableGridMenu: true,
            enableRowSelection: true,
            multiSelect: true,
            gridMenuCustomItems: [
                {
                    title: 'Add market',
                    action: function ($event) {
                        $('#new-market-dialog').modal('show');
                    },
                    order: 210,
                    icon: 'grid-icon-add'
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
                    order: 211,
                    icon: 'grid-icon-remove'
                }
            ],
            columnDefs: [
                {field: 'name'},
                {
                    field: 'action',
                    headerCellTemplate: ' ',
                    enableHiding: false,
                    cellTemplate: '<button type="button" class="btn btn-warning btn-xs" ng-disabled="row.entity.busy || row.entity.interlocked" '+
                    'ng-click="$emit(\'uploadPrices\')" ' +
                    'tooltip-append-to-body="true" uib-tooltip="Upload prices">' +
                    '<span class="glyphicon glyphicon-upload" aria-hidden="true"></span></button>' +
                    '<button type="button" class="btn btn-info btn-xs" ng-click="$emit(\'viewData\')" ' +
                    'tooltip-append-to-body="true" uib-tooltip="View data">' +
                    '<span class="glyphicon glyphicon-list-alt" aria-hidden="true"></span></button>' +
                    '<button type="button" class="btn btn-secondary btn-xs" ng-click="$emit(\'downloadData\')" ' +
                    'tooltip-append-to-body="true" uib-tooltip="Download data">' +
                    '<span class="glyphicon glyphicon-download-alt" aria-hidden="true"></span></button>' +
                    '<span ng-show="row.entity.busy" class="glyphicon glyphicon-refresh spinning"></span>' +
                    '<span ng-show="row.entity.interlocked && !row.entity.busy" class="glyphicon glyphicon-lock"></span>',
                    width: 200
                }
            ]
        };

        $scope.$on('status:update', function (event, data) {
            $scope.gridOptions.data.forEach(function (market) {
                var busy = false;
                data.rqjobs.forEach(function (rqjob) {
                    if (+rqjob.market === market.id &&
                        rqjob.job === 'fit_price' && !((rqjob.status === 'finished') || (rqjob.status === 'failed'))) {
                        busy = true;
                    }
                });
                market.busy = busy;
                market.interlocked = data.interlocks.markets.indexOf(market.id) !== -1;
            });
        });

        $scope.autoGridSize = function () {
            if ($scope.gridOptions && $scope.gridOptions.data.length > 0) {
                var rowHeight = $scope.gridOptions.rowHeight;
                var headerHeight = $scope.gridOptions.headerRowHeight;
                var marginHeight = 20;

                var newHeight = $scope.gridOptions.data.length * rowHeight + headerHeight + marginHeight;

                angular.element(document.getElementsByClassName('grid-market')[0]).css('height', newHeight + 'px');
            }

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

        $scope.$on('downloadData', function ($event) {
            var marketId = $event.targetScope.row.entity.id;
            location.href = $SCRIPT_ROOT + '/markets/' + marketId;
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
            $scope.autoGridSize();
        };

        marketService.reload().then(function () {
                $scope.update();
            },
            function (error) {
                alertify.error(error);
            });

        $scope.$on('updateMarkets', $scope.update);
    }]);
