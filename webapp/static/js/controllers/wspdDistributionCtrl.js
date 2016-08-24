/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('WspdDistributionCtrl', ['$scope', '$uibModalInstance', '$rootScope', 'entity', 'locationService',
    function ($scope, $uibModalInstance, $rootScope, entity, locationService) {
        'use strict';

        var locationId = entity.id;
        $scope.locationName = entity.name;
        $scope.windModel = null;

        $scope.close = function () {
            $uibModalInstance.close();
        };

        locationService.fitWindDistribution(locationId)
            .then(function (result) {
                    $scope.windModel = result[6];
                    $rootScope.$broadcast('updateLocations');
                    $('#wspd-distr-container').empty();
                    $scope.chart = new Highcharts.Chart({
                        chart: {
                            renderTo: 'wspd-distr-container',
                            animation: false
                        },
                        title: {
                            text: 'shape=' + Highcharts.numberFormat(result[0], 2) +
                            ', scale=' + Highcharts.numberFormat(result[1], 2) + ' km/h'
                        },
                        credits: {
                            enabled: false
                        },
                        yAxis: [{
                            title: {
                                text: 'pdf'
                            }
                        }],
                        xAxis: [{
                            title: {
                                text: 'Wind speed, km/h'
                            }
                        },
                            {
                                title: {
                                    text: 'Normalized value'
                                }
                            }],
                        tooltip: {
                            formatter: function () {
                                var s = '<b>' + Highcharts.numberFormat(this.x, 2) + ' km/h</b>';
                                $.each(this.points, function () {
                                    s += '<br/>' + this.series.name + ': ' +
                                        Highcharts.numberFormat(this.y, 2);
                                });
                                return s;
                            },
                            shared: true
                        },
                        series: [{
                            name: 'Actual histogram',
                            data: result[2],
                            type: 'column',
                            animation: false,
                            xAxis: 0
                        }, {
                            name: 'Fitted Weibull distribution',
                            data: result[3],
                            type: 'spline',
                            animation: false,
                            xAxis: 0
                        }, {
                            name: 'Normalized values histogram',
                            data: result[4],
                            type: 'column',
                            animation: false,
                            xAxis: 1,
                            color: 'rgba(144, 237, 125, 0.8)'
                        }, {
                            name: 'Desired normal distribution',
                            data: result[5],
                            type: 'spline',
                            animation: false,
                            xAxis: 1
                        }]
                    });
                },
                function (error) {
                    alertify.error('Error while fitting wind speed model for location "' + $scope.locationName +
                        '": ' + error);
                });

    }
]);
