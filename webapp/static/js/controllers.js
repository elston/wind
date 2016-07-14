var app = angular.module('app', ['ui.grid', 'ui.grid.selection', 'angularModalService']);

app.controller('LocationsCtrl', ['$scope', '$http', '$log', 'ModalService', function ($scope, $http, $log, ModalService) {

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
            {field: 'lookforward', visible: false},
            {
                field: 'action',
                headerCellTemplate: ' ',
                cellTemplate: '<button type="button" class="btn btn-default btn-sm" ng-click="$emit(\'updateHistory\')">Force update</button>' +
                '<button type="button" class="btn btn-default btn-sm" ng-click="$emit(\'viewHistory\')">View history</button>'
            }
        ]
    };

    $scope.$on('updateHistory', function ($event) {
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
    });

    $scope.$on('viewHistory', function ($event) {
        var locationId = $event.targetScope.row.entity.id;
        ModalService.showModal({
            templateUrl: "static/partials/weather-history-modal.html",
            controller: "WeatherHistoryCtrl",
            inputs: {
                locationId: locationId,
                locationName: $event.targetScope.row.entity.name
            }
        }).then(function (modal) {
            modal.element.modal();
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
    $scope.lookback = 300;
    $scope.lookforward = 10;

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
        $scope.location.lookforward = $scope.lookforward;
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

app.controller('WeatherHistoryCtrl', ['$scope', '$http', 'close', 'locationId', 'locationName',
    function ($scope, $http, close, locationId, locationName) {
        $scope.locationId = locationId;
        $scope.locationName = locationName;

        $scope.closeModal = function (result) {
            close(result, 500); // close, but give 200ms for bootstrap to animate
        };

        $http.get($SCRIPT_ROOT + '/locations/' + locationId + '/history')
            .then(function (data) {
                    if ('error' in data.data) {
                        alertify.error('Error while getting history for location "' + locationName + '": ' + data.data.error);
                    } else {
                        var observations = data.data.data;
                        $('#weather-chart-container').highcharts('StockChart', {
                            rangeSelector: {
                                selected: 1
                            },
                            title: {
                                text: locationName
                            },
                            tooltip: {
                                xDateFormat: '%b %e, %Y'
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
                                data: observations.tempm,
                                tooltip: {
                                    valueDecimals: 1
                                }
                            }, {
                                name: 'Wind speed, km/h',
                                data: observations.wspdm,
                                tooltip: {
                                    valueDecimals: 1
                                },
                                yAxis: 1
                            }, {
                                name: 'Wind direction, degrees',
                                data: observations.wdird,
                                tooltip: {
                                    valueDecimals: 0
                                },
                                yAxis: 2
                            }]
                        });
                    }
                },
                function (error) {
                    alertify.error('Error while getting history for location "' + locationName + '": ' + error.statusText);
                });

    }
]);
