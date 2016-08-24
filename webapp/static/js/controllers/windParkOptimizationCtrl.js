/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('WindParkOptimizationCtrl', ['$scope', '$interval', 'windparkService',
    function ($scope, $interval, windparkService) {
        'use strict';

        $scope.startDisabled = false;
        $scope.statusData = null;
        $scope.optimizationResults = null;
        $scope.optimizationDate = new Date($scope.windpark.optimization_job.date);

        var stopRefresh;

        $scope.optimize = function () {
            $scope.startDisabled = true;
            windparkService.startOptimization($scope.windpark.id, $scope.windpark.optimization_job);

            if ( angular.isDefined(stopRefresh) ) return;

            stopRefresh = $interval(function() {
                $scope.refresh();
            }, 2000);
        };

        $scope.refresh = function() {
            windparkService.optimizationStatus($scope.windpark.id)
                .then(function (statusData) {
                    $scope.statusData = statusData;
                    if( statusData === null) {
                        $scope.startDisabled = false;
                        $interval.cancel(stopRefresh);
                        stopRefresh = undefined;
                        return;
                    }
                    $scope.startDisabled = statusData.isStarted || statusData.isQueued;
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
