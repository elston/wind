/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('ForecastErrorModelCtrl', ['$scope', '$uibModalInstance', 'entity', 'locationService',
    function ($scope, $uibModalInstance, entity, locationService) {
        'use strict';

        $scope.locationName = entity.name;
        $scope.selectedDataPlot = 'off';
        $scope.selectedAnalyticPlot = 'off';
        $scope.modelData = {};

        $scope.update = function () {
            locationService.getModelData(entity.id)
                .then(
                    function (result) {
                        $scope.modelData = result;
                    },
                    function (error) {
                        alertify.error(error);
                    }
                );
        };

        $scope.update();

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $scope.plotErrorsChunked = function () {
            locationService.getErrorsChunked(entity.id)
                .then(
                    function (result) {
                        $scope.errorsChunked = result.errors;
                        var series = [{
                            name: 'Observations',
                            data: result.observations,
                            animation: false,
                            marker: {
                                enabled: false
                            },
                            lineWidth: 4
                        }];
                        result.errors.forEach(function (elem) {
                            series.push({
                                name: 'error ' + elem.timestamp,
                                data: elem.errors,
                                animation: false,
                                marker: {
                                    enabled: false
                                }
                            });
                            series.push({
                                name: 'forecast ' + elem.timestamp,
                                data: elem.forecasts,
                                animation: false,
                                marker: {
                                    enabled: false
                                },
                                dashStyle: 'Dot'
                            });
                        });
                        $scope.chart = new Highcharts.Chart({
                            chart: {
                                renderTo: 'plot-value-errors-chunked',
                                animation: false
                            },
                            title: {
                                text: 'Forecast error'
                            },
                            credits: {
                                enabled: false
                            },
                            legend: {
                                enabled: true
                            },
                            yAxis: [{
                                title: {
                                    text: 'Observation−forecast, km/h'
                                }
                            }],
                            xAxis: [{
                                title: {
                                    text: 'Time (' + result.tzinfo + ')'
                                },
                                type: 'datetime'
                            }],
                            series: series
                        });
                    },
                    function (error) {
                        alertify.error(error);
                    }
                );
        };

        $scope.plotErrorsMerged = function () {
            locationService.getErrorsMerged(entity.id)
                .then(
                    function (result) {
                        $scope.errorsMerged = result;
                        $scope.chart = new Highcharts.Chart({
                            chart: {
                                renderTo: 'plot-value-errors-merged',
                                animation: false
                            },
                            title: {
                                text: 'Forecast error'
                            },
                            credits: {
                                enabled: false
                            },
                            legend: {
                                enabled: true
                            },
                            yAxis: [{
                                title: {
                                    text: 'Observation−forecast, km/h'
                                }
                            }],
                            series: [{
                                data: $scope.errorsMerged.errors
                            }]
                        });
                    },
                    function (error) {
                        alertify.error(error);
                    }
                );
        };

        $scope.cleanPlot = function (value) {
            $('plot-value-' + value[0]).empty();
        };

        $scope.fitErrorModel = function () {
            locationService.fitErrorModel(entity.id)
                .then(
                    function () {
                        alertify.success('OK');
                        $scope.update();
                    },
                    function (error) {
                        alertify.error(error);
                    }
                );
        };

        $scope.plotPrediction = function () {
            var pred = $scope.modelData.forecast_error_model.pred;
            var pred_se = $scope.modelData.forecast_error_model.pred_se;
            var pred_data = [];
            var pred_data_plus_minus = [];

            for (var i = 0; i < pred.length; i++) {
                pred_data.push([i, pred[i]]);
                pred_data_plus_minus.push([i, pred[i] - pred_se[i], pred[i] + pred_se[i]]);
            }
            $scope.chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'plot-error-pred',
                    animation: false
                },
                title: {
                    text: 'Wind speed forecast error prediction'
                },
                credits: {
                    enabled: false
                },
                yAxis: [{
                    title: {
                        text: 'Wind speed forecast error'
                    }
                }],
                xAxis: [{
                    title: {
                        text: 'Hours after forecast'
                    }
                }],
                series: [
                    {
                        data: pred_data,
                        animation: false,
                        zIndex: 1
                    },
                    {
                        data: pred_data_plus_minus,
                        animation: false,
                        type: 'arearange',
                        lineWidth: 0,
                        zIndex: 0,
                        fillOpacity: 0.3
                    }]
            });

        };

        $scope.plotResiduals = function () {
            var residuals = $scope.modelData.forecast_error_model.residuals;
            var residuals_data = [];

            for (var i = 0; i < residuals.length; i++) {
                residuals_data.push(residuals[i]);
            }
            $scope.chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'plot-error-residuals',
                    animation: false
                },
                title: {
                    text: 'Wind speed forecast error residuals'
                },
                credits: {
                    enabled: false
                },
                yAxis: [{
                    title: {
                        text: 'Wind speed forecast error'
                    }
                }],
                xAxis: [{
                    title: {
                        text: 'Hours'
                    }
                }],
                series: [{
                    data: residuals_data,
                    animation: false
                }]
            });

        };

        $scope.plotResidualsAcf = function () {
            var model = $scope.modelData.forecast_error_model;
            var data = model.residuals_acf;
            var clim = model.residuals_acf_clim;
            var series_data = [];

            for (var i = 0; i < data.length; i++) {
                series_data.push([i, data[i]]);
            }
            $scope.chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'plot-error-residuals-acf',
                    animation: false,
                    type: 'column'
                },
                title: {
                    text: 'Wind speed forecast error residuals ACF'
                },
                subtitle: {
                    text: 'clim=' + clim.toFixed(3)
                },
                credits: {
                    enabled: false
                },
                legend: {
                    enabled: false
                },
                yAxis: {
                    title: {
                        text: 'ACF'
                    },
                    plotLines: [{
                        color: 'blue',
                        width: 1,
                        value: clim,
                        dashStyle: 'dash'
                    }, {
                        color: 'blue',
                        width: 1,
                        value: -clim,
                        dashStyle: 'dash'
                    }]
                },
                xAxis: {
                    title: {
                        text: 'Lag'
                    },
                    allowDecimals: false
                },
                series: [{
                    data: series_data,
                    animation: false
                }]
            });

        };

        $scope.plotResidualsPacf = function () {
            var model = $scope.modelData.forecast_error_model;
            var data = model.residuals_pacf;
            var clim = model.residuals_pacf_clim;
            var series_data = [];

            for (var i = 0; i < data.length; i++) {
                series_data.push([i + 1, data[i]]);
            }
            $scope.chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'plot-error-residuals-pacf',
                    animation: false,
                    type: 'column'
                },
                title: {
                    text: 'Wind speed forecast error residuals PACF'
                },
                subtitle: {
                    text: 'clim=' + clim.toFixed(3)
                },
                credits: {
                    enabled: false
                },
                legend: {
                    enabled: false
                },
                yAxis: {
                    title: {
                        text: 'PACF'
                    },
                    plotLines: [{
                        color: 'blue',
                        width: 1,
                        value: clim,
                        dashStyle: 'dash'
                    }, {
                        color: 'blue',
                        width: 1,
                        value: -clim,
                        dashStyle: 'dash'
                    }]
                },
                xAxis: {
                    title: {
                        text: 'Lag'
                    },
                    allowDecimals: false
                },
                series: [{
                    data: series_data,
                    animation: false
                }]
            });

        };

        $scope.plotDataAcf = function () {
            var model = $scope.modelData.forecast_error_model;
            var data = model.data_acf;
            var clim = model.data_acf_clim;
            var series_data = [];

            for (var i = 0; i < data.length; i++) {
                series_data.push([i, data[i]]);
            }
            $scope.chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'plot-error-data-acf',
                    animation: false,
                    type: 'column'
                },
                title: {
                    text: 'Wind speed forecast error ACF'
                },
                subtitle: {
                    text: 'clim=' + clim.toFixed(3)
                },
                credits: {
                    enabled: false
                },
                legend: {
                    enabled: false
                },
                yAxis: {
                    title: {
                        text: 'ACF'
                    },
                    plotLines: [{
                        color: 'blue',
                        width: 1,
                        value: clim,
                        dashStyle: 'dash'
                    }, {
                        color: 'blue',
                        width: 1,
                        value: -clim,
                        dashStyle: 'dash'
                    }]
                },
                xAxis: {
                    title: {
                        text: 'Lag'
                    },
                    allowDecimals: false
                },
                series: [{
                    data: series_data,
                    animation: false
                }]
            });

        };

        $scope.plotDataPacf = function () {
            var model = $scope.modelData.forecast_error_model;
            var data = model.data_pacf;
            var clim = model.data_pacf_clim;
            var series_data = [];

            for (var i = 0; i < data.length; i++) {
                series_data.push([i + 1, data[i]]);
            }
            $scope.chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'plot-error-data-pacf',
                    animation: false,
                    type: 'column'
                },
                title: {
                    text: 'Wind speed forecast error PACF'
                },
                subtitle: {
                    text: 'clim=' + clim.toFixed(3)
                },
                credits: {
                    enabled: false
                },
                legend: {
                    enabled: false
                },
                yAxis: {
                    title: {
                        text: 'PACF'
                    },
                    plotLines: [{
                        color: 'blue',
                        width: 1,
                        value: clim,
                        dashStyle: 'dash'
                    }, {
                        color: 'blue',
                        width: 1,
                        value: -clim,
                        dashStyle: 'dash'
                    }]
                },
                xAxis: {
                    title: {
                        text: 'Lag'
                    },
                    allowDecimals: false
                },
                series: [{
                    data: series_data,
                    animation: false
                }]
            });

        };

        $scope.plotResidualsQq = function () {
            var data = $scope.modelData.forecast_error_model.qqplot_data;
            var series_data = [];

            for (var i = 0; i < data.x.length; i++) {
                series_data.push([data.x[i], data.y[i]]);
            }

            var minX = Math.min.apply(null, data.x);
            var maxX = Math.max.apply(null, data.x);
            var linePoints = [[minX, data.intercept + minX * data.slope],
                [maxX, data.intercept + maxX * data.slope]];

            $scope.chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'plot-error-residuals-qq',
                    animation: false
                },
                title: {
                    text: 'Wind speed forecast error normal Q-Q plot'
                },
                subtitle: {
                    text: 'R<sup>2</sup>=' + data.r2.toFixed(4),
                    useHTML: true
                },
                credits: {
                    enabled: false
                },
                legend: {
                    enabled: false
                },
                yAxis: {
                    title: {
                        text: 'Ordered values'
                    }
                },
                xAxis: {
                    title: {
                        text: 'Quantiles'
                    }
                },
                series: [{
                    data: series_data,
                    animation: false,
                    type: 'scatter'
                },
                    {
                        data: linePoints,
                        animation: false,
                        type: 'line',
                        marker: {
                            enabled: false
                        }
                    }]
            });

        };

    }

]);
