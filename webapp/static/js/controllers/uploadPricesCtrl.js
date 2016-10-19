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
                        valueDecimals: 3
                    }
                });
            });

            $('#prices-upload-chart-container').empty();
            $scope.chart = new Highcharts.StockChart({
                chart: {
                    renderTo: 'prices-upload-chart-container',
                    animation: false
                },
                rangeSelector: {
                    inputDateFormat: '%b %e, %Y %H:%M',
                    inputEditDateFormat: '%Y-%m-%d %H:%M',
                    inputBoxWidth: 150,
                },
                tooltip: {
                    xDateFormat: '%b %e, %Y, %H:%M'
                },
                credits: {
                    enabled: false
                },
                yAxis: yAxis,
                series: series
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

        $scope.uploadPrices = function () {
            marketService.uploadPrices(entity.id, $scope.fileFormat, $scope.priceFile)
                .then(function (response) {
                        alertify.notify('Uploading of prices is successful!', 'success', 5);
                    },
                    function (error) {
                        alertify.error(error);
                    });

        };

    }

]);
