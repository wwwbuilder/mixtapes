Stripe.setPublishableKey(stripe_publishable_key);

function stripeResponseHandler(status, response) {
    if (response.error) {
        console.log('There are errors!');
        console.log(response.error);
        // show the errors on the form
        //alert(response.error.message);
        $(".payment-errors").text(response.error.message);
    } else {
        console.log('SUCCESS!');
        console.log(status);
        console.log(response);
        var form$ = $("#change-card-form");
        // token contains id, last4, and card type
        var token = response['id'];
        // insert the token into the form so it gets submitted to the server
        form$.append("<input type='hidden' name='stripeToken' value='" + token + "'/>");
        // and submit via ajax

        jQuery.ajax({
          url: change_card_url,
          type: 'POST',
          data: form$.serialize(),
          success: function(data) {
            console.log(data.plan);
            location.reload();
            $('#change-card').modal('hide');
            if (data.flag == true){
              window.location ='/premium-publisher/?popup='+data.plan
            }
            else if(window.location.href.split('=').pop() == 'monthly'){
                window.location ='/premium-publisher/?popup=monthly'
            }
            else if(window.location.href.split('=').pop() == 'yearly'){
                window.location ='/premium-publisher/?popup=yearly'
            }
            else{
              window.location ='/payments#success'
            }
          },
          error: function(data) {
            console.log(data)
          }
      });
    }
};

function stripeCreateToken () {
    Stripe.card.createToken($('#change-card-form'), stripeResponseHandler);
};

function deleteCard () {
  if (confirm("Delete this card: Are you sure?")){
    $.ajax({
        url: change_card_url,
        type: 'delete',
        error: function (data) {
          console.log(data)
        }
      }).done(function(data){
        if (data.success == true){
          console.log('SUCCESS!');
          window.location.reload();
        } else {
          console.log('FAILURE!');
          window.location.reload();
        }
      });
  }
};

function upgradePlan (plan) {
  $.ajax({
      url: upgrade_plan_url,
      type: 'post',
      data: {
        'plan':plan
      },
      success: function (data) {        
        if (data.success) {
          window.location.reload();
        } else {
          console.log('ERROR!');
          alert(data.message);
        }
      }
    });
};

function cancelPlan () {
  $.ajax({
      url: cancel_plan_url,
      type: 'post',
      success: function (data) {
        if (data.success) {
          window.location.reload();
        }
      },
      error: function(data){
        console.log(data);
      }
    });
};