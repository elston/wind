/*global app,$SCRIPT_ROOT,alertify,Highcharts*/

app.controller('WindParkSimulationCtrl', ['$scope', '$timeout', 'windparkService',
    function ($scope, $timeout, windparkService) {
        'use strict';

        $scope.status = {isDetailsOpen: false};
        $scope.simulationDate = new Date();
        $scope.timeSpan = 24;
        $scope.nScenarios = 15;
        $scope.nReducedScenarios = 5;
        $scope.nDaAmScenarios = 15;
        $scope.nDaAmReducedScenarios = 2;
        $scope.dayStart = 0;

        $scope.nDaPriceScenarios = 100;
        $scope.nDaAmPriceScenarios = 100;
        $scope.nAdjPriceScenarios = 100;
        $scope.nDaRedcPriceScenarios = 5;
        $scope.nDaAmRedcPriceScenarios = 5;
        $scope.nAdjRedcPriceScenarios = 5;

        if ($scope.location.forecast_error_model)
            $scope.forecastErrorVariance = $scope.location.forecast_error_model.sigma2;

        $scope.showDetails = function () {
        };

        /* accepts parameters
         * h  Object = {h:x, s:y, v:z}
         * OR
         * h, s, v
         */
        var HSVtoRGB = function (h, s, v) {
            var r, g, b, i, f, p, q, t;
            if (arguments.length === 1) {
                s = h.s;
                v = h.v;
                h = h.h;
            }
            i = Math.floor(h * 6);
            f = h * 6 - i;
            p = v * (1 - s);
            q = v * (1 - f * s);
            t = v * (1 - (1 - f) * s);
            switch (i % 6) {
                case 0:
                    r = v;
                    g = t;
                    b = p;
                    break;
                case 1:
                    r = q;
                    g = v;
                    b = p;
                    break;
                case 2:
                    r = p;
                    g = v;
                    b = t;
                    break;
                case 3:
                    r = p;
                    g = q;
                    b = v;
                    break;
                case 4:
                    r = t;
                    g = p;
                    b = v;
                    break;
                case 5:
                    r = v;
                    g = p;
                    b = q;
                    break;
            }
            return {
                r: Math.round(r * 255),
                g: Math.round(g * 255),
                b: Math.round(b * 255)
            };
        };

        $scope.overrideVariance = false;

        $scope.overrideVarianceChanged = function () {
            if (!$scope.overrideVariance) {
                $scope.forecastErrorVariance = $scope.location.forecast_error_model.sigma2;
            }
        };

        $scope.updateWindSimulation = function () {
            windparkService.getWindSimulation($scope.windpark.id, $scope.simulationDate, $scope.nScenarios,
                $scope.nReducedScenarios, $scope.nDaAmScenarios, $scope.nDaAmReducedScenarios,
                $scope.forecastErrorVariance)
                .then(function (data) {
                        var wind_series = [];
                        data.wind_speed.forEach(function (sample) {
                            wind_series.push({
                                data: sample,
                                tooltip: {
                                    valueDecimals: 3
                                }
                            });
                        });

                        wind_series.push({
                            data: data.forecasted_wind,
                            tooltip: {
                                valueDecimals: 3
                            },
                            color: 'rgba(255, 0, 0, 1)'
                        });

                        var power_series = [];
                        data.power.forEach(function (sample) {
                            power_series.push({
                                data: sample,
                                tooltip: {
                                    valueDecimals: 3
                                }
                            });
                        });

                        power_series.push({
                            data: data.forecasted_power,
                            tooltip: {
                                valueDecimals: 3
                            },
                            color: 'rgba(255, 0, 0, 1)'
                        });

                        var max_p, min_p, p, h, alpha, color;

                        var red_wind_series = [];
                        max_p = Math.max.apply(null, data.wind_probs);
                        min_p = Math.min.apply(null, data.wind_probs);
                        for (var i = 0; i < data.reduced_wind_speed.length; i++) {
                            p = data.wind_probs[i];
                            h = (max_p - p) / (max_p - min_p) * 0.66;
                            alpha = 0.3 + (p - min_p) / (max_p - min_p) * 0.6;
                            color = HSVtoRGB(h, 1, 1);
                            red_wind_series.push({
                                data: data.reduced_wind_speed[i],
                                tooltip: {
                                    valueDecimals: 3
                                },
                                name: p.toFixed(2),
                                color: 'rgba(' + color.r + ',' + color.g + ',' + color.b + ',' + alpha + ')'
                            });
                        }

                        var red_power_series = [];
                        max_p = Math.max.apply(null, data.power_probs);
                        min_p = Math.min.apply(null, data.power_probs);
                        for (i = 0; i < data.reduced_power.length; i++) {
                            p = data.power_probs[i];
                            h = (max_p - p) / (max_p - min_p) * 0.66;
                            alpha = 0.3 + (p - min_p) / (max_p - min_p) * 0.6;
                            color = HSVtoRGB(h, 1, 1);
                            red_power_series.push({
                                data: data.reduced_power[i],
                                tooltip: {
                                    valueDecimals: 3
                                },
                                name: p.toFixed(2),
                                color: 'rgba(' + color.r + ',' + color.g + ',' + color.b + ',' + alpha + ')'
                            });
                        }

                        $timeout(function () {
                            $scope.chart1 = new Highcharts.Chart({
                                chart: {
                                    renderTo: 'wind-sim',
                                    animation: false
                                },
                                title: {
                                    text: 'Wind simulation'
                                },
                                credits: {
                                    enabled: false
                                },
                                legend: {
                                    enabled: false
                                },
                                plotOptions: {
                                    line: {
                                        animation: false,
                                        marker: {
                                            enabled: false
                                        },
                                        color: 'rgba(119, 152, 191, .5)'
                                    }
                                },
                                yAxis: [{
                                    title: {
                                        text: 'Wind speed, m/s'
                                    }
                                }],
                                xAxis: {
                                    type: 'datetime',
                                    title: {
                                        text: 'Time (' + data.tzinfo + ')'
                                    }
                                },
                                series: wind_series
                            });

                            $scope.chart2 = new Highcharts.Chart({
                                chart: {
                                    renderTo: 'power-sim',
                                    animation: false
                                },
                                title: {
                                    text: 'Power simulation'
                                },
                                credits: {
                                    enabled: false
                                },
                                legend: {
                                    enabled: false
                                },
                                plotOptions: {
                                    line: {
                                        animation: false,
                                        marker: {
                                            enabled: false
                                        },
                                        color: 'rgba(0, 0, 0, .5)'
                                    }
                                },
                                yAxis: [{
                                    title: {
                                        text: 'Power, MW'
                                    }
                                }],
                                xAxis: {
                                    type: 'datetime',
                                    title: {
                                        text: 'Time (' + data.tzinfo + ')'
                                    }
                                },
                                series: power_series
                            });

                            $scope.chart3 = new Highcharts.Chart({
                                chart: {
                                    renderTo: 'wind-red-sim',
                                    animation: false
                                },
                                title: {
                                    text: 'Wind simulation (reduced scenarios)'
                                },
                                credits: {
                                    enabled: false
                                },
                                plotOptions: {
                                    line: {
                                        animation: false,
                                        marker: {
                                            enabled: false
                                        }
                                    }
                                },
                                yAxis: [{
                                    title: {
                                        text: 'Wind speed, m/s'
                                    }
                                }],
                                xAxis: {
                                    type: 'datetime',
                                    title: {
                                        text: 'Time (' + data.tzinfo + ')'
                                    }
                                },
                                series: red_wind_series
                            });

                            $scope.chart4 = new Highcharts.Chart({
                                chart: {
                                    renderTo: 'power-red-sim',
                                    animation: false
                                },
                                title: {
                                    text: 'Power simulation (reduced scenarios)'
                                },
                                credits: {
                                    enabled: false
                                },
                                plotOptions: {
                                    line: {
                                        animation: false,
                                        marker: {
                                            enabled: false
                                        }
                                    }
                                },
                                yAxis: [{
                                    title: {
                                        text: 'Power, MW'
                                    }
                                }],
                                xAxis: {
                                    type: 'datetime',
                                    title: {
                                        text: 'Time (' + data.tzinfo + ')'
                                    }
                                },
                                series: red_power_series
                            });

                        });

                    },
                    function (error) {
                        alertify.error(error);
                    });
        };

        $scope.updateMarketSimulation = function () {
            windparkService.getMarketSimulation($scope.windpark.id, $scope.simulationDate,
                $scope.nDaPriceScenarios, $scope.nDaRedcPriceScenarios,
                $scope.nDaAmPriceScenarios, $scope.nDaAmRedcPriceScenarios,
                $scope.nAdjPriceScenarios, $scope.nAdjRedcPriceScenarios)
                .then(function (data) {
                        var lambdaD_series = [];
                        data.lambdaD.forEach(function (sample) {
                            lambdaD_series.push({
                                data: sample,
                                tooltip: {
                                    valueDecimals: 3
                                }
                            });
                        });

                        var MAvsMD_series = [];
                        data.MAvsMD.forEach(function (sample) {
                            MAvsMD_series.push({
                                data: sample,
                                tooltip: {
                                    valueDecimals: 3
                                }
                            });
                        });

                        var sqrt_r_series = [];
                        data.sqrt_r.forEach(function (sample) {
                            sqrt_r_series.push({
                                data: sample,
                                tooltip: {
                                    valueDecimals: 3
                                }
                            });
                        });

                        var max_p, min_p, p, h, alpha, color;

                        var red_lambdaD_series = [];
                        max_p = Math.max.apply(null, data.lambdaD_probs);
                        min_p = Math.min.apply(null, data.lambdaD_probs);
                        for (var i = 0; i < data.reduced_lambdaD.length; i++) {
                            p = data.lambdaD_probs[i];
                            h = (max_p - p) / (max_p - min_p) * 0.66;
                            alpha = 0.3 + (p - min_p) / (max_p - min_p) * 0.6;
                            color = HSVtoRGB(h, 1, 1);
                            red_lambdaD_series.push({
                                data: data.reduced_lambdaD[i],
                                tooltip: {
                                    valueDecimals: 3
                                },
                                name: p.toFixed(2),
                                color: 'rgba(' + color.r + ',' + color.g + ',' + color.b + ',' + alpha + ')'
                            });
                        }

                        var red_MAvsMD_series = [];
                        max_p = Math.max.apply(null, data.MAvsMD_probs);
                        min_p = Math.min.apply(null, data.MAvsMD_probs);
                        for (i = 0; i < data.reduced_MAvsMD.length; i++) {
                            p = data.MAvsMD_probs[i];
                            h = (max_p - p) / (max_p - min_p) * 0.66;
                            alpha = 0.3 + (p - min_p) / (max_p - min_p) * 0.6;
                            color = HSVtoRGB(h, 1, 1);
                            red_MAvsMD_series.push({
                                data: data.reduced_MAvsMD[i],
                                tooltip: {
                                    valueDecimals: 3
                                },
                                name: p.toFixed(2),
                                color: 'rgba(' + color.r + ',' + color.g + ',' + color.b + ',' + alpha + ')'
                            });
                        }

                        var red_sqrt_r_series = [];
                        max_p = Math.max.apply(null, data.sqrt_r_probs);
                        min_p = Math.min.apply(null, data.sqrt_r_probs);
                        for (i = 0; i < data.reduced_sqrt_r.length; i++) {
                            p = data.sqrt_r_probs[i];
                            h = (max_p - p) / (max_p - min_p) * 0.66;
                            alpha = 0.3 + (p - min_p) / (max_p - min_p) * 0.6;
                            color = HSVtoRGB(h, 1, 1);
                            red_sqrt_r_series.push({
                                data: data.reduced_sqrt_r[i],
                                tooltip: {
                                    valueDecimals: 3
                                },
                                name: p.toFixed(2),
                                color: 'rgba(' + color.r + ',' + color.g + ',' + color.b + ',' + alpha + ')'
                            });
                        }


                        $timeout(function () {
                            $scope.chart1 = new Highcharts.Chart({
                                chart: {
                                    renderTo: 'lambdad-sim',
                                    animation: false
                                },
                                title: {
                                    text: 'Day ahead prices'
                                },
                                credits: {
                                    enabled: false
                                },
                                legend: {
                                    enabled: false
                                },
                                plotOptions: {
                                    line: {
                                        animation: false,
                                        marker: {
                                            enabled: false
                                        },
                                        color: 'rgba(119, 152, 191, .5)'
                                    }
                                },
                                yAxis: [{
                                    title: {
                                        text: 'Price'
                                    }
                                }],
                                series: lambdaD_series
                            });

                            $scope.chart2 = new Highcharts.Chart({
                                chart: {
                                    renderTo: 'mavsmd-sim',
                                    animation: false
                                },
                                title: {
                                    text: 'MAvsMD'
                                },
                                credits: {
                                    enabled: false
                                },
                                legend: {
                                    enabled: false
                                },
                                plotOptions: {
                                    line: {
                                        animation: false,
                                        marker: {
                                            enabled: false
                                        },
                                        color: 'rgba(119, 152, 191, .5)'
                                    }
                                },
                                yAxis: [{
                                    title: {
                                        text: 'Price'
                                    }
                                }],
                                series: MAvsMD_series
                            });

                            $scope.chart3 = new Highcharts.Chart({
                                chart: {
                                    renderTo: 'sqrtr-sim',
                                    animation: false
                                },
                                title: {
                                    text: 'sqrt(r)'
                                },
                                credits: {
                                    enabled: false
                                },
                                legend: {
                                    enabled: false
                                },
                                plotOptions: {
                                    line: {
                                        animation: false,
                                        marker: {
                                            enabled: false
                                        },
                                        color: 'rgba(119, 152, 191, .5)'
                                    }
                                },
                                yAxis: [{
                                    title: {
                                        text: 'Price'
                                    }
                                }],
                                series: sqrt_r_series
                            });

                            $scope.chart4 = new Highcharts.Chart({
                                chart: {
                                    renderTo: 'lambdad-red-sim',
                                    animation: false
                                },
                                title: {
                                    text: 'Day ahead prices (reduced scenarios)'
                                },
                                credits: {
                                    enabled: false
                                },
                                plotOptions: {
                                    line: {
                                        animation: false,
                                        marker: {
                                            enabled: false
                                        }
                                    }
                                },
                                yAxis: [{
                                    title: {
                                        text: 'Price'
                                    }
                                }],
                                series: red_lambdaD_series
                            });

                            $scope.chart5 = new Highcharts.Chart({
                                chart: {
                                    renderTo: 'mavsmd-red-sim',
                                    animation: false
                                },
                                title: {
                                    text: 'MAvsMD  (reduced scenarios)'
                                },
                                credits: {
                                    enabled: false
                                },
                                plotOptions: {
                                    line: {
                                        animation: false,
                                        marker: {
                                            enabled: false
                                        }
                                    }
                                },
                                yAxis: [{
                                    title: {
                                        text: 'Price'
                                    }
                                }],
                                series: red_MAvsMD_series
                            });

                            $scope.chart6 = new Highcharts.Chart({
                                chart: {
                                    renderTo: 'sqrtr-red-sim',
                                    animation: false
                                },
                                title: {
                                    text: 'sqrt(r)  (reduced scenarios)'
                                },
                                credits: {
                                    enabled: false
                                },
                                plotOptions: {
                                    line: {
                                        animation: false,
                                        marker: {
                                            enabled: false
                                        }
                                    }
                                },
                                yAxis: [{
                                    title: {
                                        text: 'Price'
                                    }
                                }],
                                series: red_sqrt_r_series
                            });
                        });

                    },
                    function (error) {
                        alertify.error(error);
                    });
        };
    }]);
