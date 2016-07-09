/*global EditableGrid,CellRenderer,alertify,$SCRIPT_ROOT*/

(function () {
    'use strict';

    function initializeGrid(table, tableclass, dataUrl) {
        var grid = new EditableGrid('Users', {
            enableSort: true,
            editmode: 'absolute'
        });

        grid.load({
            metadata: [{
                name: 'email',
                label: 'Name',
                datatype: 'string',
                editable: true
            }, {
                name: 'active',
                label: 'Active',
                datatype: 'boolean',
                editable: true
            }, {
                name: 'admin',
                label: 'Admin',
                datatype: 'boolean',
                editable: true
            }, {
                name: 'action',
                label: ' ',
                datatype: 'html',
                editable: false,
                value: null
            }
            ]
        });

        grid.tableLoaded = function () {
            this.setCellRenderer('action', new CellRenderer({
                render: function (cell, value) {
                    var rowId = grid.getRowId(cell.rowIndex);

                    var button1 = $('<button>').text('Change password')
                        .addClass('btn')
                        .addClass('btn-xs')
                        .addClass('btn-default')
                        .attr('data-toggle', 'modal')
                        .attr('data-target', '#change-password-dialog')
                        .attr('data-whatever', rowId);
                    $(cell).append(button1);

                    var link = $('<a>').html('<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>&nbsp;')
                        .css({
                            cursor: 'pointer'
                        })
                        .attr('data-toggle', 'tooltip')
                        .attr('title', 'Delete row')
                        .tooltip()
                        .click(function (event) {
                            alertify.confirm('Confirm', 'Are you sure you want to delete this user?',
                                function () {
                                    $.ajax({
                                            url: $SCRIPT_ROOT + '/users/' + rowId,
                                            type: 'DELETE'
                                        })
                                        .done(function (data) {
                                            if ('error' in data) {
                                                alertify.error(data.message);
                                            } else {
                                                alertify.success('OK');
                                                grid.loadData();
                                            }
                                        })
                                        .fail(function (xhr, status, error) {
                                            alertify.error(status + ': ' + error);
                                        });
                                },
                                null);
                        });
                    $(cell).append(link);
                }
            }));

            this.renderGrid(table, tableclass);

        };

        grid.loadData = function () {
            this.loadJSON(dataUrl);
        };

        grid.modelChanged = function (rowIndex, columnIndex, oldValue, newValue, row) {
            var id = this.data[rowIndex].id;
            var key = this.columns[columnIndex].name;
            $.ajax({
                    url: $SCRIPT_ROOT + '/users/' + id,
                    type: 'PUT',
                    data: {key: key, value: newValue}
                })
                .done(function (data) {
                    if ('error' in data) {
                        alertify.error(data.error);
                    } else {
                        alertify.success('OK');
                    }
                })
                .fail(function (xhr, status, error) {
                    alertify.error(status + ': ' + error);
                });
        };

        return grid;
    }

    $(document).ready(function () {

        var grid = initializeGrid('users-table', 'table table-bordered', $SCRIPT_ROOT + '/users');

        grid.loadData();

        var changePasswordDialog = $('#change-password-dialog');
        changePasswordDialog.on('show.bs.modal', function (event) {
            var button = $(event.relatedTarget);
            var rowId = button.data('whatever');
            var modal = $(this);
            modal.find('#user-id').val(rowId);
        });

        changePasswordDialog.find('input').keyup(function (event) {
            var pass1 = changePasswordDialog.find('input#pass1').val();
            var pass2 = changePasswordDialog.find('input#pass2').val();
            if (pass1 === pass2 && pass1.length) {
                $('form#change-password-form .form-group').removeClass('has-error');
                changePasswordDialog.find('button#change-password').removeAttr('disabled');
            } else {
                $('form#change-password-form .form-group').addClass('has-error');
                changePasswordDialog.find('button#change-password').attr('disabled', true);
            }
        });

        $('button#change-password').click(function () {
            var id = changePasswordDialog.find('input#user-id').val();
            var password = changePasswordDialog.find('input#pass1').val();
            $.ajax({
                    url: $SCRIPT_ROOT + '/users/' + id,
                    type: 'PUT',
                    data: {key: 'password', value: password}
                })
                .done(function (data) {
                    if ('error' in data) {
                        alertify.error(data.message);
                    } else {
                        alertify.success('OK');
                    }
                })
                .fail(function (xhr, status, error) {
                    alertify.error(status + ': ' + error);
                })
                .always(function () {
                    $('#change-password-dialog').modal('hide');
                });
        });

        $('form#new-user-form input').keyup(function (event) {
            var form = $('form#new-user-form');
            var email = form.find('input#user-email').val();
            var pass1 = form.find('input#user-pass1').val();
            var pass2 = form.find('input#user-pass2').val();
            var allOk = true;
            if (email.length > 0) {
                form.find('#email-group').removeClass('has-error');
            } else {
                form.find('#email-group').addClass('has-error');
                allOk = false;
            }
            if (pass1 === pass2 && pass1.length) {
                form.find('.pass-equal').removeClass('has-error');
            } else {
                form.find('.pass-equal').addClass('has-error');
                allOk = false;
            }
            if (allOk) {
                $('#new-user-dialog').find('button#new-user').removeAttr('disabled');
            } else {
                $('#new-user-dialog').find('button#new-user').attr('disabled', true);
            }
        });

        $('button#new-user').click(function (event) {
            var formData = new FormData(document.querySelector('form#new-user-form'));
            $.ajax({
                    type: 'POST',
                    url: $SCRIPT_ROOT + '/users',
                    data: formData,
                    processData: false,
                    contentType: false
                })
                .done(function (data) {
                    if ('error' in data) {
                        alertify.error(data.message);
                    } else {
                        alertify.success('OK');
                        grid.loadData();
                    }
                    return false;
                })
                .fail(function (xhr, status, error) {
                    alertify.error(status + ':' + error);
                })
                .always(function () {
                    $('#new-user-dialog').modal('hide');
                });
        });

    });

}());
