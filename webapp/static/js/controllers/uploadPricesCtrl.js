/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('UploadPricesCtrl', ['$scope', '$uibModalInstance', 'entity', 'marketService',
    function ($scope, $uibModalInstance, entity, marketService) {
        'use strict';

        $scope.marketName = entity.name;

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $scope.previewFile = function (priceFile) {
            marketService.previewPrices($scope.fileFormat, priceFile)
                .then(function (result) {
                        $scope.showPrices(result);
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
            marketService.uploadPrices(entity.id, $scope.fileFormat, $scope.priceFile)
                .then(function (response) {
                        alertify.alert('Prices upload', 'Done');
                    },
                    function (error) {
                        alertify.error(error);
                    });

        };

    }

]);
