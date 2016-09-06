/*global app,$SCRIPT_ROOT,alertify*/

app.factory('windparkService', ['$http', 'Upload', function ($http, Upload) {
    'use strict';
    var windparkList = [];

    var reload = function () {
        return $http.get($SCRIPT_ROOT + '/windparks')
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        windparkList = response.data.data;
                        return windparkList;
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };


    var deleteWindpark = function (id) {
        return $http.delete($SCRIPT_ROOT + '/windparks/' + id)
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return reload();
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    var updateWindpark = function (values) {
        return $http({
            url: $SCRIPT_ROOT + '/windparks',
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify(values)
        })
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return reload();
                    }
                },
                function (error) {
                    throw error.statusText;
                });

    };

    var getWindparks = function () {
        return windparkList;
    };

    var previewGeneration = function (format, file) {
        return Upload.upload({
                url: $SCRIPT_ROOT + '/windparks/preview_generation',
                data: {format: format, file: file}
            })
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return response.data.data;
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    var uploadGeneration = function (id, format, file) {
        return Upload.upload({
                url: $SCRIPT_ROOT + '/windparks/generation',
                data: {format: format, file: file, wpark_id: id}
            })
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    var getSummary = function (id) {
        return $http.get($SCRIPT_ROOT + '/windparks/summary/' + id)
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return response.data.data;
                    }
                },
                function (error) {
                    throw error.statusText;
                });

    };

    var getGeneration = function (id) {
        return $http.get($SCRIPT_ROOT + '/windparks/generation/' + id)
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return response.data.data;
                    }
                },
                function (error) {
                    throw error.statusText;
                });

    };

    var getWindVsPower = function (id) {
        return $http.get($SCRIPT_ROOT + '/windparks/windvspower/' + id)
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return response.data.data;
                    }
                },
                function (error) {
                    throw error.statusText;
                });

    };

    var addTurbine = function (windparkId, turbineId, count) {
        return $http({
            url: $SCRIPT_ROOT + '/windparks/' + windparkId + '/turbines',
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify({
                turbine_id: turbineId,
                count: count
            })
        })
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return reload();
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    var deleteTurbine = function (windparkId, relationId) {
        return $http.delete($SCRIPT_ROOT + '/windparks/' + windparkId + '/turbines/' + relationId)
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return reload();
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    var getTotalPowerCurve = function (windparkId) {
        return $http.get($SCRIPT_ROOT + '/windparks/' + windparkId + '/totalpowercurve')
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return response.data.data;
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    var getWindSimulation = function (id, timeSpan, nScenarios, nReducedScenarios, nDaAmScenarios,
                                      nDaAmReducedScenarios) {
        return $http.get($SCRIPT_ROOT + '/windparks/wind_simulation/' + id,
            {
                params: {
                    time_span: timeSpan,
                    n_scenarios: nScenarios,
                    n_reduced_scenarios: nReducedScenarios,
                    n_da_am_scenarios: nDaAmScenarios,
                    n_da_am_reduced_scenarios: nDaAmReducedScenarios
                }
            })
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return response.data.data;
                    }
                },
                function (error) {
                    throw error.statusText;
                });

    };

    var getMarketSimulation = function (id, dayStart, timeSpan, nDaPriceScenarios, nDaRedcPriceScenarios,
                                        nDaAmPriceScenarios, nDaAmRedcPriceScenarios,
                                        nAdjPriceScenarios, nAdjRedcPriceScenarios) {
        return $http.get($SCRIPT_ROOT + '/windparks/market_simulation/' + id,
            {
                params: {
                    day_start: dayStart,
                    time_span: timeSpan,
                    n_da_price_scenarios: nDaPriceScenarios,
                    n_da_redc_price_scenarios: nDaRedcPriceScenarios,
                    n_da_am_price_scenarios: nDaAmPriceScenarios,
                    n_da_am_redc_price_scenarios: nDaAmRedcPriceScenarios,
                    n_adj_price_scenarios: nAdjPriceScenarios,
                    n_adj_redc_price_scenarios: nAdjRedcPriceScenarios
                }
            })
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return response.data.data;
                    }
                },
                function (error) {
                    throw error.statusText;
                });

    };

    var startOptimization = function (windparkId, jobParameters) {
        return $http.post($SCRIPT_ROOT + '/windparks/' + windparkId + '/start_optimization', jobParameters)
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return response.data.data;
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    var optimizationStatus = function (windparkId) {
        return $http.get($SCRIPT_ROOT + '/windparks/' + windparkId + '/optimization_status')
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return response.data.data;
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    var optimizationResults = function (windparkId) {
        return $http.get($SCRIPT_ROOT + '/windparks/' + windparkId + '/optimization_results')
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return response.data.data;
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    var terminateOptimization = function (windparkId) {
        return $http.post($SCRIPT_ROOT + '/windparks/' + windparkId + '/terminate_optimization')
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return response.data.data;
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    var downloadOptRes = function (windparkId) {
        location.href = $SCRIPT_ROOT + '/windparks/' + windparkId + '/optres_zip';
    };

    var getDaOfferingCurve = function (windparkId, hour) {
        return $http.get($SCRIPT_ROOT + '/windparks/' + windparkId + '/offering_curve',
            {
                params: {
                    hour: hour
                }
            })
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return response.data.data;
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    var checkRecentPrices = function (windparkId, jobParameters) {
        return $http.post($SCRIPT_ROOT + '/windparks/' + windparkId + '/check_recent_prices', jobParameters)
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        return response.data.data;
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    return {
        reload: reload,
        deleteWindpark: deleteWindpark,
        getWindparks: getWindparks,
        updateWindpark: updateWindpark,
        previewGeneration: previewGeneration,
        uploadGeneration: uploadGeneration,
        getSummary: getSummary,
        getGeneration: getGeneration,
        getWindVsPower: getWindVsPower,
        addTurbine: addTurbine,
        deleteTurbine: deleteTurbine,
        getTotalPowerCurve: getTotalPowerCurve,
        getWindSimulation: getWindSimulation,
        getMarketSimulation: getMarketSimulation,
        startOptimization: startOptimization,
        optimizationStatus: optimizationStatus,
        optimizationResults: optimizationResults,
        terminateOptimization: terminateOptimization,
        downloadOptRes: downloadOptRes,
        getDaOfferingCurve: getDaOfferingCurve,
        checkRecentPrices: checkRecentPrices
    };

}]);
