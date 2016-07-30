/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('MarketDataCtrl', ['$scope', '$http', '$q', '$uibModalInstance', 'Upload', 'entity',
    function ($scope, $http, $q, $uibModalInstance, Upload, entity) {
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
            $http.get($SCRIPT_ROOT + '/markets/summary/' + entity.id)
                .then(function (response) {
                        if ('error' in response.data) {
                            alertify.error(response.data.error);
                        } else {
                            $scope.summary = response.data.data;
                        }
                    },
                    function (error) {
                        alertify.error(error.statusText);
                    });
        };

        $scope.update();

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $scope.plotValue = function (value) {
            $http.get($SCRIPT_ROOT + '/markets/prices/' + entity.id + '/' + value[0])
                .then(function (response) {
                        if ('error' in response.data) {
                            alertify.error(response.data.error);
                        } else {
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
                                    data: response.data.data,
                                    animation: false
                                }]
                            });
                        }
                    },
                    function (error) {
                        alertify.error(error.statusText);
                    });
        };

        $scope.cleanPlot = function (value) {
            $('plot-value-' + value[0]).empty();
        };

        $scope.calculateMissing = function () {
            $http.post($SCRIPT_ROOT + '/markets/prices/calculate_missing/' + entity.id)
                .then(function (response) {
                        if ('error' in response.data) {
                            alertify.error(response.data.error);
                        } else {
                            alertify.success('OK');
                            $scope.update();
                        }
                    },
                    function (error) {
                        alertify.error(error.statusText);
                    });
        };

        $scope.fitModel = function () {
            $http.post($SCRIPT_ROOT + '/markets/prices/fit_model/' + entity.id)
                .then(function (response) {
                        if ('error' in response.data) {
                            alertify.error(response.data.error);
                        } else {
                            alertify.success('OK');
                            $scope.update();
                        }
                    },
                    function (error) {
                        alertify.error(error.statusText);
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
