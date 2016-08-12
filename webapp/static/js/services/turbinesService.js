/*global app,$SCRIPT_ROOT,alertify*/

app.factory('turbineService', ['$http', function ($http) {
    'use strict';
    var turbineList = [];

    var reload = function () {
        return $http.get($SCRIPT_ROOT + '/turbines')
            .then(function (response) {
                    if ('error' in response.data) {
                        throw response.data.error;
                    } else {
                        turbineList = response.data.data;
                        return turbineList;
                    }
                },
                function (error) {
                    throw error.statusText;
                });
    };

    var getTurbines = function () {
        return turbineList;
    };

    var getPowerCurve = function (id) {
        return $http.get($SCRIPT_ROOT + '/turbines/' + id + '/powercurve')
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
        getTurbines: getTurbines,
        getPowerCurve: getPowerCurve
    };

}]);
