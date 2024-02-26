var currentPage = 1;
var resultsPerPage = 10;
var data;
var totalRecords = 0;
let datatableColumnSettings;
let table;
let columnVisibilityStates = [];


$(document).ready(function(){
    // $('#taskIdSelect, #projectSelect, #phaseSelect, #categorySelect, #caseTitleSelect').select2({ width: 'resolve' });
    // $('#clearAllButton').click(clearAll);
    $('#outputTable thead tr:eq(1) th').each(function(i) {
        $('input', this).on('keyup change', function() {
            if (table.column(i).search() !== this.value) {
                table.column(i).search(this.value).draw();
            }
        });
    });
    // $.ajax({
    //     url: '/get-dropdown-data',
    //     type: 'GET',
    //     success: function(data) {
    //         var taskIdSelect = $('#taskIdSelect');
    //         data.taskIds.forEach(function(taskid) {
    //             taskIdSelect.append($('<option>', { value: taskid, text: taskid }));
    //         });

    //         var projectSelect = $('#projectSelect');
    //         data.platformNames.forEach(function(name) {
    //             projectSelect.append($('<option>', { value: name, text: name }));
    //         });

    //         var phaseSelect = $('#phaseSelect');
    //         data.hwPhases.forEach(function(phase) {
    //             phaseSelect.append($('<option>', { value: phase, text: phase }));
    //         });

    //         var categorySelect = $('#categorySelect');
    //         data.categories.forEach(function(category) {
    //             categorySelect.append($('<option>', { value: category, text: category }));
    //         });

    //         var caseTitleSelect = $('#caseTitleSelect');
    //         data.caseTitles.forEach(function(title) {
    //             caseTitleSelect.append($('<option>', { value: title, text: title }));
    //         });

    //     },
    //     error: function(error) {
    //         console.error("Error loading dropdown data: ", error);
    //     }
    // });
    //initializeDataTable();
    executeQuery(); 
});

// $(document).ready(function() {
//     $('.js-example-basic-multiple').select2({
//         placeholder: "Select Columns",
//         allowClear: true,
//         width: '100%',
//         closeOnSelect: false
//     });
//     $('.js-example-basic-multiple').on('change', function() {
//         var selectedColumnsValues = $(this).val(); 

//         selectedColumnsString = selectedColumnsValues.map(function(value, index) {
//             return "`" + value + "`";
//         }).join(", ");

//         // console.log(selectedColumnsString);
//     });
// });

// $(document).on('DOMNodeRemoved', function(e) {
//     if ($(e.target).hasClass('dt-button-collection')) {
//         executeQuery();
//     }
// });

// var observer = new MutationObserver(function(mutations) {
//     mutations.forEach(function(mutation) {
//         if (mutation.removedNodes) {
//             mutation.removedNodes.forEach(function(removedNode) {
//                 if ($(removedNode).hasClass('dt-button-collection')) {
//                     captureColumnSettings(table);
//                      executeQuery();
//                      table.on('column-visibility.dt', function(e, settings, column, state) {
//                          var columnVisibility = table.columns().visible().toArray();
//                          localStorage.setItem('datatableColumnVisibility', JSON.stringify(columnVisibility));
//                      });
//                      table.on('column-visibility.dt', function(e, settings, columnIdx, visible) {
//                          visibleColumns = table.columns().visible().toArray();
//                      });
//                 }
//             });
//         }
//     });
// });

var config = { childList: true, subtree: true };

// observer.observe(document.body, config);

function captureColumnSettings(table) {
    let columnSettings = table.columns().eq(0).map(function(index) {
        let column = table.column(index);
        return {
            visible: column.visible(),
            className: $(column.header()).attr('class'),
            width: $(column.header()).css('width')
        };
    }).toArray();
    //datatableColumnSettings = JSON.stringify(columnSettings)
    localStorage.setItem('datatableColumnSettings', JSON.stringify(columnSettings));
}

function getVisibleColumnsAsString() {
    var visibleColumns = table.columns(':visible').header().toArray().map(function(header) {
        return '`' + $(header).text() + '`';
    });
    
    return visibleColumns.join(', ');
}

function executeQuery() {
    // var taskId = document.getElementById("taskIdSelect").value;
    // var project = document.getElementById("projectSelect").value;
    // var caseTitle = document.getElementById("caseTitleSelect").value;
    // var phase = document.getElementById("phaseSelect").value;
    // var category = document.getElementById("categorySelect").value;
    // var highRiskCheckbox = document.getElementById("highRiskCheckbox");

    if (typeof table === 'undefined') {
        selectedColumnsString = "`ID`, `Task ID`, `Case Title`, `Pass/Fail`, `Testing Site`, `Tester`, `Platform Name`, `SKU`, `Hw Phase`, `OBS`, `Block Type`, `File`, `KAT/KUT`, `RTA`, `ATT/UAT`, `Run Cycle`, `Fail Cycle/Total Cycle`, `Category`, `Case Note`, `Comments`, `Component List`, `Comment`";
    } else {
        selectedColumnsString = getVisibleColumnsAsString();
    }

    selectedColumnsString = "`Task ID`, `Case Title`, `Pass/Fail`, `Tester`, `Platform Name`, `SKU`, `Hw Phase`, `OBS`, `Block Type`, `File`, `KAT/KUT`, `RTA`, `ATT/UAT`, `Run Cycle`, `Fail Cycle/Total Cycle`, `Category`, `Case Note`, `Comments`, `Component List`, `Comment`";

    var sqlQuery = `SELECT ${selectedColumnsString} FROM abc`
    // WHERE (\`Task ID\` = '${taskId}' OR '${taskId}' = '')
    // AND (\`Platform Name\` = '${project}' OR '${project}' = '')
    // AND (\`Case Title\` = '${caseTitle}' OR '${caseTitle}' = '')
    // AND (\`HW Phase\` = '${phase}' OR '${phase}' = '')
    // AND (\`Category\` REGEXP '^[[:space:]]*${category}[[:space:]]*$' OR '${category}' = '')`;

    // if (highRiskCheckbox.checked) {
    //     sqlQuery += ` AND (\`OBS\` != '')`;
    // }


    fetch('/execute_query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json; charset=utf-8'
        },
        body: JSON.stringify({query: sqlQuery}),
    })
    .then(response => response.json())
    .then(responseData => {
    
        if (!responseData || !Array.isArray(responseData.result)) {
            console.error("Response data is not defined or is not an array.");
            return;
        }
        data = responseData.result; 
        totalRecords = data.length; 
        initializeDataTable();
    })
    

    .catch((error) => {
        console.error('Error:', error);
    });

}

function initializeDataTable() {
    let savedSettings = localStorage.getItem('datatableColumnSettings');
    //let savedSettings = datatableColumnSettings
    let columnSettings = savedSettings ? JSON.parse(savedSettings) : [];
    table = $('#outputTable').DataTable({
        "destroy": true, 
        "data": data,
        // "columns": data.list_columns,
        // "fixedHeader":{
        //     header: true,
        //     headerOffset: -6
        // }, 
        "processing" : true,
        
        "columns": [
            {   // Checkbox select column
                orderable: false,
                className: 'select-checkbox noVis',
                targets: -1,
                render: function (data, type, full, meta) {
                    return '<input type="checkbox" class="my-custom-checkbox" />';
                }
            },     
            { "data": 0}, // 對應 "Task ID"
            { "data": 1, "className": "case-title-column"}, // 對應 "Case Title"
            { "data": 2}, // 對應 "Pass/Fail"
            { "data": 3}, // 對應 "Tester"
            { "data": 4}, // 對應 "Platform Name"
            { "data": 5}, // 對應 "SKU"
            { "data": 6}, // 對應 "Hw Phase"
            { "data": 7,
            "className": 'redirect-cell',
            "render": function(data, type, row) {
                if (data !== null && data !== '') {
                    if (data.includes(',')) {
                        var dataArray = data.split(',');
                        var linkHtml = '';
                        for (var i = 0; i < dataArray.length; i++) {
                        var sioNumber = dataArray[i].trim(); 
                        var url = 'https://si.austin.hp.com/si/Observations/Details.aspx?offset=8&ObservationId=' + sioNumber;
                        linkHtml += '<a href="' + url + '" class="clickable" target="_blank">' + sioNumber + '</a>';

                        if (i < dataArray.length - 1) {
                            linkHtml += ', ';
                        }
                        }

                        return linkHtml;
                    } else {
                        var url = 'https://si.austin.hp.com/si/Observations/Details.aspx?offset=8&ObservationId=' + data;
                        return '<a href="' + url + '" class="clickable" target="_blank">' + data + '</a>';
                    }
                    } else {
                    return data;
                    }
            },
            "width": "0.8%"
            }, // 對應 "OBS"
            { "data": 8}, // 對應 "Block Type"
            { "data": 9}, // 對應 "File"
            { "data": 10}, // 對應 "KAT/KUT"
            { "data": 11}, // 對應 "RTA"
            { "data": 12}, // 對應 "ATT/UAT"
            { "data": 13}, // 對應 "Run Cycle"
            { "data": 14}, // 對應 "Fail Cycle/Total Cycle"
            { "data": 15}, // 對應 "Category"
            { "data": 16}, // 對應 "Case Note"
            { "data": 17,
            "className": 'ellipsis-cell', 
            "render": function(data, type, row) {
                if (data !== null && data !== '') {
                    return '<span class="has-data">' + data + '</span>';
                } else {
                    return data;
                }
            },
            "width": "2%"}, // 對應 "Comments"
            { "data": 18,
            "className": 'ellipsis-cell', 
            "render": function(data, type, row) {
                if (data !== null && data !== '') {
                    return '<span class="has-data">' + data + '</span>';
                } else {
                    return data;
                }
            },
            "width": "2%"}, // 對應 "Component List"
            { "data": 19,
            "className": 'ellipsis-cell',"render": function(data, type, row) {
                if (data !== null && data !== '') {
                    return '<span class="has-data">' + data + '</span>';
                } else {
                    return data;
                }
            },
            "width": "2%"}, // 對應 "Comment"
        ],
        "columnDefs": [ 
        { 
            searchPanes: {
                header: 'High Priority Test Cases',
                controls: false,
                options: [
                    {
                        label: 'Has OBS ID',
                        value: function(rowData) {
                            return rowData[7] != '';
                        }
                    }
                ]
            },
            targets: [8]
        }
        
    ],
        "select": {
            style:    'multi',
            selector: 'td.select-checkbox',
        },
        "order": [1, 'asc'],
        "paging": true, 
        "pagingType": "full_numbers",
        "info": true, 
        "searching": true, 
        "ordering": true, 
        "language": {
            "lengthMenu": "Show _MENU_ items",
            "info": "Showing _START_ to _END_ of _TOTAL_ items",
            "paginate": {
                next: '<i class="fas fa-angle-right"></i>',
                previous: '<i class="fas fa-angle-left"></i>',
                first: '<i class="fas fa-angle-double-left"></i>',
                last: '<i class="fas fa-angle-double-right"></i>'
              }
        },
        "scrollX": true,
        "scrollY": "600px",
        "searchPanes": {
            //initCollapsed: true,
            show: true,
            cascadePanes: true,
            orderable: false,
            layout: 'columns-1',
            columns: [8, 1, 5, 7, 16],  
            i18n: {
                title: '<i class="fa-solid fa-filter"></i>'+'Filters',
                clearMessage: '<i class="fa-solid fa-eraser"></i>',
                showMessage: '<i class="fa-solid fa-arrow-down-short-wide"></i>',
                collapseMessage: '<i class="fa-solid fa-arrow-up-short-wide"></i>',
            },        
        },
        "dom": 
        '<"dtsp-dataTable"' +
        '<"top"P>' +
        '<Bf>' +
        'rt' +
        '<"bottom"<"row"<"col-md-10"i><"col-md-1"l>>>' +
        '<"row"<"col-12"p>>' +
        '<"clear">' +
        '>',
    
        "buttons": [
            {
                extend: 'colvis',
                text: 'Display Columns',
                columns: ':not(.noVis)',
                className: 'custom-colvis-button',
                collectionLayout: 'fixed columns',
                collectionLayout: "fixed four-column",
                prefixButtons: [
                {
                    extend: "colvisGroup",
                    text:
                    '<span><i class="fas fa-check-double"></i></span>Show all',
                    className: "show-all",
                    show: ":hidden"
                },
                {
                    extend: "colvisGroup",
                    text:
                    '<span><i class="fas fa-eye-slash"></i></span>Hide all',
                    className: "hide-all",
                    hide: ":visible"
                }
                ]          
            },
            {
                extend: 'excelHtml5',
                className: 'custom-excel-button',
                text: 'Excel',
                exportOptions: {
                   columns: ':visible'
               },
                action: function (e, dt, button, config) {
                    var today = new Date();
                    var formattedDate = today.getFullYear() + '-' + (today.getMonth() + 1).toString().padStart(2, '0') + '-' + today.getDate().toString().padStart(2, '0');
                    var defaultFileName = "Test Case Prioritization-" + formattedDate;
            
                    swal({
                        title: "Export to Excel",
                        text: "Please enter a name for the Excel file:",
                        content: {
                            element: "input",
                            attributes: {
                                value: defaultFileName,
                            },
                        },
                        buttons: ["Cancel", "Export"],
                        closeOnClickOutside: true 
                    }).then((value) => {
                        if (value !== null) { 
                            config.filename = value ? value : defaultFileName; 
                            $.fn.dataTable.ext.buttons.excelHtml5.action.call(this, e, dt, button, config);
                        }
                    });
                }
             }
        ],
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]], 
        "pageLength": 10, 
        "pageResize": true,
        "initComplete": function(settings, json) {
            this.api().columns().every(function(index) {
                let column = this;
                let settings = columnSettings[index] || {};
                column.visible(settings.visible, false);
                $(column.header()).addClass(settings.className);
                $(column.header()).css('width', settings.width);
            });
            this.api().columns.adjust().draw(false);
        }
    });
    
    $("div.dtsp-verticalPanes").append(table.searchPanes.container());
    
    table.searchPanes.resizePanes()
    $('#outputTable tbody').on('click', 'td.ellipsis-cell', function() {
        var cellData = table.cell(this).data();
        if (cellData !== null && cellData !== '') {
            $('#exampleModal .modal-body').text(cellData);
            $('#exampleModal').modal('show');
        }
    }); 


    // $('#outputTable tbody').on('click', 'td.redirect-cell', function() {
    //     var cellData = $(this).text(); 
    //     var url = 'https://si.austin.hp.com/si/Observations/Details.aspx?offset=8&ObservationId=' + cellData; 
    
    //     window.open(url, '_blank'); 
    // });
}



// function clearAll() {
//     $('#taskIdSelect').attr('onchange', '');
//     $('#projectSelect').attr('onchange', '');
//     $('#phaseSelect').attr('onchange', '');
//     $('#categorySelect').attr('onchange', '');
//     $('#caseTitleSelect').attr('onchange', '');

//     $('#taskIdSelect').val('').trigger('change');
//     $('#projectSelect').val('').trigger('change');
//     $('#phaseSelect').val('').trigger('change');
//     $('#categorySelect').val('').trigger('change');
//     $('#caseTitleSelect').val('').trigger('change');

//     $('#taskIdSelect').attr('onchange', 'executeQuery()');
//     $('#projectSelect').attr('onchange', 'executeQuery()');
//     $('#phaseSelect').attr('onchange', 'executeQuery()');
//     $('#categorySelect').attr('onchange', 'executeQuery()');
//     $('#caseTitleSelect').attr('onchange', 'executeQuery()');

//     $('#highRiskCheckbox').attr('onchange', '');

//     $('#highRiskCheckbox').prop('checked', false);

//     $('#highRiskCheckbox').attr('onchange', 'executeQuery()');

//     localStorage.removeItem('datatableColumnSettings');
//     //datatableColumnSettings = null;
   
//     executeQuery();
// }


