"""Sample order emails for demo purposes."""

SAMPLE_EMAILS = [
    {
        "email_id": "EMAIL-001",
        "from": "purchasing@generalhospital.com",
        "subject": "Order Request - Surgical Positioners",
        "body": """Hi,

We need to restock our OR suite. Please process the following order:

- 5x Universal Lateral Positioner (SP-001)
- 3x Prone Positioning System (SP-002)
- 10x OR Safety Strap 2-inch (SR-001)

Please confirm availability and expected delivery timeline.

Best regards,
Sarah Mitchell
Purchasing Department
General Hospital""",
    },
    {
        "email_id": "EMAIL-002",
        "from": "supplies@citymedical.org",
        "subject": "Urgent - Gel Pads and Pressure Relief",
        "body": """Good morning,

We have an urgent requirement for the following items:

- 20 units of OR Table Gel Overlay (GP-004)
- 15 pairs of Heel Protector Gel Pad (GP-001)
- 8 units of Anti-Decubitus Foam Pad (PR-001)

This is urgent — we have a full surgery schedule next week.

Thanks,
James Wong
OR Coordinator
City Medical Center""",
    },
    {
        "email_id": "EMAIL-003",
        "from": "admin@pediatriccare.com",
        "subject": "Pediatric Supply Order",
        "body": """Hello,

Please send us the following pediatric supplies:

- Pediatric Positioner Kit (SP-005) — 4 units
- Pediatric Safety Strap (SR-006) — 6 units
- Pediatric Gel Overlay (GP-006) — 3 units
- Neonatal Positioning Aid (SI-005) — 2 units

Please let us know if any items are out of stock.

Kind regards,
Dr. Lisa Park
Pediatric Surgery Department""",
    },
    {
        "email_id": "EMAIL-004",
        "from": "procurement@regionalmc.net",
        "subject": "Monthly Infection Control Restock",
        "body": """Hi team,

Monthly infection control restock needed:

- OR Shoe Cover Pack (IC-006): 10 packs
- Surgical Cap Pack (IC-007): 8 packs
- Fluid Shield Mask (IC-008): 15 packs
- Positioning Cover Set (IC-002): 5 packs

Please process ASAP.

Mark Davidson
Procurement Manager""",
    },
    {
        "email_id": "EMAIL-005",
        "from": "or.manager@northwestsurgical.com",
        "subject": "Warming and Transfer Equipment",
        "body": """Dear Sales Team,

We need the following equipment for our new OR suite:

- Forced Air Warming Blanket Adult (WS-001): 30 units
- Underbody Warming Blanket (WS-003): 20 units
- Air Transfer Mattress (PT-001): 2 units
- Transfer Board Large (PT-002): 4 units

Please confirm pricing and stock availability.

Regards,
Nancy Thompson
OR Manager""",
    },
    {
        "email_id": "EMAIL-006",  # Ambiguous — vague product references
        "from": "nurse@ambiguoushospital.com",
        "subject": "Need some supplies",
        "body": """Hi,

We need some gel pads — the ones for heels I think? And maybe some straps 
for the OR table. Not sure of the exact product codes.

Also need compression stockings, medium size I believe.

Can you help?

Thanks,
Nurse Johnson""",
    },
]
