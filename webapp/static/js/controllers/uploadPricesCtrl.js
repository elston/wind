/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('UploadPricesCtrl', ['$scope', '$http', '$q', '$uibModalInstance', 'Upload', 'entity',
    function ($scope, $http, $q, $uibModalInstance, Upload, entity) {
        'use strict';

        $scope.marketName = entity.name;

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $scope.previewFile = function (priceFile) {
            Upload.upload({
                    url: $SCRIPT_ROOT + '/markets/preview_prices',
                    data: {format: $scope.fileFormat, file: priceFile},
                })
                .then(function (response) {
                        if ('error' in response.data) {
                            alertify.error(response.data.error);
                        } else {
                            $scope.showPrices(response.data.data);
                        }
                    },
                    function (error) {
                        alertify.error(error);
                    });

        };

        $scope.showPrices = function (data) {

            var yAxis = [];
            var series = [];

            $.each(data, function (key, value) {
                yAxis.push({title: {text: key}});
                series.push({
                    name: key,
                    data: value,
                    yAxis: yAxis.length - 1,
                    animation: false,
                    tooltip: {
                        valueDecimals: 2
                    }
                });
            });

            $('#prices-upload-chart-container').empty();
            $scope.chart = new Highcharts.StockChart({
                chart: {
                    renderTo: 'prices-upload-chart-container',
                    animation: false
                },
                tooltip: {
                    xDateFormat: '%b %e, %Y, %H:%M'
                },
                credits: {
                    enabled: false
                },
                yAxis: yAxis,
                series: series
            });
        };

        $scope.uploadPrices = function () {
            Upload.upload({
                    url: $SCRIPT_ROOT + '/markets/prices',
                    data: {format: $scope.fileFormat, file: $scope.priceFile, mkt_id: entity.id},
                })
                .then(function (response) {
                        if ('error' in response.data) {
                            alertify.error(response.data.error);
                        } else {
                            alertify.alert('Prices upload', 'Done');
                        }
                    },
                    function (error) {
                        alertify.error(error);
                    });

        };

    }

]);
