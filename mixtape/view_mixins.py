from .models import Genre
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib import messages
from django.conf import settings


class GenreListMixin(object):

	def get_context_data(self, **kwargs):
		context = super(GenreListMixin, self).get_context_data(**kwargs)
		context['genre_list'] = Genre.objects.all()
		return context

class PaymentRequiredMixin(object):

    def dispatch(self, request, *args, **kwargs):
    	try:
			if self.request.user.customer.card_fingerprint:
				return super(PaymentRequiredMixin, self).dispatch(request, *args, **kwargs)
			else:
				messages.error(self.request, 'Please update card on file before proceeding!')
				return redirect(reverse('update_card'))
        except:
			messages.error(self.request, 'Please update card on file before proceeding!')
			#return redirect(reverse('update_card'))
			return super(PaymentRequiredMixin, self).dispatch(request, *args, **kwargs)
