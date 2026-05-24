"""Script to generate sample_skus.csv — run once to create the catalog."""

import pandas as pd
import random

random.seed(42)

categories = {
    "Surgical Positioners": [
        ("SP-001", "Universal Lateral Positioner", "Foam lateral positioner for surgical positioning, adjustable straps, adult size"),
        ("SP-002", "Prone Positioning System", "Full body prone positioner set with chest rolls and head support, radiolucent"),
        ("SP-003", "Beach Chair Shoulder Positioner", "Articulating beach chair positioner for shoulder arthroscopy, 400lb capacity"),
        ("SP-004", "Lithotomy Leg Holder Set", "Pair of candy-cane lithotomy leg holders with universal OR table clamps"),
        ("SP-005", "Pediatric Positioner Kit", "Soft foam positioner set for pediatric patients, age 2-12, antimicrobial cover"),
        ("SP-006", "Supine Hip Positioner", "Radiolucent hip positioner for supine total hip replacement procedures"),
        ("SP-007", "Neurosurgery Horseshoe Headrest", "Mayfield-compatible horseshoe headrest with gel padding, MRI conditional"),
        ("SP-008", "Spine Positioner Frame", "Wilson frame spine positioner for lumbar procedures, 500lb capacity"),
        ("SP-009", "Kidney Rest Positioner", "Inflatable kidney rest for lateral flank procedures, foot pump included"),
        ("SP-010", "Cardiac Positioning Wedge Set", "Set of 3 foam wedges for cardiac procedures, autoclavable covers"),
    ],
    "Gel Pads": [
        ("GP-001", "Heel Protector Gel Pad", "Medical-grade silicone gel heel protector, reduces pressure ulcer risk, pair"),
        ("GP-002", "Elbow Gel Pad", "Antimicrobial gel elbow pad, universal size, washable cover"),
        ("GP-003", "Sacral Gel Pad Large", "Large sacral relief gel pad 18x16 inch, 2 inch gel depth"),
        ("GP-004", "OR Table Gel Overlay", "Full OR table gel overlay pad 72x20 inch, 1.5 inch medical gel"),
        ("GP-005", "Wrist Rest Gel Pad", "Ergonomic gel wrist pad for extended surgical procedures, pair"),
        ("GP-006", "Pediatric Gel Overlay", "Pediatric gel table pad 48x18 inch, soft gel formulation"),
        ("GP-007", "Shoulder Gel Pad", "Contoured shoulder gel pad for beach chair positioning, pair"),
        ("GP-008", "Occiput Gel Donut", "Gel donut headrest for supine procedures, reduces occipital pressure"),
        ("GP-009", "Arm Board Gel Pad", "Gel pad cover for surgical arm boards, universal fit, set of 2"),
        ("GP-010", "Face Gel Cushion", "Prone face cushion with gel inserts, multiple apertures for airway access"),
    ],
    "Straps & Restraints": [
        ("SR-001", "OR Safety Strap 2-inch", "2-inch wide OR table safety strap with quick-release buckle, 10ft length"),
        ("SR-002", "Arm Restraint Strap", "Padded arm restraint strap with velcro closure, pair, adult size"),
        ("SR-003", "Leg Holder Strap Set", "Set of 4 leg positioning straps with D-ring attachments"),
        ("SR-004", "Lithotomy Strap", "Padded lithotomy positioning strap, 3-inch wide, pair"),
        ("SR-005", "Chest Restraint Strap", "Diagonal chest safety strap for Trendelenburg positioning, adjustable"),
        ("SR-006", "Pediatric Safety Strap", "Soft pediatric OR safety strap, 1.5 inch, velcro closure"),
        ("SR-007", "Shoulder Positioner Strap", "Non-slip shoulder positioner strap for steep Trendelenburg, pair"),
        ("SR-008", "Universal Table Strap", "Universal OR table strap kit, 5 straps assorted sizes"),
        ("SR-009", "Foam Padded Restraint", "3-inch foam padded arm restraint, hook-and-loop closure, pair"),
        ("SR-010", "Head Holder Strap", "Adjustable head and chin strap for neurosurgery positioning"),
    ],
    "Pressure Relief": [
        ("PR-001", "Anti-Decubitus Foam Pad", "4-inch medical foam OR table pad, egg-crate surface, 72x20 inch"),
        ("PR-002", "Visco-Elastic Overlay", "2-inch visco-elastic memory foam OR overlay, fluid-resistant cover"),
        ("PR-003", "Sequential Compression Device", "Sequential compression device with bilateral leg sleeves, digital controller"),
        ("PR-004", "TED Compression Stocking XL", "Thigh-high TED anti-embolism stockings, extra large, 6-pack"),
        ("PR-005", "TED Compression Stocking M", "Thigh-high TED anti-embolism stockings, medium, 6-pack"),
        ("PR-006", "TED Compression Stocking L", "Thigh-high TED anti-embolism stockings, large, 6-pack"),
        ("PR-007", "Knee-High TED Stocking M", "Knee-high TED anti-embolism stockings, medium, 6-pack"),
        ("PR-008", "Pressure Relief Bootie", "Foam pressure relief bootie for heel and ankle protection, pair"),
        ("PR-009", "Operating Table Mattress", "3-layer OR table mattress with memory foam and gel top, standard size"),
        ("PR-010", "Pressure Mapping System", "Wireless pressure mapping mat for intraoperative pressure monitoring"),
    ],
    "Surgical Accessories": [
        ("SA-001", "Mayfield Skull Clamp", "Three-pin Mayfield skull clamp for cranial surgery, titanium pins"),
        ("SA-002", "Arm Board Padded", "Padded surgical arm board with universal OR table attachment, adult"),
        ("SA-003", "Stirrup Leg Holder", "Allen-style stirrup leg holder with boot, pair, universal table mount"),
        ("SA-004", "Traction Tower", "Orthopedic traction tower for hip arthroscopy, lateral post included"),
        ("SA-005", "IV Arm Board", "Plastic disposable IV arm board with velcro strap, adult, 50-pack"),
        ("SA-006", "OR Table Clamp Set", "Universal OR table side rail clamp set, stainless steel, set of 4"),
        ("SA-007", "Fracture Table Attachment", "Perineal post with gel pad for fracture table use"),
        ("SA-008", "Bean Bag Positioner Large", "Large vacuum bean bag positioner 30x50 inch with pump"),
        ("SA-009", "Bean Bag Positioner Small", "Small vacuum bean bag positioner 20x30 inch with pump"),
        ("SA-010", "Carbon Fiber Arm Sled", "Radiolucent carbon fiber arm sled for robotic surgery, pair"),
    ],
    "Infection Control": [
        ("IC-001", "Surgical Drape Pack", "Disposable universal extremity drape pack, sterile, 10-pack"),
        ("IC-002", "Positioning Cover Set", "Fluid-resistant positioning covers for foam positioners, 20-pack"),
        ("IC-003", "Antimicrobial Positioner Sleeve", "Antimicrobial washable sleeve for surgical positioners, universal fit"),
        ("IC-004", "Sterile Glove Size 7.5", "Sterile surgical gloves size 7.5, latex-free, 50-pair box"),
        ("IC-005", "Sterile Glove Size 8.0", "Sterile surgical gloves size 8.0, latex-free, 50-pair box"),
        ("IC-006", "OR Shoe Cover Pack", "Non-slip OR shoe covers, fluid-resistant, 100-pack"),
        ("IC-007", "Surgical Cap Pack", "Bouffant surgical caps, one-size, 100-pack"),
        ("IC-008", "Fluid Shield Mask", "Level 3 fluid shield surgical mask with eye shield, 25-pack"),
        ("IC-009", "OR Surface Disinfectant", "EPA-approved OR surface disinfectant wipes, 200-count canister"),
        ("IC-010", "Positioner Cleaning Kit", "Enzymatic cleaner concentrate for surgical positioners, 1 gallon"),
    ],
    "Imaging Accessories": [
        ("IA-001", "Radiolucent Arm Board", "Carbon fiber radiolucent arm board for intraoperative imaging, adult"),
        ("IA-002", "C-Arm Drape", "Sterile C-arm fluoroscopy drape, 120x48 inch, 10-pack"),
        ("IA-003", "Radiation Apron Lead-Free", "Lead-free radiation protection apron, 0.5mm equivalent, size M"),
        ("IA-004", "Thyroid Shield", "Lead-free thyroid collar radiation shield, adjustable"),
        ("IA-005", "Dosimeter Badge", "Monthly radiation dosimeter badge, whole body, single unit"),
        ("IA-006", "C-Arm Positioning Block", "Radiolucent foam positioning block for C-arm procedures, set of 3"),
        ("IA-007", "Lead Gloves Pair", "0.5mm lead equivalent surgical radiation gloves, size M, pair"),
        ("IA-008", "Radiation Barrier Screen", "Mobile leaded glass radiation barrier screen, 36x48 inch window"),
        ("IA-009", "Fluoroscopy Positioning Wedge", "Radiolucent fluoroscopy wedge set, 4 angles, carbon fiber"),
        ("IA-010", "Intraoperative Ultrasound Drape", "Sterile intraoperative ultrasound probe drape, 10-pack"),
    ],
    "Warming Systems": [
        ("WS-001", "Forced Air Warming Blanket Adult", "Full body forced-air warming blanket, adult, single use, 10-pack"),
        ("WS-002", "Warming Blanket Pediatric", "Pediatric forced-air warming blanket, single use, 10-pack"),
        ("WS-003", "Underbody Warming Blanket", "Underbody forced-air warming blanket for OR table, 10-pack"),
        ("WS-004", "Fluid Warming Set", "In-line IV fluid warming set, compatible with major warmers, 10-pack"),
        ("WS-005", "Warming Cabinet", "Medical warming cabinet for blankets and fluids, 16 cubic foot"),
        ("WS-006", "Hypothermia Prevention Kit", "Intraoperative hypothermia prevention kit with blanket and hat, 10-pack"),
        ("WS-007", "Temperature Probe Esophageal", "Disposable esophageal temperature probe, adult, 10-pack"),
        ("WS-008", "Skin Temperature Sensor", "Disposable skin temperature sensor for OR monitoring, 20-pack"),
        ("WS-009", "Warm Water Blanket", "Circulating warm water blanket system with pad and controller"),
        ("WS-010", "Resistive Warming Blanket", "Electric resistive warming blanket, reusable, machine washable"),
    ],
    "Patient Transfer": [
        ("PT-001", "Air Transfer Mattress", "Lateral air transfer mattress for patient transfers, 400lb capacity"),
        ("PT-002", "Transfer Board Large", "Large sliding transfer board 72x18 inch, 600lb capacity"),
        ("PT-003", "Transfer Sheet Set", "Low-friction patient transfer sheet set, reusable, 3-pack"),
        ("PT-004", "Patient Roller", "Patient positioning roller for lateral transfers, foam, pair"),
        ("PT-005", "Hover Mat", "Disposable hover transfer mat, single patient use, 5-pack"),
        ("PT-006", "Gait Belt", "Patient transfer gait belt with quick-release buckle, 60 inch"),
        ("PT-007", "Transfer Sling Set", "Bariatric patient transfer sling set, 4 loops, 600lb rated"),
        ("PT-008", "Stretcher Pad Cover", "Fluid-resistant stretcher pad cover, standard size, 10-pack"),
        ("PT-009", "OR Table Positioning Sheet", "Low-friction OR table repositioning sheet, single use, 10-pack"),
        ("PT-010", "Draw Sheet Pack", "Cotton-blend draw sheets for patient positioning, 12-pack"),
    ],
    "Specialty Items": [
        ("SI-001", "Urology Drape Set", "Sterile urology procedure drape set with leg bags, 5-pack"),
        ("SI-002", "Arthroscopy Leg Positioner", "Arthroscopy leg holder with boot for knee procedures"),
        ("SI-003", "Spinal Fusion Positioner", "Jackson table spinal fusion frame with chest and iliac pads"),
        ("SI-004", "Bariatric Positioner Set", "Bariatric surgical positioner set, 600lb rated, all components"),
        ("SI-005", "Neonatal Positioning Aid", "Neonatal gel positioning aid set for NICU, washable covers"),
        ("SI-006", "Eye Surgery Head Rest", "Ophthalmic surgery head rest with adjustable positioning"),
        ("SI-007", "ENT Procedure Headrest", "ENT/otolaryngology procedure headrest with gel pad"),
        ("SI-008", "Robotic Surgery Arm Sled", "Da Vinci compatible arm sled, radiolucent, pair"),
        ("SI-009", "Vascular Surgery Positioner", "Vascular surgery leg positioner set with adjustable supports"),
        ("SI-010", "Obstetric Positioning Wedge", "Left lateral tilt obstetric wedge, 15 degree, foam"),
    ],
}

rows = []
for category, products in categories.items():
    for sku_id, name, description in products:
        stock = random.randint(5, 200)
        unit_price = round(random.uniform(15.0, 850.0), 2)
        rows.append({
            "sku_id": sku_id,
            "name": name,
            "category": category,
            "description": description,
            "unit_price": unit_price,
            "stock": stock,
        })

df = pd.DataFrame(rows)
df.to_csv("/home/claude/order-automation-pipeline/data/sample_skus.csv", index=False)
print(f"Generated {len(df)} SKUs across {len(categories)} categories")
print(df.head())
