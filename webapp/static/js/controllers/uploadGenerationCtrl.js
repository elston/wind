/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('UploadGenerationCtrl', ['$scope', '$uibModalInstance', 'Upload', 'entity',
    function ($scope, $uibModalInstance, Upload, entity) {
        'use strict';

        $scope.marketName = entity.name;

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $scope.previewFile = function (generationFile) {
            Upload.upload({
                    url: $SCRIPT_ROOT + '/windparks/preview_generation',
                    data: {format: $scope.fileFormat, file: generationFile}
                })
                .then(function (response) {
                        if ('error' in response.data) {
                            alertify.error(response.data.error);
                        } else {
                            $scope.showGeneration(response.data.data);
                        }
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
            Upload.upload({
                    url: $SCRIPT_ROOT + '/windparks/generation',
                    data: {format: $scope.fileFormat, file: $scope.generationFile, wpark_id: entity.id}
                })
                .then(function (response) {
                        if ('error' in response.data) {
                            alertify.error(response.data.error);
                        } else {
                            alertify.alert('Generation upload', 'Done');
                        }
                    },
                    function (error) {
                        alertify.error(error);
                    });

        };

    }

]);
