/* Django a un support limité des forms intégrés à une page complexe, 
** typiquement un DesignView ou un modal ; on gère donc cette situation
** à la main en contournant Django. 
** Au submit du form, on l'envoie par AJAX ; si on récupère des erreurs,  
** on les affiche directement dans le form déjà chargé. 
*/
$(document).ready(function () {

	$('.embedded_form').on('submit', function(event) {
		let form=$(this);		
		event.preventDefault();
		event.stopImmediatePropagation();
		let url = $(this).attr('action') || action;
		
		$.ajax({
			type: $(this).attr('method'),
			
			url: url,
			data: $(this).serialize(),
			success: function(data) {
				if($.isEmptyObject(data)) {
					// Traite différemment les formulaires intégrés à une modale et ceux présents directement sur la page 
					if(form.parents('#myModal').length) {
						$('#myModal').modal('toggle');
					}
					else {
						location.reload(); 
					} 
				}
				else {
					form.find('.embedded_error').remove();
					form.find('table').prepend('<tr class="embedded_error">');
					for(key in data) {
						console.log(key);

						for(let i=0;i<data[key].length;i++) {
							form.find('.embedded_error').append('<td colspan="2"><ul>'+data[key][i]+'</ul></td></tr>');
						}
					}			
				}
			},
			error: function(xhr, ajaxOptions, thrownError) {
				console.log(xhr);
				console.log('SERVER ERROR: ' + thrownError);
			},
			
		});
	});
});

