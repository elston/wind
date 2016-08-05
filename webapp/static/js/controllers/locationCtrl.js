/*global app,$SCRIPT_ROOT,alertify,google*/

app.controller('LocationsCtrl', ['$scope', '$uibModal', 'locationService', function ($scope, $uibModal, locationService) {
    'use strict';

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
                            locationService.deleteLocation(row.entity.id)
                                .then(function () {
                                        $scope.update();
                                    },
                                    function (error) {
                                        alertify.error(error);
                                    });
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
                enableHiding: false,
                cellTemplate: '<button type="button" class="btn btn-default btn-xs" ng-click="$emit(\'updateWeather\')" ' +
                'tooltip-append-to-body="true" uib-tooltip="Reload">' +
                '<span class="glyphicon glyphicon-refresh" aria-hidden="true"></span></button>' +
                '<button type="button" class="btn btn-default btn-xs" ng-click="$emit(\'viewData\')" ' +
                'tooltip-append-to-body="true" uib-tooltip="View data">' +
                '<span class="glyphicon glyphicon-list-alt" aria-hidden="true"></span></button>' +
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
        locationService.updateHistory(locationId)
            .then(function () {
                    alertify.success('History for location "' + locationName + '" updated');
                },
                function (error) {
                    alertify.error('Error while updating history for location "' + locationName + '": ' + error);
                });

        locationService.updateForecast(locationId)
            .then(function () {
                    alertify.success('Forecast for location "' + locationName + '" updated');
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

    $scope.$on('viewData', function ($event) {
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'location-data-modal.html',
            controller: 'LocationDataCtrl',
            size: 'lg',
            resolve: {
                entity: function () {
                    return $event.targetScope.row.entity;
                }
            }
        });

    });


    $scope.updateMap = function () {
        var mapOptions = {
            //zoom: 7,
            //center: new google.maps.LatLng($scope.location.lat, $scope.location.lon),
            mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        // ROADMAP, SATELLITE, HYBRID, TERRAIN
        //$timeout(function () {
        var map = new google.maps.Map(document.getElementById('locations_map'), mapOptions);
        var markers = [];

        var bounds = new google.maps.LatLngBounds();

        $scope.gridOptions.data.forEach(function (location) {
            var marker = new google.maps.Marker({
                map: map,
                position: new google.maps.LatLng(location.lat, location.lon)
            });
            bounds.extend(marker.getPosition());
            var infoWindow = new google.maps.InfoWindow({
                content: location.name
            });
            google.maps.event.addListener(marker, 'click', function () {
                    infoWindow.open(map, marker);
                }
            );
            infoWindow.open(map, marker);
        });

        map.fitBounds(bounds);
        //}, 1000);
    };

    $scope.update = function () {
        var locations = locationService.getLocations();
        $scope.gridOptions.data = locations;
        $scope.noLocations = locations.length === 0;
        $scope.updateMap();
    };

    locationService.reload().then(function () {
            $scope.update();
        },
        function (error) {
            alertify.error(error);
        });

    $scope.$on('updateLocations', $scope.update);
    $scope.$on('updateMap', $scope.updateMap);

}]);
