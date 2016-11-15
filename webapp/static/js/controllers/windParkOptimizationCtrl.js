/*global app,$SCRIPT_ROOT,alertify,Highcharts,angular*/

app.controller('WindParkOptimizationCtrl', ['$scope', '$interval', '$timeout', 'windparkService',
    function ($scope, $interval, $timeout, windparkService) {
        'use strict';

        $scope.busy = false;
        $scope.statusData = null;
        $scope.optimizationResults = null;
        $scope.optimizationDate = new Date($scope.windpark.optimization_job.date);

        $scope.overrideVariance = false;
        if ($scope.location.forecast_error_model) {
            $scope.forecastErrorVariance = $scope.location.forecast_error_model.sigma2;
        }

        $scope.overrideVarianceChanged = function () {
            if (!$scope.overrideVariance) {
                $scope.forecastErrorVariance = $scope.location.forecast_error_model.sigma2;
            }
        };

        var startOptimization = function () {
            $scope.busy = true;
            windparkService.startOptimization($scope.windpark.id, $scope.windpark.optimization_job).then(
                function (data) {
                    $scope.jobId = data;
                }
            );
        };

        $scope.$on('status:update', function (event, data) {
            var busy = false;
            data.rqjobs.forEach(function (rqjob) {
                if (+rqjob.windpark === $scope.windpark.id && rqjob.job === 'optimize') {
                    $scope.statusData = rqjob;
                    if (rqjob.status !== 'finished' && rqjob.status !== 'failed') {
                        busy = true;
                    }
                }
            });
            if (!busy && $scope.busy) {
                refreshOptimizationResults();
            }
            $scope.busy = busy;
        });

        var confirmWarnings = function (warnings) {
            if (warnings.length === 0) {
                startOptimization();
            } else {
                var warning = warnings.shift();
                alertify.confirm('Confirm', warning,
                    function () {
                        $timeout(function () {
                            confirmWarnings(warnings);
                        }, 1000);
                    },
                    null);
            }
        };

        $scope.optimize = function () {
            $scope.windpark.optimization_job.date = $scope.optimizationDate.toISOString().split('T')[0];
            if ($scope.overrideVariance) {
                $scope.windpark.optimization_job.forecast_error_variance = +$scope.forecastErrorVariance;
            } else {
                $scope.windpark.optimization_job.forecast_error_variance = null;
            }
            windparkService.optimizationPretest($scope.windpark.id, $scope.windpark.optimization_job)
                .then(function (data) {
                        confirmWarnings(data);
                    },
                    function (error) {
                        alertify.alert('Fatal error', error);
                    });
        };

        var refreshCharts = function (data) {
            var i, j;

            var red_power_series = [];
            for (i = 0; i < data.reduced_simulated_power.length; i++) {
                for (j = 0; j < data.reduced_simulated_power[i].length; j++) {
                    var p = data.power_probs[i][j];
                    red_power_series.push({
                        data: data.reduced_simulated_power[i][j],
                        tooltip: {
                            valueDecimals: 3
                        },
                        name: 'l' + i + ',w' + j + ',p' + p.toFixed(2)
                    });
                }
            }

            var Pd_series = [];
            for (i = 0; i < data.Pd.length; i++) {
                Pd_series.push({
                    data: data.Pd[i],
                    tooltip: {
                        valueDecimals: 3
                    },
                    name: 'd' + i
                });
            }

            var Pa_series = [];
            for (i = 0; i < data.Pa.length; i++) {
                for (j = 0; j < data.Pa[i].length; j++) {
                    Pa_series.push({
                        data: data.Pa[i][j],
                        tooltip: {
                            valueDecimals: 3
                        },
                        name: 'l' + j + ',d' + i
                    });
                }
            }

            var Ps_series = [];
            for (i = 0; i < data.Ps.length; i++) {
                for (j = 0; j < data.Ps[i].length; j++) {
                    Ps_series.push({
                        data: data.Ps[i][j],
                        tooltip: {
                            valueDecimals: 3
                        },
                        name: 'd' + i + ',l' + j
                    });
                }
            }

            $timeout(function () {
                    $scope.chart_gen = new Highcharts.Chart({
                        chart: {
                            renderTo: 'opt-generation',
                            animation: false
                        },
                        title: {
                            text: 'Simulated generation'
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
                                text: 'Power, MW'
                            }
                        }],
                        xAxis: [{
                            type: 'datetime',
                            title: {
                                text: 'Time (' + data.tzinfo + ')'
                            }
                        }],
                        series: red_power_series
                    });

                    $scope.chart1 = new Highcharts.Chart({
                        chart: {
                            renderTo: 'da-volumes',
                            animation: false
                        },
                        title: {
                            text: 'Day ahead volumes'
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
                                text: 'Volume, MWh'
                            }
                        }],
                        xAxis: [{
                            type: 'datetime',
                            title: {
                                text: 'Time (' + data.tzinfo + ')'
                            }
                        }],
                        series: Pd_series
                    });

                    $scope.chart2 = new Highcharts.Chart({
                        chart: {
                            renderTo: 'am-volumes',
                            animation: false
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
                                text: 'Volume, MWh'
                            }
                        }],
                        xAxis: [{
                            type: 'datetime',
                            title: {
                                text: 'Time (' + data.tzinfo + ')'
                            }
                        }],
                        series: Pa_series
                    });

                    $scope.chart3 = new Highcharts.Chart({
                        chart: {
                            renderTo: 'total-volumes',
                            animation: false
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
                                text: 'Volume, MWh'
                            }
                        }],
                        xAxis: [{
                            type: 'datetime',
                            title: {
                                text: 'Time (' + data.tzinfo + ')'
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

        $timeout(function () {
            refreshOptimizationResults();
            $scope.$broadcast('rzSliderForceRender');
            $scope.$watch(
                function (scope) {
                    return scope.daOfferingCurveHour.value;
                },
                function (newVal, oldVal) {
                    windparkService.getDaOfferingCurve($scope.windpark.id, newVal)
                        .then(function (data) {
                                if (!data) {
                                    return;
                                }
                                $timeout(function () {
                                    var chart = new Highcharts.Chart({
                                        chart: {
                                            renderTo: 'da-offering-curve',
                                            animation: false
                                        },
                                        title: {
                                            text: 'DA offering curve'
                                        },
                                        credits: {
                                            enabled: false
                                        },
                                        legend: {
                                            enabled: false
                                        },
                                        plotOptions: {
                                            line: {
                                                animation: false,
                                                marker: {
                                                    enabled: true
                                                }
                                            }
                                        },
                                        xAxis: [{
                                            title: {
                                                text: 'Volume, MWh'
                                            },
                                            max: Math.max.apply(null, data.map(function (x) {
                                                return x[0];
                                            })) + 1,
                                            min: Math.min.apply(null, data.map(function (x) {
                                                return x[0];
                                            })) - 1
                                        }],
                                        yAxis: [{
                                            title: {
                                                text: 'DA price, €/MWh'
                                            },
                                            max: Math.max.apply(null, data.map(function (x) {
                                                return x[1];
                                            })) + 1,
                                            min: Math.min.apply(null, data.map(function (x) {
                                                return x[1];
                                            })) - 1
                                        }],
                                        series: [{
                                            name: 'DA price, €/MWh',
                                            data: data,
                                            animation: false,
                                            tooltip: {
                                                headerFormat: 'Volume, MWh: <b>{point.x:.3f}</b><br/>',
                                                pointFormat: '{series.name}: <b>{point.y}</b><br/>',
                                                valueDecimals: 1
                                            }
                                        }]
                                    });
                                });
                            },
                            function (error) {
                                alertify.error(error);
                            });
                }
            );
        }, 2000);

        $scope.downloadOptRes = function () {
            windparkService.downloadOptRes($scope.windpark.id);
        };

        $scope.daOfferingCurveHour = {
            value: 12,
            options: {
                floor: 0,
                ceil: 23,
                vertical: true
            }
        };

    }]);
