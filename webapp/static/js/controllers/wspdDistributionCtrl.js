/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('WspdDistributionCtrl', ['$scope', '$http', '$q', '$uibModalInstance', '$rootScope', 'entity',
    function ($scope, $http, $q, $uibModalInstance, $rootScope, entity) {
        'use strict';

        var locationId = entity.id;
        $scope.locationName = entity.name;

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $http.post($SCRIPT_ROOT + '/locations/' + locationId + '/wspd_distr')
            .then(function (response) {
                    if ('error' in response.data) {
                        alertify.error('Error while fitting wind speed model for location "' + $scope.locationName +
                            '": ' + response.data.error);
                    } else {
                        $rootScope.$broadcast('updateLocations');
                        $('#wspd-distr-container').empty();
                        $scope.chart = new Highcharts.Chart({
                            chart: {
                                renderTo: 'wspd-distr-container',
                                animation: false
                            },
                            title: {
                                text: 'shape=' + Highcharts.numberFormat(response.data.data[0], 2) +
                                ', scale=' + Highcharts.numberFormat(response.data.data[1], 2) + ' km/h'
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
                                data: response.data.data[2],
                                type: 'column',
                                animation: false
                            }, {
                                name: 'Fitted Weibull distribution',
                                data: response.data.data[3],
                                type: 'spline',
                                animation: false
                            }]
                        });
                    }
                },
                function (error) {
                    alertify.error('Error while fitting wind speed model for location "' + $scope.locationName +
                        '": ' + error.statusText);
                });

    }
]);
