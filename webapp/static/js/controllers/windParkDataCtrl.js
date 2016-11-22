/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('WindParkDataCtrl', ['$scope', '$rootScope', 'locationService', 'marketService', 'windparkService',
    function ($scope, $rootScope, locationService, marketService, windparkService) {
        'use strict';

        $scope.windpark = $scope.tab.data;

        $scope.name = $scope.windpark.name;
        $scope.dataSource = $scope.windpark.data_source;
        $scope.locations = locationService.getLocations();
        $scope.markets = marketService.getMarkets();
        $scope.location = $scope.windpark.location;
        $scope.market = $scope.windpark.market;

        $scope.interlocked = false;

        $scope.$on('status:update', function (event, data) {
            $scope.interlocked = data.interlocks.windparks.indexOf($scope.windpark.id) !== -1;
        });

        $scope.update = function () {
            windparkService.updateWindpark({
                    id: $scope.windpark.id,
                    name: $scope.name,
                    location_id: $scope.location.id,
                    market_id: $scope.market.id,
                    data_source: $scope.dataSource
                })
                .then(function (data) {
                        alertify.success('OK');
                        $rootScope.$broadcast('reloadWindParks');
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

    }]);
