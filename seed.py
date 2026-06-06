"""装备数据字典种子脚本"""
from app.database import SessionLocal, engine, Base
from app.models import ItemDefinition, ItemCategory, ItemRarity

# 热门 CS2 饰品数据 (70+)
ITEM_DEFINITIONS = [
    # === 匕首 ===
    ("★ Karambit | Doppler", ItemCategory.knife, "Karambit", "Doppler", ItemRarity.covert, "★ Karambit | Doppler"),
    ("★ Karambit | Tiger Tooth", ItemCategory.knife, "Karambit", "Tiger Tooth", ItemRarity.covert, "★ Karambit | Tiger Tooth"),
    ("★ Karambit | Fade", ItemCategory.knife, "Karambit", "Fade", ItemRarity.covert, "★ Karambit | Fade"),
    ("★ Bayonet | Doppler", ItemCategory.knife, "Bayonet", "Doppler", ItemRarity.covert, "★ Bayonet | Doppler"),
    ("★ Bayonet | Rust Coat", ItemCategory.knife, "Bayonet", "Rust Coat", ItemRarity.covert, "★ Bayonet | Rust Coat"),
    ("★ M9 Bayonet | Doppler", ItemCategory.knife, "M9 Bayonet", "Doppler", ItemRarity.covert, "★ M9 Bayonet | Doppler"),
    ("★ M9 Bayonet | Fade", ItemCategory.knife, "M9 Bayonet", "Fade", ItemRarity.covert, "★ M9 Bayonet | Fade"),
    ("★ Butterfly Knife | Fade", ItemCategory.knife, "Butterfly Knife", "Fade", ItemRarity.covert, "★ Butterfly Knife | Fade"),
    ("★ Butterfly Knife | Doppler", ItemCategory.knife, "Butterfly Knife", "Doppler", ItemRarity.covert, "★ Butterfly Knife | Doppler"),
    ("★ Talon Knife | Doppler", ItemCategory.knife, "Talon Knife", "Doppler", ItemRarity.covert, "★ Talon Knife | Doppler"),
    ("★ Stiletto Knife | Doppler", ItemCategory.knife, "Stiletto Knife", "Doppler", ItemRarity.covert, "★ Stiletto Knife | Doppler"),
    ("★ Ursus Knife | Fade", ItemCategory.knife, "Ursus Knife", "Fade", ItemRarity.covert, "★ Ursus Knife | Fade"),
    ("★ Navaja Knife | Doppler", ItemCategory.knife, "Navaja Knife", "Doppler", ItemRarity.covert, "★ Navaja Knife | Doppler"),
    ("★ Classic Knife | Fade", ItemCategory.knife, "Classic Knife", "Fade", ItemRarity.covert, "★ Classic Knife | Fade"),

    # === AK-47 ===
    ("AK-47 | Redline", ItemCategory.weapon, "AK-47", "Redline", ItemRarity.classified, "AK-47 | Redline"),
    ("AK-47 | Vulcan", ItemCategory.weapon, "AK-47", "Vulcan", ItemRarity.covert, "AK-47 | Vulcan"),
    ("AK-47 | Fire Serpent", ItemCategory.weapon, "AK-47", "Fire Serpent", ItemRarity.covert, "AK-47 | Fire Serpent"),
    ("AK-47 | The Empress", ItemCategory.weapon, "AK-47", "The Empress", ItemRarity.covert, "AK-47 | The Empress"),
    ("AK-47 | Neon Rider", ItemCategory.weapon, "AK-47", "Neon Rider", ItemRarity.covert, "AK-47 | Neon Rider"),
    ("AK-47 | Bloodsport", ItemCategory.weapon, "AK-47", "Bloodsport", ItemRarity.covert, "AK-47 | Bloodsport"),
    ("AK-47 | Asiimov", ItemCategory.weapon, "AK-47", "Asiimov", ItemRarity.restricted, "AK-47 | Asiimov"),
    ("AK-47 | Ice Coaled", ItemCategory.weapon, "AK-47", "Ice Coaled", ItemRarity.restricted, "AK-47 | Ice Coaled"),
    ("AK-47 | Uncharted", ItemCategory.weapon, "AK-47", "Uncharted", ItemRarity.restricted, "AK-47 | Uncharted"),

    # === M4A4 ===
    ("M4A4 | Howl", ItemCategory.weapon, "M4A4", "Howl", ItemRarity.covert, "M4A4 | Howl"),
    ("M4A4 | Poseidon", ItemCategory.weapon, "M4A4", "Poseidon", ItemRarity.covert, "M4A4 | Poseidon"),
    ("M4A4 | Neo-Noir", ItemCategory.weapon, "M4A4", "Neo-Noir", ItemRarity.covert, "M4A4 | Neo-Noir"),
    ("M4A4 | The Emperor", ItemCategory.weapon, "M4A4", "The Emperor", ItemRarity.classified, "M4A4 | The Emperor"),
    ("M4A4 | Asiimov", ItemCategory.weapon, "M4A4", "Asiimov", ItemRarity.classified, "M4A4 | Asiimov"),
    ("M4A4 | Dragon King", ItemCategory.weapon, "M4A4", "Dragon King", ItemRarity.classified, "M4A4 | Dragon King"),

    # === M4A1-S ===
    ("M4A1-S | Printstream", ItemCategory.weapon, "M4A1-S", "Printstream", ItemRarity.covert, "M4A1-S | Printstream"),
    ("M4A1-S | Mecha Industries", ItemCategory.weapon, "M4A1-S", "Mecha Industries", ItemRarity.classified, "M4A1-S | Mecha Industries"),
    ("M4A1-S | Hyper Beast", ItemCategory.weapon, "M4A1-S", "Hyper Beast", ItemRarity.classified, "M4A1-S | Hyper Beast"),
    ("M4A1-S | Decimator", ItemCategory.weapon, "M4A1-S", "Decimator", ItemRarity.classified, "M4A1-S | Decimator"),
    ("M4A1-S | Golden Coil", ItemCategory.weapon, "M4A1-S", "Golden Coil", ItemRarity.classified, "M4A1-S | Golden Coil"),

    # === AWP ===
    ("AWP | Dragon Lore", ItemCategory.weapon, "AWP", "Dragon Lore", ItemRarity.covert, "AWP | Dragon Lore"),
    ("AWP | Gungnir", ItemCategory.weapon, "AWP", "Gungnir", ItemRarity.covert, "AWP | Gungnir"),
    ("AWP | Medusa", ItemCategory.weapon, "AWP", "Medusa", ItemRarity.covert, "AWP | Medusa"),
    ("AWP | Asiimov", ItemCategory.weapon, "AWP", "Asiimov", ItemRarity.covert, "AWP | Asiimov"),
    ("AWP | Oni Taiji", ItemCategory.weapon, "AWP", "Oni Taiji", ItemRarity.covert, "AWP | Oni Taiji"),
    ("AWP | Hyper Beast", ItemCategory.weapon, "AWP", "Hyper Beast", ItemRarity.covert, "AWP | Hyper Beast"),
    ("AWP | Fade", ItemCategory.weapon, "AWP", "Fade", ItemRarity.covert, "AWP | Fade"),
    ("AWP | Chrome Cannon", ItemCategory.weapon, "AWP", "Chrome Cannon", ItemRarity.classified, "AWP | Chrome Cannon"),

    # === Desert Eagle ===
    ("Desert Eagle | Blaze", ItemCategory.weapon, "Desert Eagle", "Blaze", ItemRarity.classified, "Desert Eagle | Blaze"),
    ("Desert Eagle | Code Red", ItemCategory.weapon, "Desert Eagle", "Code Red", ItemRarity.classified, "Desert Eagle | Code Red"),
    ("Desert Eagle | Printstream", ItemCategory.weapon, "Desert Eagle", "Printstream", ItemRarity.covert, "Desert Eagle | Printstream"),
    ("Desert Eagle | Ocean Drive", ItemCategory.weapon, "Desert Eagle", "Ocean Drive", ItemRarity.covert, "Desert Eagle | Ocean Drive"),
    ("Desert Eagle | Koi", ItemCategory.weapon, "Desert Eagle", "Koi", ItemRarity.classified, "Desert Eagle | Koi"),

    # === USP-S ===
    ("USP-S | Kill Confirmed", ItemCategory.weapon, "USP-S", "Kill Confirmed", ItemRarity.covert, "USP-S | Kill Confirmed"),
    ("USP-S | Printstream", ItemCategory.weapon, "USP-S", "Printstream", ItemRarity.covert, "USP-S | Printstream"),
    ("USP-S | The Traitor", ItemCategory.weapon, "USP-S", "The Traitor", ItemRarity.covert, "USP-S | The Traitor"),
    ("USP-S | Orion", ItemCategory.weapon, "USP-S", "Orion", ItemRarity.classified, "USP-S | Orion"),
    ("USP-S | Cortex", ItemCategory.weapon, "USP-S", "Cortex", ItemRarity.classified, "USP-S | Cortex"),

    # === Glock-18 ===
    ("Glock-18 | Fade", ItemCategory.weapon, "Glock-18", "Fade", ItemRarity.covert, "Glock-18 | Fade"),
    ("Glock-18 | Twilight Galaxy", ItemCategory.weapon, "Glock-18", "Twilight Galaxy", ItemRarity.classified, "Glock-18 | Twilight Galaxy"),
    ("Glock-18 | Bullet Queen", ItemCategory.weapon, "Glock-18", "Bullet Queen", ItemRarity.classified, "Glock-18 | Bullet Queen"),
    ("Glock-18 | Water Elemental", ItemCategory.weapon, "Glock-18", "Water Elemental", ItemRarity.classified, "Glock-18 | Water Elemental"),

    # === 手套 ===
    ("★ Sport Gloves | Pandora's Box", ItemCategory.gloves, "Sport Gloves", "Pandora's Box", ItemRarity.special, "★ Sport Gloves | Pandora's Box"),
    ("★ Sport Gloves | Vice", ItemCategory.gloves, "Sport Gloves", "Vice", ItemRarity.special, "★ Sport Gloves | Vice"),
    ("★ Driver Gloves | Crimson Weave", ItemCategory.gloves, "Driver Gloves", "Crimson Weave", ItemRarity.special, "★ Driver Gloves | Crimson Weave"),
    ("★ Hand Wraps | Cobalt Skulls", ItemCategory.gloves, "Hand Wraps", "Cobalt Skulls", ItemRarity.special, "★ Hand Wraps | Cobalt Skulls"),
    ("★ Moto Gloves | Spearmint", ItemCategory.gloves, "Moto Gloves", "Spearmint", ItemRarity.special, "★ Moto Gloves | Spearmint"),
    ("★ Moto Gloves | Boom!", ItemCategory.gloves, "Moto Gloves", "Boom!", ItemRarity.special, "★ Moto Gloves | Boom!"),
    ("★ Specialist Gloves | Fade", ItemCategory.gloves, "Specialist Gloves", "Fade", ItemRarity.special, "★ Specialist Gloves | Fade"),
    ("★ Bloodhound Gloves | Bronzed", ItemCategory.gloves, "Bloodhound Gloves", "Bronzed", ItemRarity.special, "★ Bloodhound Gloves | Bronzed"),

    # === MAC-10 ===
    ("MAC-10 | Neon Rider", ItemCategory.weapon, "MAC-10", "Neon Rider", ItemRarity.classified, "MAC-10 | Neon Rider"),
    ("MAC-10 | Stalker", ItemCategory.weapon, "MAC-10", "Stalker", ItemRarity.restricted, "MAC-10 | Stalker"),

    # === P250 ===
    ("P250 | Franklin", ItemCategory.weapon, "P250", "Franklin", ItemRarity.restricted, "P250 | Franklin"),

    # === Five-SeveN ===
    ("Five-SeveN | Fairy Tale", ItemCategory.weapon, "Five-SeveN", "Fairy Tale", ItemRarity.classified, "Five-SeveN | Fairy Tale"),

    # === AUG / SG 553 ===
    ("AUG | Akihabara Accept", ItemCategory.weapon, "AUG", "Akihabara Accept", ItemRarity.covert, "AUG | Akihabara Accept"),
    ("SG 553 | Integrale", ItemCategory.weapon, "SG 553", "Integrale", ItemRarity.covert, "SG 553 | Integrale"),

    # === FAMAS ===
    ("FAMAS | Eye of the Storm", ItemCategory.weapon, "FAMAS", "Eye of the Storm", ItemRarity.restricted, "FAMAS | Eye of the Storm"),

    # === 贴纸示例 ===
    ("Sticker | s1mple (Gold) | Antwerp 2022", ItemCategory.sticker, "Sticker", "s1mple (Gold)", ItemRarity.exceedingly_rare, "Sticker | s1mple (Gold) | Antwerp 2022"),
    ("Sticker | ZywOo (Gold) | Paris 2023", ItemCategory.sticker, "Sticker", "ZywOo (Gold)", ItemRarity.exceedingly_rare, "Sticker | ZywOo (Gold) | Paris 2023"),

    # === 探员 ===
    ("Agent | Ava (Imperial Officer)", ItemCategory.agent, "Agent", "Ava", ItemRarity.restricted, "Agent | Ava (Imperial Officer)"),
    ("Agent | The Elite Mr. Muhlik", ItemCategory.agent, "Agent", "The Elite Mr. Muhlik", ItemRarity.restricted, "Agent | The Elite Mr. Muhlik"),
]


def seed():
    """填充装备数据字典"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        count = 0
        for name, category, weapon_type, skin_name, rarity, market_hash in ITEM_DEFINITIONS:
            exists = db.query(ItemDefinition).filter(
                ItemDefinition.market_hash_name == market_hash
            ).first()
            if not exists:
                db.add(ItemDefinition(
                    name=name,
                    category=category,
                    weapon_type=weapon_type,
                    skin_name=skin_name,
                    rarity=rarity,
                    market_hash_name=market_hash,
                ))
                count += 1

        db.commit()
        total = db.query(ItemDefinition).count()
        print(f"✅ Seed 完成: 新增 {count} 条, 总计 {total} 条装备定义")
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 正在填充装备数据字典...")
    seed()
