/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('MarketDataCtrl', ['$scope', '$uibModalInstance', 'entity', 'marketService',
    function ($scope, $uibModalInstance, entity, marketService) {
        'use strict';

        $scope.marketName = entity.name;
        $scope.busy = false;

        $scope.$on('status:update', function (event, data) {
            $scope.interlocked = data.interlocks.markets.indexOf(entity.id) !== -1;

            var busy = false;
            data.rqjobs.forEach(function (rqjob) {
                if (+rqjob.market === entity.id && rqjob.job === 'fit_price') {
                    if (rqjob.status !== 'finished' && rqjob.status !== 'failed') {
                        busy = true;
                    }
                }
            });
            if (!busy && $scope.busy) {
                $scope.update();
            }
            $scope.busy = busy;
        });

        $scope.chartsMetadata = [
            ['lambdaD', 'Day ahead prices'],
            ['lambdaA', 'Adjustment market prices'],
            ['MAvsMD', 'Difference between AM and DA prices'],
            ['lambdaPlus', 'Upward imbalance prices (lambdaPlus)'],
            ['lambdaMinus', 'Downward imbalance prices (lambdaMinus)'],
            ['r_pos', 'r+'],
            ['r_neg', 'r-'],
            ['sqrt_r', 'sqrt(r)']
        ];

        $scope.modelsMetadata = [
            ['lambdaD', 'Day ahead prices'],
            ['MAvsMD', 'Difference between AM and DA prices'],
            ['sqrt_r', 'sqrt(r)']
        ];

        $scope.update = function () {
            marketService.getSummary(entity.id)
                .then(function (result) {
                        $scope.summary = result;
                        $scope.summary.selectedDataPlot = 'off';
                        $scope.summary.selectedAnalyticPlot = {};
                        $scope.modelsMetadata.forEach(function (elem) {
                            $scope.summary.selectedAnalyticPlot[elem[0]] = 'off';
                        });
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        $scope.update();

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $scope.plotValue = function (value) {
            marketService.getValues(entity.id, value[0])
                .then(function (result) {
                        $scope.chart = new Highcharts.StockChart({
                            chart: {
                                renderTo: 'plot-value-' + value[0],
                                animation: false
                            },
                            rangeSelector: {
                                inputDateFormat: '%b %e, %Y',
                                inputEditDateFormat: '%Y-%m-%d',
                                inputBoxWidth: 150,
                                inputDateParser: function (value) {
                                    return new Date(new Date(value).setUTCHours(0,0,0,0)).setUTCDate(new Date(value).getDate());
                                }
                            },
                            title: {
                                text: value[1]
                            },
                            credits: {
                                enabled: false
                            },
                            yAxis: [{
                                title: {
                                    text: value[1]
                                }
                            }],
                            series: [{
                                data: result,
                                tooltip: {
                                    valueDecimals: 3
                                },
                                animation: false
                            }]
                        }, function (chart) {
                            setTimeout(function () {
                                $('input.highcharts-range-selector', $($scope.chart.container).parent())
                                    .datepicker();
                            }, 1);
                        });

                        $.datepicker.setDefaults({
                            dateFormat: 'yy-mm-dd',
                            onSelect: function (dateText) {
                                $(this).trigger('change');
                                $(this).trigger('blur');
                            },
                            onClose: function () {
                                $(this).trigger('change');
                                $(this).trigger('blur');
                            }
                        });
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        $scope.cleanPlot = function (value) {
            $('plot-value-' + value[0]).empty();
        };

        $scope.calculateMissing = function () {
            marketService.calculateMissing(entity.id)
                .then(function (response) {
                        alertify.success('OK');
                        $scope.update();
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        $scope.fitModel = function () {
            $scope.busy = true;
            marketService.fitModel(entity.id)
                .then(function (response) {
                        alertify.success('OK');
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        $scope.plotPrediction = function (value) {
            var pred = $scope.summary[value[0] + '_model'].pred;
            var pred_se = $scope.summary[value[0] + '_model'].pred_se;
            var pred_data = [];
            var pred_data_plus_minus = [];
            var d = new Date($scope.summary.end);

            for (var i = 0; i < pred.length; i++) {
                d.setHours(d.getHours() + 1);
                if (value[0] === 'lambdaD') {
                    pred_data.push([d.getTime(), Math.exp(pred[i])]);
                    pred_data_plus_minus.push([d.getTime(), Math.exp(pred[i] - pred_se[i]),
                        Math.exp(pred[i] + pred_se[i])]);
                } else {
                    pred_data.push([d.getTime(), pred[i]]);
                    pred_data_plus_minus.push([d.getTime(), pred[i] - pred_se[i], pred[i] + pred_se[i]]);
                }
            }
            $scope.chart = new Highcharts.StockChart({
                chart: {
                    renderTo: 'plot-' + value[0] + '-pred',
                    animation: false
                },
                rangeSelector: {
                    inputDateFormat: '%b %e, %Y',
                    inputEditDateFormat: '%Y-%m-%d',
                    inputBoxWidth: 150,
                    inputDateParser: function (value) {
                        return new Date(new Date(value).setUTCHours(0,0,0,0)).setUTCDate(new Date(value).getDate());
                    }
                },
                title: {
                    text: value[1] + ' prediction'
                },
                credits: {
                    enabled: false
                },
                yAxis: [{
                    title: {
                        text: value[1]
                    }
                }],
                xAxis: [{
                    type: 'datetime'
                }],
                series: [
                    {
                        data: pred_data,
                        tooltip: {
                            valueDecimals: 3
                        },
                        animation: false,
                        zIndex: 1
                    },
                    {
                        data: pred_data_plus_minus,
                        tooltip: {
                            valueDecimals: 3
                        },
                        animation: false,
                        type: 'arearange',
                        lineWidth: 0,
                        zIndex: 0,
                        fillOpacity: 0.3
                    }]
            }, function (chart) {
                setTimeout(function () {
                    $('input.highcharts-range-selector', $($scope.chart.container).parent())
                        .datepicker();
                }, 1);
            });

            $.datepicker.setDefaults({
                dateFormat: 'yy-mm-dd',
                onSelect: function (dateText) {
                    $(this).trigger('change');
                    $(this).trigger('blur');
                },
                onClose: function () {
                    $(this).trigger('change');
                    $(this).trigger('blur');
                }
            });
        };

        $scope.plotResiduals = function (value) {
            var residuals = $scope.summary[value[0] + '_model'].residuals;
            var residuals_data = [];
            var d = new Date($scope.summary.end);

            for (var i = 0; i < residuals.length; i++) {
                d.setHours(d.getHours() + 1);
                residuals_data.push([d.getTime(), residuals[i]]);
            }
            $scope.chart = new Highcharts.StockChart({
                chart: {
                    renderTo: 'plot-' + value[0] + '-residuals',
                    animation: false
                },
                rangeSelector: {
                    inputDateFormat: '%b %e, %Y',
                    inputEditDateFormat: '%Y-%m-%d',
                    inputBoxWidth: 150,
                    inputDateParser: function (value) {
                        return new Date(new Date(value).setUTCHours(0,0,0,0)).setUTCDate(new Date(value).getDate());
                    }
                },
                title: {
                    text: value[1] + ' residuals'
                },
                credits: {
                    enabled: false
                },
                yAxis: [{
                    title: {
                        text: value[1]
                    }
                }],
                xAxis: [{
                    type: 'datetime'
                }],
                series: [{
                    data: residuals_data,
                    tooltip: {
                        valueDecimals: 3
                    },
                    animation: false
                }]
            }, function (chart) {
                setTimeout(function () {
                    $('input.highcharts-range-selector', $($scope.chart.container).parent())
                        .datepicker();
                }, 1);
            });

            $.datepicker.setDefaults({
                dateFormat: 'yy-mm-dd',
                onSelect: function (dateText) {
                    $(this).trigger('change');
                    $(this).trigger('blur');
                },
                onClose: function () {
                    $(this).trigger('change');
                    $(this).trigger('blur');
                }
            });

        };

        $scope.plotResidualsAcf = function (value) {
            var model = $scope.summary[value[0] + '_model'];
            var data = model.residuals_acf;
            var clim = model.residuals_acf_clim;
            var series_data = [];

            for (var i = 0; i < data.length; i++) {
                series_data.push([i, data[i]]);
            }
            $scope.chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'plot-' + value[0] + '-residuals-acf',
                    animation: false,
                    type: 'column'
                },
                title: {
                    text: value[1] + ' residuals ACF'
                },
                subtitle : {
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
                    },{
                        color: 'blue',
                        width: 1,
                        value: -clim,
                        dashStyle: 'dash'
                    }],
                },
                xAxis: {
                    title: {
                        text: 'Lag'
                    },
                    allowDecimals: false
                },
                series: [{
                    data: series_data,
                    tooltip: {
                        valueDecimals: 3
                    },
                    animation: false
                }]
            });

        };

        $scope.plotResidualsPacf = function (value) {
            var model = $scope.summary[value[0] + '_model'];
            var data = model.residuals_pacf;
            var clim = model.residuals_pacf_clim;
            var series_data = [];

            for (var i = 0; i < data.length; i++) {
                series_data.push([i + 1, data[i]]);
            }
            $scope.chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'plot-' + value[0] + '-residuals-pacf',
                    animation: false,
                    type: 'column'
                },
                title: {
                    text: value[1] + ' residuals PACF'
                },
                subtitle : {
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
                    },{
                        color: 'blue',
                        width: 1,
                        value: -clim,
                        dashStyle: 'dash'
                    }],
                },
                xAxis: {
                    title: {
                        text: 'Lag'
                    },
                    allowDecimals: false
                },
                series: [{
                    data: series_data,
                    tooltip: {
                        valueDecimals: 3
                    },
                    animation: false
                }]
            });

        };

        $scope.plotDataAcf = function (value) {
            var model = $scope.summary[value[0] + '_model'];
            var data = model.data_acf;
            var clim = model.data_acf_clim;
            var series_data = [];

            for (var i = 0; i < data.length; i++) {
                series_data.push([i, data[i]]);
            }
            $scope.chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'plot-' + value[0] + '-data-acf',
                    animation: false,
                    type: 'column'
                },
                title: {
                    text: value[1] + ' ACF'
                },
                subtitle : {
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
                    },{
                        color: 'blue',
                        width: 1,
                        value: -clim,
                        dashStyle: 'dash'
                    }],
                },
                xAxis: {
                    title: {
                        text: 'Lag'
                    },
                    allowDecimals: false
                },
                series: [{
                    data: series_data,
                    tooltip: {
                        valueDecimals: 3
                    },
                    animation: false
                }]
            });

        };

        $scope.plotDataPacf = function (value) {
            var model = $scope.summary[value[0] + '_model'];
            var data = model.data_pacf;
            var clim = model.data_pacf_clim;
            var series_data = [];

            for (var i = 0; i < data.length; i++) {
                series_data.push([i + 1, data[i]]);
            }
            $scope.chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'plot-' + value[0] + '-data-pacf',
                    animation: false,
                    type: 'column'
                },
                title: {
                    text: value[1] + ' PACF'
                },
                subtitle : {
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
                    },{
                        color: 'blue',
                        width: 1,
                        value: -clim,
                        dashStyle: 'dash'
                    }],
                },
                xAxis: {
                    title: {
                        text: 'Lag'
                    },
                    allowDecimals: false
                },
                series: [{
                    data: series_data,
                    tooltip: {
                        valueDecimals: 3
                    },
                    animation: false
                }]
            });

        };

        $scope.plotResidualsQq = function (value) {
            var data = $scope.summary[value[0] + '_model'].qqplot_data;
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
                    renderTo: 'plot-' + value[0] + '-residuals-qq',
                    animation: false
                },
                tooltip : {
                    formatter: function() {
                        return '<span style="color:'+ this.color +'">\u25CF</span> ' +
                            this.series.name + '<br/>x: <b>' + this.x.toFixed(3) +'</b>'+
                            '<br/>y: <b>' + this.y.toFixed(3) + '</b>';
                    }
                },
                title: {
                    text: value[1] + ' normal Q-Q plot'
                },
                subtitle : {
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
