function setDataTable() {
	data_tab=$('#bill_tab').DataTable({
			    		"ordering": true,
			    		paging: false,
			    		"order": [[ 0, "asc" ]],
			    		"language": {
						    "emptyTable": "Aucune facture dans la base de données",
						    "search":         "Rechercher :",
						    "info":           "Données de _START_ à _END_ sur _TOTAL_",
    						"infoEmpty":      "",

    						"infoFiltered":   "(filtré depuis _MAX_ entrées totales)",
    						"lengthMenu":     "Montre _MENU_ entrées",
						    "loadingRecords": "Chargement...",
						    "processing":     "Exécution...",
						    "zeroRecords":    "Aucune correspondance trouvée"
						}
		    		});

	data_tab.on('click', '.button_detail',function() {
		let bill_id=$(this).data('bid');
		$.ajax({
			headers: { "X-CSRFToken": csrf}, 
			type: 'POST',
			url: url_get_bill_modal,
			data: {
				'id': bill_id,
			},
			dataType: 'html',
			success: function (data) {
				if(data['error'])
					alert(data['error']);	
				else {
				
					$('#myModal').html(data);
					$('#myModal').modal('toggle');
				}
			}
		});
	});


}
// query : mot-clé arbitraire désignant ce qu'on veut faire
// soit 'table' (remplace data_tab par un queryset filtré), soit 'recap' (affiche une modale)
function sendDateAndGetResponse(query) {
	$.ajax({
		headers: { "X-CSRFToken": csrf}, 
		type: 'POST',
		url: url_swap_bills_display,
		data: {
			'date': $('#swap_bills_input').val(),
			'query':query
		},
		dataType: 'html',
		success: function (data) {
			if(data['error'])
				alert(data['error']);	
			else {
				if(query=='table') {				
					$('#table_container').html(data);
					setDataTable();
				}
				else {
					$('#myModal').html(data);
					$('#myModal').modal('show');
				}
			}
		}
	});
}


$(document).ready(function() {

	setDataTable();

	$('#swap_bills_display').click(function() {
		sendDateAndGetResponse('table');
	});

	$('#show_bills_recap').click(function() {
		sendDateAndGetResponse('recap');

	});

	//$('#datepickerFact').val("").datepicker("update");


});

$('#swap_bills_input').datepicker({
            format: "mm/yyyy",
		    startView: 1,
		    minViewMode: 1,
		    maxViewMode: 2,
		    language: "fr",
		    calendarWeeks: true,
		    autoclose: true,
		    clearBtn: true,
    });
