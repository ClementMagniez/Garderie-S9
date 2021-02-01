from django.forms import DateTimeInput

class BootstrapDateTimePickerInput(DateTimeInput):
	template_name="garderie/widgets/bootstrap_datetimepicker.html"
	
	def get_context(self, name, value, attrs):
		datepicker_id=f'datepicker_{name}'
		if attrs is None:
			attrs=dict()
		attrs['data-target']=f'#{datepicker_id}'
		attrs['class']='form-control datetimepicker-input'

		context=super().get_context(name, value, attrs)
		context['widget']['datepicker_id']=datepicker_id
		return context
