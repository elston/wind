/*global app,$SCRIPT_ROOT,alertify*/

app.controller('NewWindParkCtrl', ['$scope', '$rootScope', '$uibModalInstance', 'locationService',
    'marketService', 'windparkService',
    function ($scope, $rootScope, $uibModalInstance, locationService, marketService, windparkService) {
        'use strict';

        $scope.locations = locationService.getLocations();
        $scope.markets = marketService.getMarkets();

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $scope.addWindPark = function () {
            $uibModalInstance.close();
            windparkService.updateWindpark({
                    name: $scope.name,
                    location_id: $scope.location,
                    market_id: $scope.market
                })
                .then(function (data) {
                        $rootScope.$broadcast('updateWindParks');
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

    }]);
