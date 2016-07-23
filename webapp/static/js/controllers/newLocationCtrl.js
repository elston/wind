
app.controller('NewLocationCtrl', ['$scope', '$rootScope', '$http', '$log', '$timeout',
function ($scope, $rootScope, $http, $log, $timeout) {
    $scope.lookback = 10;
//    $scope.lookforward = 10;

    $scope.gridOptions = {
        minRowsToShow: 5,
        enableSorting: false,
        enableRowSelection: true,
        multiSelect: false,
        rowHeight: 40,
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
                            var mapOptions = {
                                zoom: 7,
                                center: new google.maps.LatLng($scope.location.lat, $scope.location.lon),
                                mapTypeId: google.maps.MapTypeId.ROADMAP
                            };
                            // ROADMAP, SATELLITE, HYBRID, TERRAIN
                            $timeout(function () {
                                map = new google.maps.Map(document.getElementById('gmap_canvas'), mapOptions);
                                marker = new google.maps.Marker({
                                    map: map,
                                    position: new google.maps.LatLng($scope.location.lat, $scope.location.lon)
                                });
                            }, 1000);

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
                                    var mapOptions = {
                                        zoom: 7,
                                        center: new google.maps.LatLng($scope.location.lat, $scope.location.lon),
                                        mapTypeId: google.maps.MapTypeId.ROADMAP
                                    };
                                    // ROADMAP, SATELLITE, HYBRID, TERRAIN
                                    $timeout(function () {
                                        map = new google.maps.Map(document.getElementById('gmap_canvas'), mapOptions);
                                        marker = new google.maps.Marker({
                                            map: map,
                                            position: new google.maps.LatLng($scope.location.lat, $scope.location.lon)
                                        });
                                    }, 1000);
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
