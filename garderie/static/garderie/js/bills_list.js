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
		let pid=$(this).data('pid');
		let month=$(this).data('month');
		let year=$(this).data('year');
		$.ajax({
			headers: { "X-CSRFToken": csrf}, 
			type: 'POST',
			url: url_get_bill_modal,
			data: {
				'id': pid,
				'month': month,
				'year': year,
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


$(document).ready(function() {

	setDataTable();

	$('#swap_bills_display').click(function() {
		$.ajax({
			headers: { "X-CSRFToken": csrf}, 
			type: 'POST',
			url: url_swap_bills_display,
			data: {
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

	$('#show_bills_recap').click(function() {
		$.ajax({
			headers: { "X-CSRFToken": csrf}, 
			type: 'POST',
			url: url_show_recap,
			data: {
				'date': $('#swap_bills_input').val(),
			},
			dataType: 'html',
			success: function (data) {
				if(data['error'])
					alert(data['error']);	
				else {
					$('#myModal').html(data);
					$('#myModal').modal('show');
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
