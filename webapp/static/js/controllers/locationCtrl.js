app.controller('LocationsCtrl', ['$scope', '$http', '$log', '$uibModal', function ($scope, $http, $log, $uibModal) {

    $scope.gridOptions = {
        enableSorting: false,
        enableGridMenu: true,
        enableRowSelection: true,
        multiSelect: true,
        gridMenuCustomItems: [
            {
                title: 'Add location',
                action: function ($event) {
                    $('#new-location-dialog').modal('show');
                },
                order: 210
            },
            {
                title: 'Delete selected locations',
                action: function ($event) {
                    var rows = this.grid.rows;
                    rows.forEach(function (row) {
                        if (row.isSelected) {
                            $scope.deleteLocation(row);
                        }
                    });
                },
                order: 211
            }
        ],
        columnDefs: [
            {field: 'name'},
            {field: 'country_iso3166', visible: false},
            {name: 'Country', field: 'country_name'},
            {field: 'city'},
            {field: 'tz_short', visible: false},
            {field: 'tz_long', visible: false},
            {field: 'lat', cellFilter: 'number: 5'},
            {field: 'lon', cellFilter: 'number: 5'},
            {field: 'wspd_shape', cellFilter: 'number: 2'},
            {field: 'wspd_scale', cellFilter: 'number: 2'},
            {field: 'lookback', visible: false},
//            {field: 'lookforward', visible: false},
            {
                field: 'action',
                headerCellTemplate: ' ',
                cellTemplate: '<button type="button" class="btn btn-default btn-xs" ng-click="$emit(\'updateWeather\')" ' +
                'tooltip-append-to-body="true" uib-tooltip="Reload">' +
                '<span class="glyphicon glyphicon-refresh" aria-hidden="true"></span></button>' +
                '<button type="button" class="btn btn-default btn-xs" ng-click="$emit(\'viewWeather\')" ' +
                'tooltip-append-to-body="true" uib-tooltip="View chart">' +
                '<span class="glyphicon glyphicon-search" aria-hidden="true"></span></button>' +
                '<button type="button" class="btn btn-default btn-xs" ng-click="$emit(\'viewDistribution\')" ' +
                'tooltip-append-to-body="true" uib-tooltip="Fit and view wind speed distribution">' +
                '<span class="glyphicon glyphicon-stats" aria-hidden="true"></span></button>',
                width: 200
            }
        ]
    };

    $scope.$on('updateWeather', function ($event) {
        var locationId = $event.targetScope.row.entity.id;
        var locationName = $event.targetScope.row.entity.name;
        $http.post($SCRIPT_ROOT + '/locations/' + locationId + '/update_history')
            .then(function (data) {
                    if ('error' in data.data) {
                        alertify.error('Error while updating history for location "' + locationName + '": ' + data.data.error);
                    } else {
                        alertify.success('History for location "' + locationName + '" updated');
                    }
                },
                function (error) {
                    alertify.error('Error while updating history for location "' + locationName + '": ' + error);
                });
        $http.post($SCRIPT_ROOT + '/locations/' + locationId + '/update_forecast')
            .then(function (data) {
                    if ('error' in data.data) {
                        alertify.error('Error while updating forecast for location "' + locationName + '": ' + data.data.error);
                    } else {
                        alertify.success('Forecast for location "' + locationName + '" updated');
                    }
                },
                function (error) {
                    alertify.error('Error while updating forecast for location "' + locationName + '": ' + error);
                });
    });

    $scope.$on('viewWeather', function ($event) {
        var locationId = $event.targetScope.row.entity.id;
        var locationName = $event.targetScope.row.entity.name;

        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'weather-plot-modal.html',
            controller: 'WeatherPlotCtrl',
            size: 'lg',
            resolve: {
                entity: function () {
                    return $event.targetScope.row.entity;
                }
            }
        });

    });

    $scope.$on('viewDistribution', function ($event) {
        var locationId = $event.targetScope.row.entity.id;
        var locationName = $event.targetScope.row.entity.name;

        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'wspd-distribution-modal.html',
            controller: 'WspdDistributionCtrl',
            size: 'lg',
            resolve: {
                entity: function () {
                    return $event.targetScope.row.entity;
                }
            }
        });

    });

    $scope.deleteLocation = function (row) {
        $http.delete($SCRIPT_ROOT + '/locations/' + row.entity.id)
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
        $http.get($SCRIPT_ROOT + '/locations')
            .then(function (data) {
                    if ('error' in data.data) {
                        alertify.error(data.data.error);
                    } else {
                        $scope.gridOptions.data = data.data.data;
                        $scope.noLocations = data.data.data.length === 0;
                    }
                },
                function (error) {
                    alertify.error(error);
                });
    };

    $scope.update();

    $scope.$on('updateLocations', $scope.update);
}]);
