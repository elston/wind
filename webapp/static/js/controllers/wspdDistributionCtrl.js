/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('WspdDistributionCtrl', ['$scope', '$uibModalInstance', '$rootScope', 'entity', 'locationService',
    function ($scope, $uibModalInstance, $rootScope, entity, locationService) {
        'use strict';

        var locationId = entity.id;
        $scope.locationName = entity.name;

        $scope.close = function () {
            $uibModalInstance.close();
        };

        locationService.fitWindDistribution(locationId)
            .then(function (result) {
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
                            animation: false
                        }, {
                            name: 'Fitted Weibull distribution',
                            data: result[3],
                            type: 'spline',
                            animation: false
                        }]
                    });
                },
                function (error) {
                    alertify.error('Error while fitting wind speed model for location "' + $scope.locationName +
                        '": ' + error);
                });

    }
]);
