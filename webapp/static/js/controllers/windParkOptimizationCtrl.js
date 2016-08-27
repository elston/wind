/*global app,$SCRIPT_ROOT,alertify,Highcharts,angular*/

app.controller('WindParkOptimizationCtrl', ['$scope', '$interval', '$timeout', 'windparkService',
    function ($scope, $interval, $timeout, windparkService) {
        'use strict';

        $scope.startDisabled = false;
        $scope.statusData = null;
        $scope.optimizationResults = null;
        $scope.optimizationDate = new Date($scope.windpark.optimization_job.date);

        var stopRefresh;

        $scope.optimize = function () {
            $scope.startDisabled = true;
            windparkService.startOptimization($scope.windpark.id, $scope.windpark.optimization_job);

            if (angular.isDefined(stopRefresh)) {
                return;
            }

            stopRefresh = $interval(function () {
                refresh();
            }, 2000);
        };

        $scope.terminate = function () {
            windparkService.terminateOptimization($scope.windpark.id)
                .then(function (statusData) {
                        alertify.success('OK');
                        refresh();
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        var refreshCharts = function (data) {
            var i, j;
            var Pd_series = [];
            for (i = 0; i < data.Pd.length; i++) {
                Pd_series.push({
                    data: data.Pd[i],
                    name: 'd' + i
                });
            }

            var Pa_series = [];
            for (i = 0; i < data.Pa.length; i++) {
                for (j = 0; j < data.Pa[i].length; j++) {
                    Pa_series.push({
                        data: data.Pa[i][j],
                        name: 'd' + i + ',l' + j
                    });
                }
            }

            var Ps_series = [];
            for (i = 0; i < data.Ps.length; i++) {
                for (j = 0; j < data.Ps[i].length; j++) {
                    Ps_series.push({
                        data: data.Ps[i][j],
                        name: 'd' + i + ',l' + j
                    });
                }
            }

            $timeout(function () {
                    $scope.chart1 = new Highcharts.Chart({
                        chart: {
                            renderTo: 'da-volumes',
                            animation: false,
                            type: 'column'
                        },
                        title: {
                            text: 'Day ahead volumes'
                        },
                        credits: {
                            enabled: false
                        },
                        plotOptions: {
                            column: {
                                animation: false,
                                marker: {
                                    enabled: false
                                }
                            }
                        },
                        yAxis: [{
                            title: {
                                text: 'Volume'
                            }
                        }],
                        series: Pd_series
                    });

                    $scope.chart2 = new Highcharts.Chart({
                        chart: {
                            renderTo: 'am-volumes',
                            animation: false,
                            type: 'column'
                        },
                        title: {
                            text: 'Adjustment market volumes'
                        },
                        credits: {
                            enabled: false
                        },
                        plotOptions: {
                            line: {
                                animation: false,
                                marker: {
                                    enabled: false
                                }
                            }
                        },
                        yAxis: [{
                            title: {
                                text: 'Volume'
                            }
                        }],
                        series: Pa_series
                    });

                    $scope.chart3 = new Highcharts.Chart({
                        chart: {
                            renderTo: 'total-volumes',
                            animation: false,
                            type: 'column'
                        },
                        title: {
                            text: 'Total volumes'
                        },
                        credits: {
                            enabled: false
                        },
                        plotOptions: {
                            line: {
                                animation: false,
                                marker: {
                                    enabled: false
                                }
                            }
                        },
                        yAxis: [{
                            title: {
                                text: 'Volume'
                            }
                        }],
                        series: Ps_series
                    });

                }
            );

        };

        var refreshOptimizationResults = function () {
            windparkService.optimizationResults($scope.windpark.id)
                .then(function (data) {
                        $scope.optimizationResults = data;
                        if (data !== null) {
                            refreshCharts(data);
                        }
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        var refresh = function () {
            windparkService.optimizationStatus($scope.windpark.id)
                .then(function (statusData) {
                        $scope.statusData = statusData;
                        if (statusData === null) {
                            $scope.startDisabled = false;
                            $interval.cancel(stopRefresh);
                            stopRefresh = undefined;
                            return;
                        }
                        $scope.startDisabled = statusData.isStarted || statusData.isQueued;
                        if (statusData.isFinished || statusData.isFailed) {
                            $interval.cancel(stopRefresh);
                            stopRefresh = undefined;
                            refreshOptimizationResults();
                        }
                    },
                    function (error) {
                        alertify.error(error);
                        $interval.cancel(stopRefresh);
                        stopRefresh = undefined;
                    });
        };

        refreshOptimizationResults();
        refresh();

        $scope.$on('$destroy', function () {
            if (angular.isDefined(stopRefresh)) {
                $interval.cancel(stopRefresh);
                stopRefresh = undefined;
            }
        });
    }]);
