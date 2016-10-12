/*global app,$SCRIPT_ROOT,alertify,Highcharts,google*/

app.controller('NewLocationCtrl', ['$scope', '$rootScope', '$http', '$timeout', 'locationService',
    function ($scope, $rootScope, $http, $timeout, locationService) {
        'use strict';

        var now = new Date();
        $scope.timeRange = {
            type: 'rolling',
            end: now,
            start: new Date(now - 10 * 24 * 3600 * 1000),
            lookback: 10
        };
        $scope.updateAt11am = true;
        $scope.updateAt11pm = true;
//    $scope.lookforward = 10;

        $scope.gridOptions = {
            minRowsToShow: 5,
            enableRowSelection: true,
            multiSelect: false,
            rowHeight: 40,
            columnDefs: [
                {field: 'name'},
                {field: 'city'},
                {name: 'Country', field: 'country_name'}
            ]
        };

        $scope.getSuggestions = function (query) {
            return $http.jsonp('http://autocomplete.wunderground.com/aq', {
                    params: {
                        query: query,
                        cb: 'JSON_CALLBACK'
                    }
                })
                .then(function (response) {
                    return response.data.RESULTS.map(function (item) {
                        return item;
                    });
                });
        };

        $scope.typeaheadSelected = function ($item, $model, $label, $event) {
            $scope.query = $item.name;
            $scope.search('zmw:' + $item.zmw);
        };

        $scope.search = function (query) {
            var query1 = query ? query : $scope.query;
            locationService.geoLookup(query1)
                .then(function (result) {
                        $scope.manyLocations = 'results' in result.response;
                        $scope.oneLocation = 'location' in result;
                        $scope.notFound = result.response.error;
                        if ($scope.oneLocation) {
                            $scope.location = result.location;
                            $scope.name = result.location.city;
                            var mapOptions = {
                                zoom: 7,
                                center: new google.maps.LatLng($scope.location.lat, $scope.location.lon),
                                mapTypeId: google.maps.MapTypeId.ROADMAP
                            };
                            // ROADMAP, SATELLITE, HYBRID, TERRAIN
                            $timeout(function () {
                                var map = new google.maps.Map(document.getElementById('gmap_canvas'), mapOptions);
                                var marker = new google.maps.Marker({
                                    map: map,
                                    position: new google.maps.LatLng($scope.location.lat, $scope.location.lon)
                                });
                            }, 1000);

                        }
                        if ($scope.manyLocations) {
                            $scope.gridOptions.data = result.response.results;
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
                    locationService.geoLookup('zmw:' + zmw)
                        .then(function (result) {
                                $scope.oneLocation = 'location' in result;
                                $scope.notFound = result.response.error;
                                if ($scope.oneLocation) {
                                    $scope.location = result.location;
                                    $scope.name = result.location.city;
                                    var mapOptions = {
                                        zoom: 7,
                                        center: new google.maps.LatLng($scope.location.lat, $scope.location.lon),
                                        mapTypeId: google.maps.MapTypeId.ROADMAP
                                    };
                                    // ROADMAP, SATELLITE, HYBRID, TERRAIN
                                    $timeout(function () {
                                        var map = new google.maps.Map(document.getElementById('gmap_canvas'), mapOptions);
                                        var marker = new google.maps.Marker({
                                            map: map,
                                            position: new google.maps.LatLng($scope.location.lat, $scope.location.lon)
                                        });
                                    }, 1000);
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
            $scope.location.time_range = $scope.timeRange.type;
            $scope.location.lookback = $scope.timeRange.lookback;
            $scope.location.history_start = $scope.timeRange.start.getTime();
            $scope.location.history_end = $scope.timeRange.end.getTime();
            $scope.location.update_at_11am = $scope.updateAt11am;
            $scope.location.update_at_11pm = $scope.updateAt11pm;
//        $scope.location.lookforward = $scope.lookforward;
            locationService.updateLocation($scope.location)
                .then(function (data) {
                        $rootScope.$broadcast('updateLocations');
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

    }]);
