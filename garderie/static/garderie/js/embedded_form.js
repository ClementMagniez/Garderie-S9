/* Django a un support limité des forms intégrés à une page complexe, 
** typiquement un DesignView ou un modal ; on gère donc cette situation
** à la main en contournant Django. 
** Au submit du form, on l'envoie par AJAX ; si on récupère des erreurs,  
** on les affiche directement dans le form déjà chargé. 
*/
$(document).ready(function () {

	console.log("jquery up");
	$('.embedded_form').on('submit', function(event) {

		console.log("event registered");
		event.preventDefault();

		let url = $(this).attr('action') || action;
		
		console.log($(this).serialize());

		$.ajax({
			type: $(this).attr('method'),
			
			url: url,
			data: $(this).serialize(),
			success: function(data) {
				let parser = new DOMParser();
				doc = parser.parseFromString(data, "text/html");
				let remainder = $(doc).find(".errorlist");
				console.log(remainder);
	
				if (remainder[0]) {
					$('.embedded_error').remove();
					$('.embedded_form table').prepend('<tr class="embedded_error"><td colspan="2"><ul class="errorlist nonfield">'+remainder[0].innerHTML+'</ul></td></tr>');
				}
				else { location.reload(); }
			},
			error: function(xhr, ajaxOptions, thrownError) {
				console.log('SERVER ERROR: ' + thrownError);
			},
			
		});
	});
});
