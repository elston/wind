/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('WindParkOptimizationCtrl', ['$scope', '$interval', 'windparkService',
    function ($scope, $interval, windparkService) {
        'use strict';

        $scope.startDisabled = false;
        $scope.statusData = null;
        $scope.optimizationResults = null;

        var stopRefresh;

        $scope.optimize = function () {
            windparkService.startOptimization($scope.windpark.id);

            if ( angular.isDefined(stopRefresh) ) return;

            stopRefresh = $interval(function() {
                $scope.refresh();
            }, 2000);
        };

        $scope.refresh = function() {
            windparkService.optimizationStatus($scope.windpark.id)
                .then(function (statusData) {
                    $scope.statusData = statusData;
                    $scope.startDisabled = statusData.isWorking || statusData.isQueued;
                    if(statusData.isFinished || statusData.isFailed) {
                        $interval.cancel(stopRefresh);
                        stopRefresh = undefined;
                        windparkService.optimizationResults($scope.windpark.id)
                            .then(function (data) {
                                $scope.optimizationResults = data;
                            },
                            function (error) {
                                alertify.error(error);
                            });
                    }
                },
                function (error) {
                    alertify.error(error);
                    $interval.cancel(stopRefresh);
                    stopRefresh = undefined;
                });
        };

        windparkService.optimizationResults($scope.windpark.id)
            .then(function (data) {
                $scope.optimizationResults = data;
            },
            function (error) {
                alertify.error(error);
            });

        $scope.refresh();

        $scope.$on('$destroy', function() {
            if (angular.isDefined(stopRefresh)) {
                $interval.cancel(stopRefresh);
                stopRefresh = undefined;
            }
        });
}]);
