/*global app,$SCRIPT_ROOT,alertify*/

app.factory('jobsService', [function () {
    'use strict';
    var sJobsList = [];
    var rqJobsList = [];

    var getSchedulerJobs = function () {
        return sJobsList;
    };

    var getRqJobs = function () {
        return rqJobsList;
    };

    var loadJobsList = function () {
        return $.when(
            $.get($SCRIPT_ROOT + '/scheduler/jobs')
                .then(function (response) {
                        if ('error' in response) {
                            throw response.error;
                        } else {
                            sJobsList = response.data;
                        }
                    },
                    function (error) {
                        throw error.statusText;
                    }),
            $.get($SCRIPT_ROOT + '/rq/jobs')
                .then(function (response) {
                        if ('error' in response) {
                            throw response.error;
                        } else {
                            rqJobsList = response.data;
                        }
                    },
                    function (error) {
                        throw error.statusText;
                    })
        );
    };

    return {
        getSchedulerJobs: getSchedulerJobs,
        getRqJobs: getRqJobs,
        loadJobsList: loadJobsList
    };

}]);
