# Create your views here.

from reports import *

class ConcorOutputs(forms.Form):
	bit0 = forms.BooleanField(label = "Acometida 1", required=False)
	bit1 = forms.BooleanField(label = "Acometida 2", required=False)
	bit2 = forms.BooleanField(label = "Acometida 3", required=False)
	bit3 = forms.BooleanField(label = "Acometida 4", required=False)
	bit4 = forms.BooleanField(label = "Acometida 5", required=False)
	bit5 = forms.BooleanField(label = "Acometida 6", required=False)
	bit6 = forms.BooleanField(label = "Acometida 7", required=False)
	bit7 = forms.BooleanField(label = "Acometida 8", required=False)
	bit8 = forms.BooleanField(label = "Acometida 9", required=False)
	bit9 = forms.BooleanField(label = "Acometida 10", required=False)
	bit10 = forms.BooleanField(label = "Acometida 11", required=False)
	bit11 = forms.BooleanField(label = "Acometida 12", required=False)
	submit_text = "Modificar"
	
class ConcorView(FormView)	:
	template_name = "cfeForm.html"
	form_class = ConcorOutputs
	success_url = ''
	imei = '862462035432417'
	
	def dispatch(self, *args, **kwargs):
		self.imei = kwargs.pop('imei') or self.imei
		self.dev = get_object_or_404(SGAvl,imei = self.imei)
		return super(FormView, self).dispatch(*args, **kwargs)
	
	def get_initial(self):
		bit0 = (self.dev.outputs & 1) != 0
		bit1 = (self.dev.outputs & 2) != 0
		bit2 = (self.dev.outputs & 4) != 0
		bit3 = (self.dev.outputs & 8) != 0
		bit4 = (self.dev.outputs & 16) != 0
		bit5 = (self.dev.outputs & 32) != 0
		bit6 = (self.dev.outputs & 64) != 0
		bit7 = (self.dev.outputs & 128) != 0
		bit8 = (self.dev.outputs & 256) != 0
		bit9 = (self.dev.outputs & 512) != 0
		bit10 = (self.dev.outputs & 1024) != 0
		bit11 = (self.dev.outputs & 2048) != 0
		return dict(bit0 = bit0,bit1 = bit1,bit2 = bit2,bit3 = bit3,bit4 = bit4,bit5 = bit5,bit6 = bit6,bit7 = bit7,bit8 = bit8,bit9 = bit9,bit10 = bit10,bit11 = bit11)

	def form_valid(self,form):
		ins = 0
		if form.cleaned_data['bit0']: ins |=1
		if form.cleaned_data['bit1']: ins |=2
		if form.cleaned_data['bit2']: ins |=4
		if form.cleaned_data['bit3']: ins |=8
		if form.cleaned_data['bit4']: ins |=16
		if form.cleaned_data['bit5']: ins |=32
		if form.cleaned_data['bit6']: ins |=64
		if form.cleaned_data['bit7']: ins |=128
		if form.cleaned_data['bit8']: ins |=256
		if form.cleaned_data['bit9']: ins |=512
		if form.cleaned_data['bit10']: ins |=1024
		if form.cleaned_data['bit11']: ins |=2048
		self.dev.inputs = ins
		self.dev.save()
		return self.render_to_response(self.get_context_data(form=form))
		
class CfeView(TemplateView):
	EVS = ["TRACK","IO_FIX","IO_NOFIX","SMS_RECEIVED"] #,"GPS_OK","GPS_LOST"]

	template_name = "fancyCFE.html"
	#imei = '13949000489073'
	
	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		self.imei = kwargs.pop('imei')	
		self.dev = get_object_or_404(SGAvl,imei = self.imei)
		return super(CfeView, self).dispatch(*args, **kwargs)

	#def get(self, request, *args, **kwargs):
	#	self.dev = get_object_or_404(SGAvl,imei = self.imei)
	#	return super(CfeView, self).get(request,*args,**kwargs)
	
	def post(self, request, *args, **kwargs):
		if not request.is_ajax():
			return HttpResponse(simplejson.dumps({'result': "Not Ajax"}), mimetype='application/json')
		try:
			cmd = request.POST['cmd']
			id = int(request.POST['id'])
			if id<1 or id>6:
				raise ValueError()
			if cmd == 'cancel':
				a = 1<<(id-1)
				if self.dev.newOutputs:
					self.dev.newOutputs ^= a
					if self.dev.newOutputs == self.dev.outputs:
						self.dev.newOutputs = None
				self.dev.save()
			elif cmd == "set":
				a = 1<<(id-1)
				if self.dev.newOutputs:
					self.dev.newOutputs |= a
				else:
					self.dev.newOutputs = self.dev.outputs |a
				self.dev.save()
			elif cmd == "clr":
				a = 1<<(id-1)
				if self.dev.newOutputs:
					self.dev.newOutputs &= (~a)
				else:
					self.dev.newOutputs = self.dev.outputs & ~a
				self.dev.save()
			else:
				raise ValueError
			return HttpResponse(simplejson.dumps({'result': "Ok", "cmd":cmd , "id":id}), mimetype='application/json')
		except:
			return HttpResponse(simplejson.dumps({'result': "Invalid request"}), mimetype='application/json')

	def get_context_data(self, **kwargs):
		context = super(CfeView, self).get_context_data(**kwargs)
		context['avl'] = self.dev
		if self.dev.position:
			context['x'] = self.dev.position.x
			context['y'] = self.dev.position.y
		context['dev_name'] = self.dev.name
		outputs = []
		for i in range(0,4):
			if self.dev.newOutputs:
				no = True if ((self.dev.newOutputs^self.dev.outputs)>>i) & 1 else False
			else: 
				no = False
			o =  True if (self.dev.outputs>>i) & 1 else False
			cmd = "cancel" if no else "clr" if o else "set"
			action = "Cancelar" if no else "Desactivar" if o else "Activar"
			state = "Encendido" if o else "Apagado"
			dir = "out" if o else "in"
			a = dict(id = i+1,cmd =cmd,action =action, state = state, dir = dir)
			outputs.append(a)
		context['outputs']=outputs
		return context
