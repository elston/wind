/*global app,$SCRIPT_ROOT,alertify*/

app.factory('marketService', ['$http', 'Upload', function ($http, Upload) {
    'use strict';
    var marketList = [];

    var reload = function () {
        return $http.get($SCRIPT_ROOT + '/markets')
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        marketList = response.data.data;
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };


    var deleteMarket = function (id) {
        return $http.delete($SCRIPT_ROOT + '/markets/' + id)
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

    var updateMarket = function (values) {
        return $http({
            url: $SCRIPT_ROOT + '/markets',
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

    var getMarkets = function () {
        return marketList;
    };

    var getSummary = function (id) {
        return $http.get($SCRIPT_ROOT + '/markets/summary/' + id)
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

    var getValues = function (id, valueName) {
        return $http.get($SCRIPT_ROOT + '/markets/prices/' + id + '/' + valueName)
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

    var calculateMissing = function (id) {
        return $http.post($SCRIPT_ROOT + '/markets/prices/calculate_missing/' + id)
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    var fitModel = function (id) {
        return $http.post($SCRIPT_ROOT + '/markets/prices/fit_model/' + id)
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    var previewPrices = function (format, file) {
        return Upload.upload({
                url: $SCRIPT_ROOT + '/markets/preview_prices',
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

    var uploadPrices = function (id, format, file) {
        return Upload.upload({
                url: $SCRIPT_ROOT + '/markets/prices',
                data: {format: format, file: file, mkt_id: id}
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

    return {
        reload: reload,
        deleteMarket: deleteMarket,
        getMarkets: getMarkets,
        updateMarket: updateMarket,
        getSummary: getSummary,
        getValues: getValues,
        calculateMissing: calculateMissing,
        fitModel: fitModel,
        previewPrices: previewPrices,
        uploadPrices: uploadPrices
    };

}]);
