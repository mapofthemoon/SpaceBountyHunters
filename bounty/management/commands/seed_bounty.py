
from django.core.management.base import BaseCommand
from bounty.models import WantedCriminal, HuntLog


class Command(BaseCommand):
    help = "Add sample criminals and hunting logs"

    def handle(self, *args, **options):

        criminals = [
            {
                "name": "Zara Voss",
                "nickname": "Nebula Fox",
                "reward": 2500,
                "latitude": 35.5,
                "longitude": 42.1,
                "difficulty": 3,
                "armed": False,
                "has_crew": False,
                "escape_master": True,
            },
            {
                "name": "Kane Draven",
                "nickname": "Void Reaper",
                "reward": 12000,
                "last_known_note": "Near the abandoned space station",
                "difficulty": 9,
                "armed": True,
                "has_crew": True,
                "escape_master": True,
            },
            {
                "name": None,
                "nickname": "Starlight Ghost",
                "reward": 7000,
                "latitude": -15.2,
                "longitude": 78.4,
                "difficulty": 7,
                "armed": False,
                "has_crew": True,
                "escape_master": True,
            },
            {
                "name": "Jax Orion",
                "nickname": "Meteor Jack",
                "reward": 4500,
                "last_known_note": "Last seen at a trading outpost",
                "difficulty": 5,
                "armed": True,
                "has_crew": False,
                "escape_master": False,
            },
            {
                "name": "Luna Krynn",
                "nickname": "Quantum Viper",
                "reward": 9000,
                "latitude": 62.5,
                "longitude": -44.8,
                "difficulty": 8,
                "armed": True,
                "has_crew": True,
                "escape_master": False,
            },
        ]

        for data in criminals:
            WantedCriminal.objects.update_or_create(
                nickname=data["nickname"],
                defaults=data
            )

        logs = [
            ("Nebula Fox", False, "Escaped into the asteroid belt."),
            ("Nebula Fox", True, "Captured near the spaceport."),
            ("Void Reaper", False, "Our ship was heavily damaged."),
            ("Void Reaper", False, "Target escaped with crew."),
            ("Starlight Ghost", False, "Criminal disappeared from radar."),
            ("Starlight Ghost", True, "Captured after a long chase."),
            ("Meteor Jack", False, "Target escaped on a stolen ship."),
            ("Meteor Jack", True, "Captured at the trading station."),
            ("Quantum Viper", False, "Ambush was unsuccessful."),
            ("Quantum Viper", True, "Captured after negotiations."),
        ]

        for nickname, success, notes in logs:
            criminal = WantedCriminal.objects.get(
                nickname=nickname
            )

            HuntLog.objects.get_or_create(
                criminal=criminal,
                notes=notes,
                defaults={"success": success}
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Sample data imported successfully!"
            )
        )

        self.stdout.write(
            f"Criminals: {WantedCriminal.objects.count()}"
        )

        self.stdout.write(
            f"Hunt logs: {HuntLog.objects.count()}"
        )
