/*global app,$SCRIPT_ROOT,alertify*/

app.factory('locationService', ['$http', function ($http) {
    'use strict';
    var locationList = [];

    var reload = function () {
        return $http.get($SCRIPT_ROOT + '/locations')
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        locationList = response.data.data;
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };


    var updateHistory = function (locationId) {
        return $http.post($SCRIPT_ROOT + '/locations/' + locationId + '/update_history')
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

    var updateForecast = function (locationId) {
        return $http.post($SCRIPT_ROOT + '/locations/' + locationId + '/update_forecast')
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

    var deleteLocation = function (id) {
        return $http.delete($SCRIPT_ROOT + '/locations/' + id)
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

    var updateLocation = function (values) {
        return $http({
            url: $SCRIPT_ROOT + '/locations',
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

    var getLocations = function () {
        return locationList;
    };

    var geoLookup = function (query) {
        return $http({
            url: $SCRIPT_ROOT + '/locations/geolookup',
            method: "GET",
            params: {query: query}
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

    var getHistory = function (id) {
        return $http.get($SCRIPT_ROOT + '/locations/' + id + '/history')
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

    var getForecast = function (id) {
        return $http.get($SCRIPT_ROOT + '/locations/' + id + '/forecast')
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

    var fitWindDistribution = function (id) {
        return $http.post($SCRIPT_ROOT + '/locations/' + id + '/wspd_distr')
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

    var getErrorsChunked = function (id) {
        return $http.get($SCRIPT_ROOT + '/locations/' + id + '/errors_chunked')
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

    var getErrorsMerged = function (id) {
        return $http.get($SCRIPT_ROOT + '/locations/' + id + '/errors_merged')
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

    var fitErrorModel = function (id) {
        return $http.post($SCRIPT_ROOT + '/locations/' + id + '/fit_error_model')
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

    var getModelData = function (id) {
        return $http.get($SCRIPT_ROOT + '/locations/' + id + '/model_data')
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
        updateHistory: updateHistory,
        updateForecast: updateForecast,
        deleteLocation: deleteLocation,
        getLocations: getLocations,
        updateLocation: updateLocation,
        geoLookup: geoLookup,
        getHistory: getHistory,
        getForecast: getForecast,
        fitWindDistribution: fitWindDistribution,
        getErrorsChunked: getErrorsChunked,
        getErrorsMerged: getErrorsMerged,
        fitErrorModel: fitErrorModel,
        getModelData: getModelData
    };

}]);
