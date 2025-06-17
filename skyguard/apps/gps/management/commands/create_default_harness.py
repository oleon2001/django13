from django.core.management.base import BaseCommand
from skyguard.gps.tracker.models import SGHarness

class Command(BaseCommand):
    help = 'Creates a default SGHarness if it does not exist'

    def handle(self, *args, **options):
        try:
            harness = SGHarness.objects.get(name="default")
            self.stdout.write(self.style.SUCCESS('Default harness already exists'))
        except SGHarness.DoesNotExist:
            harness = SGHarness(
                name="default",
                in00="PANIC",
                in01="IGNITION",
                in02="",
                in03="",
                in04="",
                in05="",
                in06="BAT_DOK",
                in07="BAT_CHG",
                in08="BAT_FLT",
                in09="",
                in10="",
                in11="",
                in12="",
                in13="",
                in14="",
                in15="",
                out00="MOTOR",
                out01="",
                out02="",
                out03="",
                out04="",
                out05="",
                out06="",
                out07="",
                out08="",
                out09="",
                out10="",
                out11="",
                out12="",
                out13="",
                out14="",
                out15="",
                inputCfg=""
            )
            harness.save()
            self.stdout.write(self.style.SUCCESS('Successfully created default harness')) 