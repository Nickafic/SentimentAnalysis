function exportTableToCSV(tableId, filename) 
{
    
    var csv = []; //DATA
    var rows = document.getElementById(tableId).querySelectorAll('tr'); //Grab all rows from the table with the given table id

    for (var i = 0; i < rows.length; i++) 
    {
        var activeRow = [];
        var activeCols = rows[i].querySelectorAll('td, th'); //Select headers and data cells

        for (var j = 0; j < activeCols.length; j++) 
            activeRow.push( activeCols[j].innerText );
        
        csv.push(activeRow.join(','));
    }
    //Encode To File
    var csvContent = 'data:text/csv;charset=utf-8,' + csv.join('\n');
    var encodedUri = encodeURI(csvContent);
    //Start Download
    var link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
}

function openPopup() {
    $('#saveTableModal').modal('show');
}
  