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
