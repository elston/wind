/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('LocationDataCtrl', ['$scope', '$rootScope', '$http', '$uibModalInstance', 'entity',
    function ($scope, $rootScope, $http, $uibModalInstance, entity) {
        'use strict';

        $scope.name = entity.name;
        $scope.timeRange = {
            type: entity.time_range,
            end: new Date(entity.history_end),
            start: new Date(entity.history_start),
            lookback: entity.lookback
        };

        $scope.update = function () {
            $http({
                url: $SCRIPT_ROOT + '/locations',
                method: "POST",
                headers: {'Content-Type': 'application/json'},
                data: JSON.stringify({
                    id: entity.id,
                    name: $scope.name,
                    time_range: $scope.timeRange.type,
                    lookback: $scope.timeRange.lookback,
                    history_start: $scope.timeRange.start.getTime(),
                    history_end: $scope.timeRange.end.getTime()
                })
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

        $scope.close = function () {
            $uibModalInstance.close();
        };

    }

]);
