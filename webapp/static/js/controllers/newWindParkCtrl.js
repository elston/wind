/*global app,$SCRIPT_ROOT,alertify*/

app.controller('NewWindParkCtrl', ['$scope', '$rootScope', '$uibModalInstance', '$http',
    function ($scope, $rootScope, $uibModalInstance, $http) {
        'use strict';

        // TODO: idiotic way, use services to share locations and markets
        $http.get($SCRIPT_ROOT + '/locations')
            .then(function (response) {
                    if ('error' in response.data) {
                        alertify.error('Error while getting location: ' + response.data.error);
                    }
                    $scope.locations = response.data.data;
                },
                function (error) {
                    alertify.error('Error while getting location: ' + error.statusText);
                });
        $http.get($SCRIPT_ROOT + '/markets')
            .then(function (response) {
                    if ('error' in response.data) {
                        alertify.error('Error while getting markets: ' + response.data.error);
                    }
                    $scope.markets = response.data.data;
                },
                function (error) {
                    alertify.error('Error while gettingmarkets: ' + error.statusText);
                });

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $scope.addWindPark = function () {
            $uibModalInstance.close();
            $http({
                url: $SCRIPT_ROOT + '/windparks',
                method: "POST",
                headers: {'Content-Type': 'application/json'},
                data: JSON.stringify({
                    name: $scope.name,
                    location_id: $scope.location,
                    market_id: $scope.market
                })
            })
                .then(function (data) {
                        if ('error' in data.data) {
                            alertify.error(data.data.error);
                        } else {
                            alertify.success('OK');
                            $rootScope.$broadcast('updateWindParks');
                        }
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

    }]);
