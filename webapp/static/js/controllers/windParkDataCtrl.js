/*global app,$SCRIPT_ROOT,alertify*/

app.controller('WindParkDataCtrl', ['$scope', '$uibModalInstance',
    function ($scope, $uibModalInstance) {
        'use strict';

        $scope.close = function () {
            $uibModalInstance.close();
        };

    }]);
