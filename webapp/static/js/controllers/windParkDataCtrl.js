/*global app,$SCRIPT_ROOT,alertify*/

app.controller('WindParkDataCtrl', ['$scope', '$http', '$uibModalInstance', 'entity',
    function ($scope, $http, $uibModalInstance, entity) {
        'use strict';

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $scope.windParkName = entity.name;

        $scope.update = function () {
            $http.get($SCRIPT_ROOT + '/windparks/summary/' + entity.id)
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

        $scope.plotGeneration = function (value) {
            $http.get($SCRIPT_ROOT + '/windparks/generation/' + entity.id)
                .then(function (response) {
                        if ('error' in response.data) {
                            alertify.error(response.data.error);
                        } else {
                            $scope.chart = new Highcharts.StockChart({
                                chart: {
                                    renderTo: 'plot-generation',
                                    animation: false
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

        $scope.cleanGenerationPlot = function () {
            $('#plot-generation').empty();
        };


    }]);
