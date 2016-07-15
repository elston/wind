
app.controller('WeatherPlotCtrl', ['$scope', '$http', '$q', '$uibModalInstance', 'entity',
    function ($scope, $http, $q, $uibModalInstance, entity) {

        var locationId = entity.id;
        $scope.locationName = entity.name;

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $q.all([
                $http.get($SCRIPT_ROOT + '/locations/' + locationId + '/history')
                    .then(function (response) {
                            if ('error' in response.data) {
                                alertify.error('Error while getting history for location "' + $scope.locationName +
                                    '": ' + response.data.error);
                            }
                            $scope.history_data = response.data.data
                        },
                        function (error) {
                            alertify.error('Error while getting history for location "' + $scope.locationName +
                                '": ' + error.statusText);
                        }),
                $http.get($SCRIPT_ROOT + '/locations/' + locationId + '/forecast')
                    .then(function (response) {
                            if ('error' in response.data) {
                                alertify.error('Error while getting forecast for location "' + $scope.locationName +
                                    '": ' + response.data.error);
                            }
                            $scope.forecast_data = response.data.data
                        },
                        function (error) {
                            alertify.error('Error while getting history for location "' + $scope.locationName +
                                '": ' + error.statusText);
                        })
            ])
            .then(function () {
                $('#weather-chart-container').empty();
                $('#weather-chart-container').highcharts('StockChart', {
                    rangeSelector: {
                        selected: 1
                    },
                    title: {
                        text: $scope.locationName
                    },
                    tooltip: {
                        xDateFormat: '%b %e, %Y, %H:%M'
                    },
                    credits: {
                        enabled: false
                    },
                    yAxis: [{
                        title: {
                            text: 'Temperature, C'
                        }
                    }, {
                        title: {
                            text: 'Wind speed, km/h'
                        }
                    }, {
                        title: {
                            text: 'Wind direction, degrees'
                        }
                    }],
                    series: [{
                        name: 'Temperature, C',
                        data: $scope.history_data.tempm.concat($scope.forecast_data.tempm),
                        zoneAxis: 'x',
                        zones: [{
                            value: $scope.forecast_data.tempm[0][0]
                        }, {
                            dashStyle: 'dot'
                        }],
                        tooltip: {
                            valueDecimals: 1
                        }
                    }, {
                        name: 'Wind speed, km/h',
                        data: $scope.history_data.wspdm.concat($scope.forecast_data.wspdm),
                        zoneAxis: 'x',
                        zones: [{
                            value: $scope.forecast_data.wspdm[0][0]
                        }, {
                            dashStyle: 'dot'
                        }],
                        tooltip: {
                            valueDecimals: 1
                        },
                        yAxis: 1
                    }, {
                        name: 'Wind direction, degrees',
                        data: $scope.history_data.wdird.concat($scope.forecast_data.wdird),
                        zoneAxis: 'x',
                        zones: [{
                            value: $scope.forecast_data.wdird[0][0]
                        }, {
                            dashStyle: 'dot'
                        }],
                        tooltip: {
                            valueDecimals: 0
                        },
                        yAxis: 2
                    }]
                });
            })

    }
]);
