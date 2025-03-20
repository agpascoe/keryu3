from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from custodians.models import Custodian
from subjects.models import Subject, SubjectQR
from django.db import transaction

class Command(BaseCommand):
    help = 'Deletes all records from the database except admin users'

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                # Get admin users to preserve
                admin_users = User.objects.filter(is_staff=True)
                admin_usernames = list(admin_users.values_list('username', flat=True))
                
                # Delete all QR codes
                qr_count = SubjectQR.objects.all().count()
                SubjectQR.objects.all().delete()
                
                # Delete all subjects
                subject_count = Subject.objects.all().count()
                Subject.objects.all().delete()
                
                # Delete non-admin custodians and users
                non_admin_users = User.objects.filter(is_staff=False)
                custodian_count = Custodian.objects.filter(user__in=non_admin_users).count()
                non_admin_users.delete()  # This will cascade delete associated custodians
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully deleted all records except admin users:\n'
                        f'- Preserved admin users: {", ".join(admin_usernames)}\n'
                        f'- Deleted {qr_count} QR codes\n'
                        f'- Deleted {subject_count} subjects\n'
                        f'- Deleted {custodian_count} custodians and their associated users'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'An error occurred: {str(e)}')
            ) 