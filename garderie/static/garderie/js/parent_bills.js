function setDataTable() {

	let data_tab_bills = $('#parent_profile_facture_tab').DataTable({
			    		"ordering": true,
			    		paging: false,
			    		"order": [[ 0, "asc" ]],
			    		"searching": false,
			    		"language": {
						    "emptyTable": "Aucune facture n'est enregistrée",
						    "search":         "Rechercher :",
						    "info":           "Données de _START_ à _END_ sur _TOTAL_ entrées",
    						"infoEmpty":      "Données 0 à 0 sur 0"
						}
		    		});

	

}


$(document).ready(function() {

	setDataTable();

	$('#swap_bills_display').click(function() {
		$.ajax({
			headers: { "X-CSRFToken": csrf}, 
			type: 'POST',
			url: url_swap_bills_display,
			data: {
				'pid': $(this).data('pid'),
				'date': $('#swap_bills_input').val(),
			},
			dataType: 'html',
			success: function (data) {
				if(data['error'])
					alert(data['error']);	
				else {
					$('#table_container').html(data);
					setDataTable();
				}
			}
		});
	});

	$('#btn-detail').click(function() {
		let pid=$(this).data('pid');
		let d=$('#swap_bills_input').datepicker('getDate');
		$.ajax({
			headers: { "X-CSRFToken": csrf}, 
			type: 'POST',
			url: url_show_details,
			data: {
				'id': pid,
				'month': d ? d.getMonth()+1 : null,
				'year': d ? d.getFullYear() : null,
			},
			dataType: 'html',
			success: function (data) {
				if(data['error'])
					alert(data['error']);	
				else {
				
					$('#factureModal').html(data);
					$('#factureModal').modal('toggle');
				}
			}
		});
	});



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
