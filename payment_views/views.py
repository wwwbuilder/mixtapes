from django.shortcuts import render
from braces import views
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from payments.models import *
from addon.models import *
from django.views.generic import TemplateView
from django.conf import settings

class ChangeCardView(views.JSONResponseMixin, views.AjaxResponseMixin, View):
	def get(self, request, *args, **kwargs):
		return redirect(reverse('my-account:my-payments'))

	def post_ajax(self, request, *args, **kwargs):

		#print request.POST

		data = {}

		try:
			if request.user.customer:
				print 'Customer for %s found!' % request.user.username
				try:
					print '\t--> attempting to update card.'
					update = request.user.customer.update_card(token=request.POST['stripeToken'])
					data['success'] = True

				except Exception as e:
					data['success'] = False
					data['exception'] = '%s' % e

		except:
			print 'No customer for %s found!' % request.user.username
			try:
				print '\t--> attempting to create user.'
				customer = Customer.create(user=request.user, card=request.POST['stripeToken'])
				data['success'] = True

			except Exception as e:
				print e
				data['success'] = False
				data['exception'] = '%s' % e

		return self.render_json_response(data)

	def delete_ajax(self, request, *args, **kwargs):

		data = {}

		try:
			print 'Trying to delete!'
			customer = request.user.customer
			stripe_customer = customer.stripe_customer
			card = stripe_customer.cards['data'][0]['id']

			print '\t--> deleting from stripe API'
			#Delete via API on stripe
			stripe_customer.cards.retrieve(card).delete()

			print '\t--> syncing locally'
			#Also clear this on our model
			customer.sync()

			data['success'] = True
			data['message'] = 'Card successfully deleted'

		except Exception as e:
			data['success'] = False
			data['message'] = '%s' % e

		return self.render_json_response(data)



class PaymentsView(TemplateView):
	template_name = "my-payments.html"

	def get_context_data(self, **kwargs):
		context = super(PaymentsView, self).get_context_data(**kwargs)

		context['plans'] = [
			{'name':k.name(), 'price':'$%s/%s' % (v['price'], v['interval'])} for k, v in settings.PAYMENTS_PLANS.iteritems()
			]    	


		cats = AddonCategory.objects.all()
		addons = AddonType.objects.all()

		addon_categories = [{'name':c.name, 'addons':filter(lambda x: x.category == c, addons)} for c in cats]
		context['addon_categories'] = addon_categories

		return context

class AJAXCancelPlanView(views.JSONResponseMixin, views.AjaxResponseMixin, View):
	def post_ajax(self, request, *args, **kwargs):
		data = {}
		try:			
			request.user.customer.cancel()
			data['success'] = True

		except:
			data['success'] = False

		return self.render_json_response(data)

class AJAXUpgradePlanView(views.JSONResponseMixin, views.AjaxResponseMixin, View):
	def post_ajax(self, request, *args, **kwargs):
		data = {}
		plan = request.POST['plan']

		if plan == 'monthly' and request.user.customer.current_subscription.plan == 'yearly':
			data['success'] = False
			data['message'] = 'Downgrading from existing premium yearly to monthly membership is not permitted.'
			return self.render_json_response(data)

		else:
			try:		
				s=request.user.customer.subscribe(plan)
				print s
				data['success'] = True
			except Exception as e:
				data['success'] = False
				data['message'] = '%s' % e
			return self.render_json_response(data)		