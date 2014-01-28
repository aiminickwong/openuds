/* jshint strict: true */
gui.servicesPool = new GuiElement(api.servicesPool, 'servicespool');
 

gui.servicesPool.link = function(event) {
    "use strict";
    gui.clearWorkspace();
    
    // Clears the details
    // Memory saver :-)
    var prevTables = [];
    var clearDetails = function() {
        $.each(prevTables, function(undefined, tbl){
            var $tbl = $(tbl).dataTable();
            $tbl.fnClearTable();
            $tbl.fnDestroy();
        });
        
        $('#assigned-services-placeholder').empty();
        $('#cache-placeholder').empty();
        $('#transports-placeholder').empty();
        $('#groups-placeholder').empty();
        $('#logs-placeholder').empty();
        
        $('#detail-placeholder').addClass('hidden');
        
        prevTables = [];
    };
    
    // Fills up the list of available services
    api.providers.allServices(function(services){
        var availableServices = {};
        
        $.each(services, function(undefined, service){
            availableServices[service.id] = service;    
        });

        gui.doLog('Available services', availableServices);
        api.templates.get('services_pool', function(tmpl) {
            gui.appendToWorkspace(api.templates.evaluate(tmpl, {
                deployed_services : 'deployed-services-placeholder',
                assigned_services : 'assigned-services-placeholder',
                cache : 'cache-placeholder',
                groups : 'groups-placeholder',
                transports : 'transports-placeholder',
                publications: 'publications-placeholder',
                logs : 'logs-placeholder',
            }));
            gui.setLinksEvents();
            
            var testClick = function(val, value, btn, tbl, refreshFnc) {
                gui.doLog(value);
            };
            var counter = 0;
            var testSelect = function(val, value, btn, tbl, refreshFnc) {
                if( !val ) {
                    $(btn).removeClass('btn3d-info').addClass('disabled');
                    return;
                }
                $(btn).removeClass('disabled').addClass('btn3d-info');
                counter = counter + 1;
                gui.doLog('Select', counter.toString(), val, value);
            };
            
            var tableId = gui.servicesPool.table({
                container : 'deployed-services-placeholder',
                rowSelect : 'single',
                buttons : [ 'new', 'edit', 'delete', { text: gettext('Test'), css: 'disabled', click: testClick, select: testSelect }, 'xls' ],
                onRowDeselect: function() {
                    clearDetails();
                },
                onRowSelect : function(selected) {
                    var servPool = selected[0];
                    gui.doLog('Selected services pool', servPool);
                    
                    clearDetails();
                    $('#detail-placeholder').removeClass('hidden');
                    // If service does not supports cache, do not show it
                    var service = null;
                    try {
                        service = availableServices[servPool.service_id];
                    } catch (e) {
                        gui.doLog('Exception on rowSelect', e);
                        gui.notify(gettext('Error processing deployed service'), 'danger');
                        return;
                    }
                    
                    var cachedItems = null;
                    // Shows/hides cache
                    if( service.info.uses_cache || service.info.uses_cache_l2 ) {
                        $('#cache-placeholder_tab').removeClass('hidden');
                        cachedItems = new GuiElement(api.servicesPool.detail(servPool.id, 'cache'), 'cache');
                        var cachedItemsTable = cachedItems.table({
                            container : 'cache-placeholder',
                            rowSelect : 'single'
                        });
                        prevTables.push(cachedItemsTable);
                    } else {
                        $('#cache-placeholder_tab').addClass('hidden');
                    }
                    var groups = null;
                    // Shows/hides groups
                    if( service.info.must_assign_manually === false ) {
                        $('#groups-placeholder_tab').removeClass('hidden');
                        groups = new GuiElement(api.servicesPool.detail(servPool.id, 'groups'), 'groups');
                        var groupsTable = groups.table({
                            container : 'groups-placeholder',
                            rowSelect : 'single',
                            onData: function(data) {
                                $.each(data, function(undefined, value){
                                    value.group_name = '<b>' + value.auth_name + '</b>\\' + value.name;
                                });
                            },
                        });
                        prevTables.push(groupsTable);
                    } else {
                        $('#groups-placeholder_tab').addClass('hidden');
                    }
                    
                    var assignedServices =  new GuiElement(api.servicesPool.detail(servPool.id, 'services'), 'services');
                    var assignedServicesTable = assignedServices.table({
                        container: 'assigned-services-placeholder',
                        rowSelect: 'single',
                    });
                    prevTables.push(assignedServicesTable);
                    
                    var transports =  new GuiElement(api.servicesPool.detail(servPool.id, 'transports'), 'transports');
                    var transportsTable = transports.table({
                        container: 'transports-placeholder',
                        rowSelect: 'single',
                        onData: function(data) {
                            $.each(data, function(undefined, value){
                                var style = 'display:inline-block; background: url(data:image/png;base64,' +
                                            value.type.icon + '); ' + 'width: 16px; height: 16px; vertical-align: middle;';
                                value.trans_type = value.type.name;
                                value.name = '<span style="' + style + '"></span> ' + value.name;
                            });
                        }
                    });
                    prevTables.push(transportsTable);
                    
                    var publications = null;
                    if( service.info.needs_publication ) {
                        $('#publications-placeholder_tab').removeClass('hidden');
                        var pubApi = api.servicesPool.detail(servPool.id, 'publications');
                        publications = new GuiElement(pubApi, 'publications');
                        var publicationsTable = publications.table({
                            container : 'publications-placeholder',
                            rowSelect : 'single',
                            buttons : [ 'new', { 
                                                    text: gettext('Cancel'), 
                                                    css: 'disabled', 
                                                    click: function(val, value, btn, tbl, refreshFnc) {
                                                        gui.doLog(val);
                                                    }, 
                                                    select: function(val, value, btn, tbl, refreshFnc) {
                                                        if( !val ) {
                                                            $(btn).removeClass('btn3d-info').addClass('disabled');
                                                            return;
                                                        }
                                                        if( ['P','W','L'].indexOf(val.state) > 0 ) { // Waiting for publication, Preparing or running
                                                            $(btn).removeClass('disabled').addClass('btn3d-info');
                                                        }
                                                    },
                                                }, 
                                        'xls' ],
                            onNew: function(action, tbl, refreshFnc) {
                                gui.doLog('New publication');
                                pubApi.invoke('publish', function(){
                                    gui.doLog('Success');
                                }, gui.failRequestModalFnc(gettext('Publication failed')) );
                            },
                        });
                        prevTables.push(publicationsTable);
                        
                    } else {
                        $('#publications-placeholder_tab').addClass('hidden');
                    }
                    
                    var logTable = gui.servicesPool.logTable(servPool.id, {
                        container : 'logs-placeholder',
                    });
                    
                    prevTables.push(logTable);
                },
                // Pre-process data received to add "icon" to deployed service
                onData: function(data) {
                    gui.doLog('onData', data);
                    $.each(data, function(index, value){
                        try {
                            var service = availableServices[value.service_id];
                            var style = 'display:inline-block; background: url(data:image/png;base64,' +
                                service.info.icon + '); ' + 'width: 16px; height: 16px; vertical-align: middle;';

                            if( value.restrained ) {
                                value.name = '<span class="fa fa-exclamation text-danger"></span> ' + value.name;
                                value.state = gettext('Restrained');
                            }
                            
                            value.name = '<span style="' + style + '"></span> ' + value.name;
                            
                            value.parent = service.name;
                        } catch (e) {
                            value.name = '<span class="fa fa-asterisk text-alert"></span> ' + value.name; 
                            value.parent = gettext('unknown (needs reload)');
                        }
                    });
                },
                onNew: function(type, table, refreshFnc) {
                    gui.methods.typedNew(gui.servicesPool, gettext('New service pool'), gettext('Error deleting service pool'))(type, table, refreshFnc);
                }
            });
        });
    });
      
};