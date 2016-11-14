/*global app,$SCRIPT_ROOT,alertify*/

app.factory('jobsService', ['$interval', '$rootScope', '$http', function ($interval, $rootScope, $http) {
    'use strict';
    var status = {};

    var getStatus = function () {
        return status;
    };

    var cancelJob = function (jobId) {
        return $http.post($SCRIPT_ROOT + '/rqjobs/' + jobId + '/cancel')
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        reload();
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    var killJob = function (jobId) {
        return $http.post($SCRIPT_ROOT + '/rqjobs/' + jobId + '/kill')
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        reload();
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    var reload = function () {
        $.get($SCRIPT_ROOT + '/status')
            .then(function (data) {
                    if ('error' in data) {
                        console.log(data.error);
                    } else {
                        status = data.data;
                        $rootScope.$broadcast('status:update', status);
                    }
                },
                function (error) {
                    console.log(error.statusText);
                });
    };

    $interval(reload, 2000);

    return {
        getStatus: getStatus,
        cancelJob: cancelJob,
        killJob: killJob
    };

}]);
