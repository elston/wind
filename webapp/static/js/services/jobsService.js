/*global app,$SCRIPT_ROOT,alertify*/

app.factory('jobsService', ['$interval', '$rootScope', function ($interval, $rootScope) {
    'use strict';
    var status = {};

    var getStatus = function () {
        return status;
    };

    $interval(function () {
        $.get($SCRIPT_ROOT + '/status')
            .then(function (data) {
                    if ('error' in data) {
                        throw data.error;
                    } else {
                        status = data.data;
                        $rootScope.$broadcast('status:update', status);
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    }, 2000);

    return {
        getStatus: getStatus
    };

}]);
