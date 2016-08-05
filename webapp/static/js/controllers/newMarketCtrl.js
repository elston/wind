/*global app,$SCRIPT_ROOT,alertify*/

app.controller('NewMarketCtrl', ['$scope', '$rootScope', 'marketService',
    function ($scope, $rootScope, marketService) {
        'use strict';

        $scope.name = '';

        $scope.addMarket = function () {
            $('#new-market-dialog').modal('hide');
            marketService.updateMarket({name: $scope.name})
                .then(function (result) {
                        $rootScope.$broadcast('updateMarkets');
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };
    }]);
