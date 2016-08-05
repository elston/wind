/*global app,$SCRIPT_ROOT,alertify*/

app.controller('NewWindParkCtrl', ['$scope', '$rootScope', '$uibModalInstance', '$http', 'locationService', 'marketService',
    function ($scope, $rootScope, $uibModalInstance, $http, locationService, marketService) {
        'use strict';

        $scope.locations = locationService.getLocations();
        $scope.markets = marketService.getMarkets();

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
