/*global app,alertify*/

app.controller('JobsCtrl', ['$scope', '$interval', 'jobsService', function ($scope, $interval, jobsService) {
    'use strict';

    $scope.sjGridOptions = {
        columnDefs: [
            {field: 'id', name: 'Name'},
            {field: 'next_run_time', name: 'Next run time'}
        ]
    };

    $scope.rqjGridOptions = {
        columnDefs: [
            {field: 'job_id', name: 'Name'},
            {field: 'status'},
            {field: 'created_at'},
            {field: 'enqueued_at'},
            {field: 'ended_at'},
            {field: 'exc_info', name: 'Error'}
        ]
    };

    $scope.update = function () {
        $scope.sjGridOptions.data = jobsService.getSchedulerJobs();
        $scope.rqjGridOptions.data = jobsService.getRqJobs();
    };

    $interval(function () {
        jobsService.loadJobsList().then(function () {
                $scope.update();
            },
            function (error) {
                alertify.error(error);
            });
    }, 2000);

}]);
