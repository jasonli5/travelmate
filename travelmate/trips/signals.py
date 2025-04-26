from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import TripInvite

@receiver(user_logged_in)
def apply_pending_invites(sender, request, user, **kwargs):
    invites = TripInvite.objects.filter(email=user.email)
    for invite in invites:
        invite.trip.collaborators.add(user)
    invites.delete()