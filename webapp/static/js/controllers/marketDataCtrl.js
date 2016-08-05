/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('MarketDataCtrl', ['$scope', '$uibModalInstance', 'entity', 'marketService',
    function ($scope, $uibModalInstance, entity, marketService) {
        'use strict';

        $scope.marketName = entity.name;

        $scope.chartsMetadata = [
            ['lambdaD', 'Day ahead prices'],
            ['lambdaA', 'Adjustment market prices'],
            ['MAvsMD', 'Difference between DA and AM prices'],
            ['lambdaPlus', 'Upward imbalance prices (lambdaPlus)'],
            ['lambdaMinus', 'Downward imbalance prices (lambdaMinus)'],
            ['r_pos', 'r+'],
            ['r_neg', 'r-'],
            ['sqrt_r', 'sqrt(r)']
        ];

        $scope.modelsMetadata = [
            ['lambdaD', 'Day ahead prices'],
            ['MAvsMD', 'Difference between DA and AM prices'],
            ['sqrt_r', 'sqrt(r)']
        ];

        $scope.update = function () {
            marketService.getSummary(entity.id)
                .then(function (result) {
                        $scope.summary = result;
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
                                animation: false
                            }]
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
            marketService.fitModel(entity.id)
                .then(function (response) {
                        alertify.success('OK');
                        $scope.update();
                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        $scope.plotPrediction = function (value) {
            $scope.chart = new Highcharts.StockChart({
                chart: {
                    renderTo: 'plot-' + value[0] + '-pred',
                    animation: false
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
                series: [{
                    data: $scope.summary[value[0] + '_model'].pred,
                    animation: false
                },
                    {
                        data: $scope.summary[value[0] + '_model'].pred_se,
                        animation: false
                    }]
            });

        };

        $scope.plotResiduals = function (value) {
            $scope.chart = new Highcharts.StockChart({
                chart: {
                    renderTo: 'plot-' + value[0] + '-residuals',
                    animation: false
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
                series: [{
                    data: $scope.summary[value[0] + '_model'].residuals,
                    animation: false
                }]
            });

        };

    }

]);
