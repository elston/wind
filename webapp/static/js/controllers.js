var app = angular.module('app', ['ui.grid', 'ui.grid.selection', 'ui.bootstrap']);

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
            {field: 'lat'},
            {field: 'lon'},
            {field: 'lookback', visible: false},
//            {field: 'lookforward', visible: false},
            {
                field: 'action',
                headerCellTemplate: ' ',
                cellTemplate: '<button type="button" class="btn btn-default btn-xs" ng-click="$emit(\'updateWeather\')">Force update</button>' +
                '<button type="button" class="btn btn-default btn-xs" ng-click="$emit(\'viewWeather\')">View weather</button>'
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
            templateUrl: 'static/partials/weather-plot-modal.html',
            controller: 'WeatherPlotCtrl',
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

app.controller('NewLocationCtrl', ['$scope', '$rootScope', '$http', '$log', function ($scope, $rootScope, $http, $log) {
    $scope.lookback = 10;
//    $scope.lookforward = 10;

    $scope.gridOptions = {
        minRowsToShow: 5,
        enableSorting: false,
        enableRowSelection: true,
        multiSelect: false,
        columnDefs: [
            {field: 'name'},
            {field: 'city'},
            {name: 'Country', field: 'country_name'}
        ]
    };

    $scope.search = function () {
        $http({
            url: $SCRIPT_ROOT + '/locations/geolookup',
            method: "GET",
            params: {query: $scope.query}
        })
            .then(function (data) {
                    if ('error' in data.data) {
                        alertify.error(data.data.error);
                    } else {
                        console.log(data.data.data);
                        var result = data.data.data;
                        $scope.manyLocations = 'results' in result.response;
                        $scope.oneLocation = 'location' in result;
                        $scope.notFound = result.response.error;
                        if ($scope.oneLocation) {
                            $scope.location = result.location;
                            $scope.name = result.location.city;
                        }
                        if ($scope.manyLocations) {
                            $scope.gridOptions.data = result.response.results;
                        }
                    }
                },
                function (error) {
                    alertify.error(error);
                });
    };

    $scope.gridOptions.onRegisterApi = function (gridApi) {
        //set gridApi on scope
        $scope.gridApi = gridApi;
        gridApi.selection.on.rowSelectionChanged($scope, function (row) {
            if (row.isSelected) {
                var zmw = row.entity.zmw;
                $http({
                    url: $SCRIPT_ROOT + '/locations/geolookup',
                    method: "GET",
                    params: {query: 'zmw:' + zmw}
                })
                    .then(function (data) {
                            if ('error' in data.data) {
                                alertify.error(data.data.error);
                            } else {
                                var result = data.data.data;
                                $scope.oneLocation = 'location' in result;
                                $scope.notFound = result.response.error;
                                if ($scope.oneLocation) {
                                    $scope.location = result.location;
                                    $scope.name = result.location.city;
                                }
                            }
                        },
                        function (error) {
                            alertify.error(error);
                        });
            } else {
                $scope.oneLocation = false;
            }
        });

    };

    $scope.addLocation = function () {
        $('#new-location-dialog').modal('hide');
        $scope.location.name = $scope.name;
        $scope.location.lookback = $scope.lookback;
//        $scope.location.lookforward = $scope.lookforward;
        alertify.message('Wait until data will be loaded');
        $http({
            url: $SCRIPT_ROOT + '/locations',
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify($scope.location)
        })
            .then(function (data) {
                    if ('error' in data.data) {
                        alertify.error(data.data.error);
                    } else {
                        alertify.success('OK');
                        $rootScope.$broadcast('updateLocations');
                    }
                },
                function (error) {
                    alertify.error(error);
                });
    };

}]);

app.controller('WeatherPlotCtrl', ['$scope', '$http', '$q', '$uibModalInstance', 'entity',
    function ($scope, $http, $q, $uibModalInstance, entity) {

        var locationId = entity.id;
        $scope.locationName = entity.name;

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $q.all([
            $http.get($SCRIPT_ROOT + '/locations/' + locationId + '/history').then(function(response) {
                if ('error' in response.data) {
                        alertify.error('Error while getting history for location "' + $scope.locationName + '": ' + response.data.error);
                }
              $scope.history_data = response.data.data
            },
                function (error) {
                    alertify.error('Error while getting history for location "' + $scope.locationName + '": ' + error.statusText);
                }),
            $http.get($SCRIPT_ROOT + '/locations/' + locationId + '/forecast').then(function(response) {
                if ('error' in response.data) {
                        alertify.error('Error while getting forecast for location "' + $scope.locationName + '": ' + response.data.error);
                }
              $scope.forecast_data = response.data.data
            },
                function (error) {
                    alertify.error('Error while getting history for location "' + $scope.locationName + '": ' + error.statusText);
                })
          ]).then(function() {
                        $('#weather-chart-container').empty();
                        $('#weather-chart-container').highcharts('StockChart', {
                            rangeSelector: {
                                selected: 1
                            },
                            title: {
                                text: $scope.locationName
                            },
                            tooltip: {
                                xDateFormat: '%b %e, %Y, %H:%M'
                            },
                            credits: {
                                enabled: false
                            },
                            yAxis: [{
                                title: {
                                    text: 'Temperature, C'
                                }
                            }, {
                                title: {
                                    text: 'Wind speed, km/h'
                                }
                            }, {
                                title: {
                                    text: 'Wind direction, degrees'
                                }
                            }],
                            series: [{
                                name: 'Temperature, C',
                                data: $scope.history_data.tempm.concat($scope.forecast_data.tempm),
                                zoneAxis: 'x',
                                zones: [{
                                    value: $scope.forecast_data.tempm[0][0]
                                }, {
                                    dashStyle: 'dot'
                                }],
                                tooltip: {
                                    valueDecimals: 1
                                }
                            }, {
                                name: 'Wind speed, km/h',
                                data: $scope.history_data.wspdm.concat($scope.forecast_data.wspdm),
                                zoneAxis: 'x',
                                zones: [{
                                    value: $scope.forecast_data.wspdm[0][0]
                                }, {
                                    dashStyle: 'dot'
                                }],
                                tooltip: {
                                    valueDecimals: 1
                                },
                                yAxis: 1
                            }, {
                                name: 'Wind direction, degrees',
                                data: $scope.history_data.wdird.concat($scope.forecast_data.wdird),
                                zoneAxis: 'x',
                                zones: [{
                                    value: $scope.forecast_data.wdird[0][0]
                                }, {
                                    dashStyle: 'dot'
                                }],
                                tooltip: {
                                    valueDecimals: 0
                                },
                                yAxis: 2
                            }]
                        });
          })

    }
]);
