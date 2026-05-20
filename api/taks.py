


from email.mime import message
from multiprocessing import context

from celery import shared_task


@shared_task
def send_email_task( otp, recipient_list):
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.conf import settings
    context = {
        'appname': 'HelenPOS',
        'time': '2',
        'otp': otp,
        'toEmail':'Amir Samyan',
      
    }
    html_content = render_to_string('merchant/email/otp_email.html', context)
    msg = EmailMultiAlternatives(
        subject='Your OTP Code',
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()  
    return True


@shared_task
def send_otp(code):
    # Implement your OTP sending logic here
    print(f"Sending OTP: {code}")
    