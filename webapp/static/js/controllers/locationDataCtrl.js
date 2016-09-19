/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('LocationDataCtrl', ['$scope', '$rootScope', '$uibModalInstance', 'entity', 'locationService',
    function ($scope, $rootScope, $uibModalInstance, entity, locationService) {
        'use strict';

        $scope.name = entity.name;
        $scope.timeRange = {
            type: entity.time_range,
            end: new Date(entity.history_end),
            start: new Date(entity.history_start),
            lookback: entity.lookback
        };
        $scope.updateAt11am = entity.update_at_11am;
        $scope.updateAt11pm = entity.update_at_11pm;

        $scope.update = function () {
            locationService.updateLocation({
                    id: entity.id,
                    name: $scope.name,
                    time_range: $scope.timeRange.type,
                    lookback: $scope.timeRange.lookback,
                    history_start: $scope.timeRange.start.getTime(),
                    history_end: $scope.timeRange.end.getTime(),
                    update_at_11am: $scope.updateAt11am,
                    update_at_11pm: $scope.updateAt11pm,
                })
                .then(function (data) {
                        alertify.success('OK');
                        $rootScope.$broadcast('updateLocations');
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        $scope.close = function () {
            $uibModalInstance.close();
        };

    }

]);
