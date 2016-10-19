/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('UploadGenerationCtrl', ['$scope', '$uibModalInstance', 'entity', 'windparkService',
    function ($scope, $uibModalInstance, entity, windparkService) {
        'use strict';

        $scope.marketName = entity.name;

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $scope.previewFile = function (generationFile) {
            windparkService.previewGeneration($scope.fileFormat, generationFile)
                .then(function (result) {
                        $scope.showGeneration(result);
                    },
                    function (error) {
                        alertify.error(error);
                    });

        };

        $scope.showGeneration = function (data) {

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

            $('#generation-upload-chart-container').empty();
            $scope.chart = new Highcharts.StockChart({
                chart: {
                    renderTo: 'generation-upload-chart-container',
                    animation: false
                },
                rangeSelector: {
                    inputDateFormat: '%b %e, %Y %H:%M',
                    inputEditDateFormat: '%Y-%m-%d %H:%M',
                    inputBoxWidth: 150,
                    inputDateParser: function (value) {
                        return new Date(new Date(value).setUTCHours(0,0,0,0)).setUTCDate(new Date(value).getDate());
                    }
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

        $scope.uploadGeneration = function () {
            windparkService.uploadGeneration(entity.id, $scope.fileFormat, $scope.generationFile)
                .then(function () {
                        alertify.notify('Uploading of generation is successful!', 'success', 5);
                    },
                    function (error) {
                        alertify.error(error);
                    });

        };

    }

]);
