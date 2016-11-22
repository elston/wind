/*global app,alertify*/

app.controller('JobsCtrl', ['$scope', '$uibModal', 'jobsService', function ($scope, $uibModal, jobsService) {
    'use strict';

    $scope.sjGridOptions = {
        columnDefs: [
            {field: 'name', name: 'Name'},
            {field: 'next_run_time', name: 'Next run time'}
        ]
    };

    $scope.rqjGridOptions = {
        columnDefs: [
            {
                field: 'name', name: 'Name',
                cellTemplate: '<div class="ui-grid-cell-contents" uib-tooltip="{{grid.getCellValue(row, col)}}" ' +
                'tooltip-append-to-body="true">' +
                '{{grid.getCellValue(row, col)}}</div>'
            },
            {field: 'status'},
//            {
//                field: 'created_at',
//                cellTemplate: '<div class="ui-grid-cell-contents" uib-tooltip="{{grid.getCellValue(row, col)}}" ' +
//                'tooltip-append-to-body="true">' +
//                '{{grid.getCellValue(row, col)}}</div>'
//            },
            {
                field: 'enqueued_at',
                cellTemplate: '<div class="ui-grid-cell-contents" uib-tooltip="{{grid.getCellValue(row, col)}}" ' +
                'tooltip-append-to-body="true">' +
                '{{grid.getCellValue(row, col)}}</div>'
            },
            {
                field: 'ended_at',
                cellTemplate: '<div class="ui-grid-cell-contents" uib-tooltip="{{grid.getCellValue(row, col)}}" ' +
                'tooltip-append-to-body="true">' +
                '{{grid.getCellValue(row, col)}}</div>'
            },
            {
                field: 'exc_info', name: 'Error',
                cellTemplate: '<div class="ui-grid-cell-contents">' +
                '<a href="#" ng-click="$emit(\'error:open\', grid.getCellValue(row, col))">' +
                '{{grid.getCellValue(row, col)}}</a></div>'
            },
            {
                field: 'meta', name: 'Log',
                cellTemplate: '<div class="ui-grid-cell-contents">' +
                '<a href="#" ng-click="$emit(\'log:open\', grid.getCellValue(row, col).log)" '+
                'ng-show="grid.getCellValue(row, col).log.length">' +
                '{{grid.getCellValue(row, col).log.length}} lines</a></div>'
            },
            {
                field: 'action',
                headerCellTemplate: ' ',
                enableHiding: false,
                width: 32,
                cellTemplate: '<button type="button" class="btn btn-warning btn-xs" '+
                'ng-show="row.entity.status==\'queued\'" ng-click="$emit(\'job:cancel\',row.entity.job_id)" ' +
                'tooltip-append-to-body="true" uib-tooltip="Cancel">' +
                '<span class="glyphicon glyphicon-remove-sign" aria-hidden="true"></span></button>' +
                '<button type="button" class="btn btn-danger btn-xs" '+
                'ng-show="row.entity.status==\'started\'" ng-click="$emit(\'job:kill\',row.entity.job_id)" ' +
                'tooltip-append-to-body="true" uib-tooltip="Kill">' +
                '<span class="glyphicon glyphicon-fire" aria-hidden="true"></span></button>'
            }
        ]
    };

    $scope.$on('status:update', function (event, data) {
        $scope.sjGridOptions.data = data.scheduler;
        $scope.rqjGridOptions.data = data.rqjobs;
    });

    $scope.$on('error:open', function (event, data) {
        $uibModal.open({
            templateUrl: 'jobErrorModal.html',
            size: 'lg',
            controller: function ($scope, $uibModalInstance) {
                $scope.errorMessage = data;
                $scope.close = function () {
                    $uibModalInstance.close();
                };
            }
        });
    });

    $scope.$on('log:open', function (event, data) {
        $uibModal.open({
            templateUrl: 'jobLogModal.html',
            size: 'lg',
            controller: function ($scope, $uibModalInstance) {
                $scope.jobLog = data.join('\n');
                $scope.close = function () {
                    $uibModalInstance.close();
                };
            }
        });
    });

    $scope.$on('job:cancel', function (event, data) {
        jobsService.cancelJob(data).then(function () {
                alertify.success('OK');
            },
            function (error) {
                alertify.error(error);
            });
    });

    $scope.$on('job:kill', function (event, data) {
        alertify.confirm('Confirm', 'Your activity can break data integrity. Would you like to proceed anyway?',
            function() {
            jobsService.killJob(data).then(function () {
                alertify.success('OK');
            },
            function (error) {
                alertify.error(error);
            })
            },
                        null);
    });
}]);
