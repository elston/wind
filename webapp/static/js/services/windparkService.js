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
        deleteTurbine: deleteTurbine
    };

}]);
