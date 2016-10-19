/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('WindparkGenerationCtrl', ['$scope', 'windparkService',
    function ($scope, windparkService) {
        'use strict';

        windparkService.getSummary($scope.windpark.id)
            .then(function (result) {
                    $scope.summary = result;
                },
                function (error) {
                    alertify.error(error);
                });

        $scope.plotGeneration = function () {
            windparkService.getGeneration($scope.windpark.id)
                .then(function (result) {
                        $scope.chart = new Highcharts.StockChart({
                            chart: {
                                renderTo: 'plot-generation',
                                animation: false
                            },
                            rangeSelector: {
                                inputDateFormat: '%b %e, %Y',
                                inputEditDateFormat: '%Y-%m-%d',
                                inputDateParser: function (value) {
                                    return new Date(new Date(value).setUTCHours(0,0,0,0)).setUTCDate(new Date(value).getDate());
                                }
                            },
                            title: {
                                text: 'Generation'
                            },
                            credits: {
                                enabled: false
                            },
                            yAxis: [{
                                title: {
                                    text: 'Power, MW'
                                }
                            },
                                {
                                    title: {
                                        text: 'Wind speed, km/h'
                                    }
                                }],
                            series: [{
                                name: 'Generation, MW',
                                data: result.power,
                                animation: false,
                                tooltip: {
                                    valueDecimals: 3
                                }
                            },
                                {
                                    name: 'Wind speed, km/h',
                                    data: result.wind,
                                    animation: false,
                                    yAxis: 1,
                                    tooltip: {
                                        valueDecimals: 1
                                    }
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
                        alertify.error(error.statusText);
                    });
        };

        $scope.cleanGenerationPlot = function () {
            $('#plot-generation').empty();
        };

        $scope.plotWindVsPower = function () {
            windparkService.getWindVsPower($scope.windpark.id)
                .then(function (result) {
                        $scope.beta = result.beta;
                        $scope.sd_beta = result.sd_beta;
                        $scope.chart = new Highcharts.Chart({
                            chart: {
                                zoomType: 'xy',
                                renderTo: 'plot-wind-vs-power',
                                animation: false
                            },
                            title: {
                                text: 'Wind vs Power'
                            },
                            credits: {
                                enabled: false
                            },
                            yAxis: [{
                                title: {
                                    text: 'Power, MW'
                                }
                            }],
                            xAxis: [{
                                title: {
                                    text: 'Wind speed, km/h'
                                }
                            }],
                            series: [{
                                type: 'scatter',
                                name: 'Wind vs Power',
                                data: result.scatterplot,
                                animation: false,
                                tooltip: {
                                    valueDecimals: 3
                                },
                                color: 'rgba(119, 152, 191, .5)'
                            },
                                {
                                    type: 'line',
                                    name: 'Wind vs Power model',
                                    data: result.model,
                                    animation: false,
                                    tooltip: {
                                        valueDecimals: 3
                                    }
                                }]
                        });
                    },
                    function (error) {
                        alertify.error(error);
                        $scope.summary.showWindVsPower = false;
                    });
        };

        $scope.cleanWindVsPowerPlot = function () {
            $('#plot-wind-vs-power').empty();
        };


    }]);
