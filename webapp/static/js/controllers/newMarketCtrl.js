/*global app,$SCRIPT_ROOT,alertify*/

app.controller('NewMarketCtrl', ['$scope', '$rootScope', '$http', '$log', '$timeout',
    function ($scope, $rootScope, $http, $log, $timeout) {
        'use strict';

        $scope.name = '';

        $scope.addMarket = function () {
            $('#new-market-dialog').modal('hide');
            $http({
                url: $SCRIPT_ROOT + '/markets',
                method: "POST",
                headers: {'Content-Type': 'application/json'},
                data: JSON.stringify({name: $scope.name})
            })
                .then(function (data) {
                        if ('error' in data.data) {
                            alertify.error(data.data.error);
                        } else {
                            alertify.success('OK');
                            $rootScope.$broadcast('updateMarkets');
                        }
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };
    }]);
