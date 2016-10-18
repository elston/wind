/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('ForecastErrorModelCtrl', ['$scope', '$uibModalInstance', 'entity', 'locationService',
    function ($scope, $uibModalInstance, entity, locationService) {
        'use strict';

        $scope.locationName = entity.name;
        $scope.selectedDataPlot = 'off';
        $scope.selectedAnalyticPlot = 'off';
        $scope.modelData = {};

        $scope.observationEnabled = false;
        $scope.forecastEnabled = true;
        $scope.errorsEnabled = false;

        $scope.datePickerModel = {startDate: null, endDate: null};
        $scope.datePickerMin = null;
        $scope.datePickerMax = null;

        $scope.datePickerOpts = {
            locale: {
                applyClass: 'btn-warning'
            },
            eventHandlers: {
                'apply.daterangepicker': function(ev, picker) {
                    $scope.updateSeriesSet();
            }, 'show.daterangepicker': function() {
                    angular.element(document.getElementsByClassName('applyBtn')[0]).addClass('btn-warning');
            }}

        };

        $scope.forDatePickerParser = function (date) {
            var parsedDate = new Date(date);
            var modifiedDate = new Date(parsedDate.getFullYear()+'-'+(parsedDate.getMonth()+1)+'-'+parsedDate.getDate());
            return modifiedDate;
        };

        $scope.updateSeriesSet = function () {

            var parsedStartDate = new Date(new Date($scope.datePickerModel.startDate).setUTCHours(0,0,0,0)).setUTCDate(new Date($scope.datePickerModel.startDate).getDate());
            var parsedEndDate = new Date(new Date($scope.datePickerModel.endDate).setUTCHours(23,59,0,0)).setUTCDate(new Date($scope.datePickerModel.endDate).getDate());

            if ($scope.observationEnabled) {
                $scope.chart.series[0].show();
                $scope.chart.series[0].options.showInLegend = true;
                $scope.chart.legend.renderItem($scope.chart.series[0]);
                $scope.chart.legend.render();
            } else {
                $scope.chart.series[0].hide();
                $scope.chart.series[0].options.showInLegend = false;
                $scope.chart.series[0].legendItem = null;
                $scope.chart.legend.destroyItem($scope.chart.series[0]);
                $scope.chart.legend.render();
            }

            for (var i = 1; i < $scope.chart.series.length - 1; i += 2) {
                if ($scope.errorsEnabled) {
                    if ($scope.forDatePickerParser($scope.chart.series[i + 0].data[0].x) >= new Date(parsedStartDate)
                        && $scope.forDatePickerParser($scope.chart.series[i + 0].data[0].x) <= new Date(parsedEndDate)){
                        $scope.chart.series[i + 0].show();
                        $scope.chart.series[i + 0].options.showInLegend = true;
                        $scope.chart.legend.renderItem($scope.chart.series[i + 0]);
                        $scope.chart.legend.render();
                    } else {
                        $scope.chart.series[i + 0].hide();
                        $scope.chart.series[i + 0].options.showInLegend = false;
                        $scope.chart.series[i + 0].legendItem = null;
                        $scope.chart.legend.destroyItem($scope.chart.series[i + 0]);
                        $scope.chart.legend.render();
                    }
                } else {
                    $scope.chart.series[i + 0].hide();
                    $scope.chart.series[i + 0].options.showInLegend = false;
                    $scope.chart.series[i + 0].legendItem = null;
                    $scope.chart.legend.destroyItem($scope.chart.series[i + 0]);
                    $scope.chart.legend.render();
                }

                if ($scope.forecastEnabled) {
                    if ($scope.forDatePickerParser($scope.chart.series[i + 1].data[0].x) >= new Date(parsedStartDate)
                        && $scope.forDatePickerParser($scope.chart.series[i + 1].data[0].x) <= new Date(parsedEndDate)){
                        $scope.chart.series[i + 1].show();
                        $scope.chart.series[i + 1].options.showInLegend = true;
                        $scope.chart.legend.renderItem($scope.chart.series[i + 1]);
                        $scope.chart.legend.render();
                    } else {
                        $scope.chart.series[i + 1].hide();
                        $scope.chart.series[i + 1].options.showInLegend = false;
                        $scope.chart.series[i + 1].legendItem = null;
                        $scope.chart.legend.destroyItem($scope.chart.series[i + 1]);
                        $scope.chart.legend.render();
                    }
                } else {
                    $scope.chart.series[i + 1].hide();
                    $scope.chart.series[i + 1].options.showInLegend = false;
                    $scope.chart.series[i + 1].legendItem = null;
                    $scope.chart.legend.destroyItem($scope.chart.series[i + 1]);
                    $scope.chart.legend.render();
                }
            }

            // setTimeout(function(){
            //     $scope.chart.xAxis[0].setExtremes(
            //         new Date(new Date($scope.datePickerModel.startDate).setUTCHours(0,0,0,0)).setUTCDate(new Date($scope.datePickerModel.startDate).getDate()),
            //         new Date(new Date($scope.datePickerModel.endDate).setUTCHours(23,59,0,0)).setUTCDate(new Date($scope.datePickerModel.endDate).getDate()));
            // }, 1);

            setTimeout(function(){
                $scope.chart.xAxis[0].setExtremes(
                    parsedStartDate,
                    parsedEndDate);
            }, 1);
        };

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

                        $scope.datePickerStart = function () {
                            var first = $scope.errorsChunked[$scope.errorsChunked.length - 1].errors[0];
                            var parsedFirstDate = new Date(first[0]);
                            parsedFirstDate.setUTCDate(parsedFirstDate.getUTCDate() - 4);
                            var day = parsedFirstDate.getUTCDate();
                            if(day.toString().length == 1){
                                day = '0'+day;
                            }
                            return parsedFirstDate.getUTCFullYear()+'-'+(parsedFirstDate.getUTCMonth()+1)+'-'+day;
                        };

                        $scope.datePickerEnd = function () {
                            var last = $scope.errorsChunked[$scope.errorsChunked.length - 1].errors[0];
                            var parsedLastDate = new Date(last[0]);
                            return parsedLastDate.getUTCFullYear()+'-'+(parsedLastDate.getUTCMonth()+1)+'-'+parsedLastDate.getUTCDate();
                        };

                        $scope.dateMinInitial = function () {
                            var first = $scope.errorsChunked[0].errors[0];
                            var parsedFirstDate = new Date(first[0]);
                            return parsedFirstDate.getUTCFullYear()+'-'+(parsedFirstDate.getUTCMonth()+1)+'-'+parsedFirstDate.getUTCDate();
                        };

                        $scope.datePickerMin = $scope.dateMinInitial();
                        $scope.datePickerMax = $scope.datePickerEnd();

                        $scope.datePickerModel = {startDate: $scope.datePickerStart(), endDate: $scope.datePickerEnd()};

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

                        $scope.updateSeriesSet();
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
