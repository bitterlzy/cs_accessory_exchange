import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

const ITEM_DEFINITIONS = [
  // === 匕首 (Knives) ===
  { name: "★ Karambit | Doppler", category: "knife", weaponType: "Karambit", skinName: "Doppler", rarity: "covert", marketHashName: "★ Karambit | Doppler" },
  { name: "★ Karambit | Tiger Tooth", category: "knife", weaponType: "Karambit", skinName: "Tiger Tooth", rarity: "covert", marketHashName: "★ Karambit | Tiger Tooth" },
  { name: "★ Bayonet | Doppler", category: "knife", weaponType: "Bayonet", skinName: "Doppler", rarity: "covert", marketHashName: "★ Bayonet | Doppler" },
  { name: "★ Bayonet | Rust Coat", category: "knife", weaponType: "Bayonet", skinName: "Rust Coat", rarity: "covert", marketHashName: "★ Bayonet | Rust Coat" },
  { name: "★ M9 Bayonet | Doppler", category: "knife", weaponType: "M9 Bayonet", skinName: "Doppler", rarity: "covert", marketHashName: "★ M9 Bayonet | Doppler" },
  { name: "★ M9 Bayonet | Fade", category: "knife", weaponType: "M9 Bayonet", skinName: "Fade", rarity: "covert", marketHashName: "★ M9 Bayonet | Fade" },
  { name: "★ Butterfly Knife | Fade", category: "knife", weaponType: "Butterfly Knife", skinName: "Fade", rarity: "covert", marketHashName: "★ Butterfly Knife | Fade" },
  { name: "★ Butterfly Knife | Doppler", category: "knife", weaponType: "Butterfly Knife", skinName: "Doppler", rarity: "covert", marketHashName: "★ Butterfly Knife | Doppler" },
  { name: "★ Talon Knife | Doppler", category: "knife", weaponType: "Talon Knife", skinName: "Doppler", rarity: "covert", marketHashName: "★ Talon Knife | Doppler" },
  { name: "★ Stiletto Knife | Doppler", category: "knife", weaponType: "Stiletto Knife", skinName: "Doppler", rarity: "covert", marketHashName: "★ Stiletto Knife | Doppler" },
  { name: "★ Ursus Knife | Fade", category: "knife", weaponType: "Ursus Knife", skinName: "Fade", rarity: "covert", marketHashName: "★ Ursus Knife | Fade" },
  { name: "★ Navaja Knife | Doppler", category: "knife", weaponType: "Navaja Knife", skinName: "Doppler", rarity: "covert", marketHashName: "★ Navaja Knife | Doppler" },

  // === AK-47 ===
  { name: "AK-47 | Redline", category: "weapon", weaponType: "AK-47", skinName: "Redline", rarity: "classified", marketHashName: "AK-47 | Redline" },
  { name: "AK-47 | Vulcan", category: "weapon", weaponType: "AK-47", skinName: "Vulcan", rarity: "covert", marketHashName: "AK-47 | Vulcan" },
  { name: "AK-47 | Fire Serpent", category: "weapon", weaponType: "AK-47", skinName: "Fire Serpent", rarity: "covert", marketHashName: "AK-47 | Fire Serpent" },
  { name: "AK-47 | The Empress", category: "weapon", weaponType: "AK-47", skinName: "The Empress", rarity: "covert", marketHashName: "AK-47 | The Empress" },
  { name: "AK-47 | Neon Rider", category: "weapon", weaponType: "AK-47", skinName: "Neon Rider", rarity: "covert", marketHashName: "AK-47 | Neon Rider" },
  { name: "AK-47 | Bloodsport", category: "weapon", weaponType: "AK-47", skinName: "Bloodsport", rarity: "covert", marketHashName: "AK-47 | Bloodsport" },
  { name: "AK-47 | Asiimov", category: "weapon", weaponType: "AK-47", skinName: "Asiimov", rarity: "restricted", marketHashName: "AK-47 | Asiimov" },
  { name: "AK-47 | Ice Coaled", category: "weapon", weaponType: "AK-47", skinName: "Ice Coaled", rarity: "restricted", marketHashName: "AK-47 | Ice Coaled" },

  // === M4A4 ===
  { name: "M4A4 | Howl", category: "weapon", weaponType: "M4A4", skinName: "Howl", rarity: "covert", marketHashName: "M4A4 | Howl" },
  { name: "M4A4 | Poseidon", category: "weapon", weaponType: "M4A4", skinName: "Poseidon", rarity: "covert", marketHashName: "M4A4 | Poseidon" },
  { name: "M4A4 | Neo-Noir", category: "weapon", weaponType: "M4A4", skinName: "Neo-Noir", rarity: "covert", marketHashName: "M4A4 | Neo-Noir" },
  { name: "M4A4 | The Emperor", category: "weapon", weaponType: "M4A4", skinName: "The Emperor", rarity: "classified", marketHashName: "M4A4 | The Emperor" },
  { name: "M4A4 | Asiimov", category: "weapon", weaponType: "M4A4", skinName: "Asiimov", rarity: "classified", marketHashName: "M4A4 | Asiimov" },
  { name: "M4A4 | Dragon King", category: "weapon", weaponType: "M4A4", skinName: "Dragon King", rarity: "classified", marketHashName: "M4A4 | Dragon King" },

  // === M4A1-S ===
  { name: "M4A1-S | Knight", category: "weapon", weaponType: "M4A1-S", skinName: "Knight", rarity: "covert", marketHashName: "M4A1-S | Knight" },
  { name: "M4A1-S | Printstream", category: "weapon", weaponType: "M4A1-S", skinName: "Printstream", rarity: "covert", marketHashName: "M4A1-S | Printstream" },
  { name: "M4A1-S | Mecha Industries", category: "weapon", weaponType: "M4A1-S", skinName: "Mecha Industries", rarity: "classified", marketHashName: "M4A1-S | Mecha Industries" },
  { name: "M4A1-S | Hyper Beast", category: "weapon", weaponType: "M4A1-S", skinName: "Hyper Beast", rarity: "classified", marketHashName: "M4A1-S | Hyper Beast" },
  { name: "M4A1-S | Decimator", category: "weapon", weaponType: "M4A1-S", skinName: "Decimator", rarity: "classified", marketHashName: "M4A1-S | Decimator" },

  // === AWP ===
  { name: "AWP | Dragon Lore", category: "weapon", weaponType: "AWP", skinName: "Dragon Lore", rarity: "covert", marketHashName: "AWP | Dragon Lore" },
  { name: "AWP | Gungnir", category: "weapon", weaponType: "AWP", skinName: "Gungnir", rarity: "covert", marketHashName: "AWP | Gungnir" },
  { name: "AWP | Medusa", category: "weapon", weaponType: "AWP", skinName: "Medusa", rarity: "covert", marketHashName: "AWP | Medusa" },
  { name: "AWP | Asiimov", category: "weapon", weaponType: "AWP", skinName: "Asiimov", rarity: "covert", marketHashName: "AWP | Asiimov" },
  { name: "AWP | Oni Taiji", category: "weapon", weaponType: "AWP", skinName: "Oni Taiji", rarity: "covert", marketHashName: "AWP | Oni Taiji" },
  { name: "AWP | Hyper Beast", category: "weapon", weaponType: "AWP", skinName: "Hyper Beast", rarity: "covert", marketHashName: "AWP | Hyper Beast" },
  { name: "AWP | Fade", category: "weapon", weaponType: "AWP", skinName: "Fade", rarity: "covert", marketHashName: "AWP | Fade" },
  { name: "AWP | Chrome Cannon", category: "weapon", weaponType: "AWP", skinName: "Chrome Cannon", rarity: "classified", marketHashName: "AWP | Chrome Cannon" },

  // === Desert Eagle ===
  { name: "Desert Eagle | Blaze", category: "weapon", weaponType: "Desert Eagle", skinName: "Blaze", rarity: "classified", marketHashName: "Desert Eagle | Blaze" },
  { name: "Desert Eagle | Code Red", category: "weapon", weaponType: "Desert Eagle", skinName: "Code Red", rarity: "classified", marketHashName: "Desert Eagle | Code Red" },
  { name: "Desert Eagle | Printstream", category: "weapon", weaponType: "Desert Eagle", skinName: "Printstream", rarity: "covert", marketHashName: "Desert Eagle | Printstream" },
  { name: "Desert Eagle | Ocean Drive", category: "weapon", weaponType: "Desert Eagle", skinName: "Ocean Drive", rarity: "covert", marketHashName: "Desert Eagle | Ocean Drive" },
  { name: "Desert Eagle | Koi", category: "weapon", weaponType: "Desert Eagle", skinName: "Koi", rarity: "classified", marketHashName: "Desert Eagle | Koi" },

  // === USP-S ===
  { name: "USP-S | Kill Confirmed", category: "weapon", weaponType: "USP-S", skinName: "Kill Confirmed", rarity: "covert", marketHashName: "USP-S | Kill Confirmed" },
  { name: "USP-S | Printstream", category: "weapon", weaponType: "USP-S", skinName: "Printstream", rarity: "covert", marketHashName: "USP-S | Printstream" },
  { name: "USP-S | The Traitor", category: "weapon", weaponType: "USP-S", skinName: "The Traitor", rarity: "covert", marketHashName: "USP-S | The Traitor" },
  { name: "USP-S | Orion", category: "weapon", weaponType: "USP-S", skinName: "Orion", rarity: "classified", marketHashName: "USP-S | Orion" },
  { name: "USP-S | Cortex", category: "weapon", weaponType: "USP-S", skinName: "Cortex", rarity: "classified", marketHashName: "USP-S | Cortex" },

  // === Glock-18 ===
  { name: "Glock-18 | Fade", category: "weapon", weaponType: "Glock-18", skinName: "Fade", rarity: "covert", marketHashName: "Glock-18 | Fade" },
  { name: "Glock-18 | Twilight Galaxy", category: "weapon", weaponType: "Glock-18", skinName: "Twilight Galaxy", rarity: "classified", marketHashName: "Glock-18 | Twilight Galaxy" },
  { name: "Glock-18 | Bullet Queen", category: "weapon", weaponType: "Glock-18", skinName: "Bullet Queen", rarity: "classified", marketHashName: "Glock-18 | Bullet Queen" },
  { name: "Glock-18 | Water Elemental", category: "weapon", weaponType: "Glock-18", skinName: "Water Elemental", rarity: "classified", marketHashName: "Glock-18 | Water Elemental" },

  // === SSG 08 ===
  { name: "SSG 08 | Dragonfire", category: "weapon", weaponType: "SSG 08", skinName: "Dragonfire", rarity: "classified", marketHashName: "SSG 08 | Dragonfire" },
  { name: "SSG 08 | Death Strike", category: "weapon", weaponType: "SSG 08", skinName: "Death Strike", rarity: "mil-spec", marketHashName: "SSG 08 | Death Strike" },

  // === 手套 (Gloves) ===
  { name: "★ Sport Gloves | Pandora's Box", category: "gloves", weaponType: "Sport Gloves", skinName: "Pandora's Box", rarity: "special", marketHashName: "★ Sport Gloves | Pandora's Box" },
  { name: "★ Sport Gloves | Vice", category: "gloves", weaponType: "Sport Gloves", skinName: "Vice", rarity: "special", marketHashName: "★ Sport Gloves | Vice" },
  { name: "★ Driver Gloves | Crimson Weave", category: "gloves", weaponType: "Driver Gloves", skinName: "Crimson Weave", rarity: "special", marketHashName: "★ Driver Gloves | Crimson Weave" },
  { name: "★ Hand Wraps | Cobalt Skulls", category: "gloves", weaponType: "Hand Wraps", skinName: "Cobalt Skulls", rarity: "special", marketHashName: "★ Hand Wraps | Cobalt Skulls" },
  { name: "★ Moto Gloves | Spearmint", category: "gloves", weaponType: "Moto Gloves", skinName: "Spearmint", rarity: "special", marketHashName: "★ Moto Gloves | Spearmint" },
  { name: "★ Moto Gloves | Boom!", category: "gloves", weaponType: "Moto Gloves", skinName: "Boom!", rarity: "special", marketHashName: "★ Moto Gloves | Boom!" },
  { name: "★ Specialist Gloves | Fade", category: "gloves", weaponType: "Specialist Gloves", skinName: "Fade", rarity: "special", marketHashName: "★ Specialist Gloves | Fade" },

  // === MAC-10 ===
  { name: "MAC-10 | Neon Rider", category: "weapon", weaponType: "MAC-10", skinName: "Neon Rider", rarity: "classified", marketHashName: "MAC-10 | Neon Rider" },
  { name: "MAC-10 | Stalker", category: "weapon", weaponType: "MAC-10", skinName: "Stalker", rarity: "restricted", marketHashName: "MAC-10 | Stalker" },

  // === P250 ===
  { name: "P250 | Franklin", category: "weapon", weaponType: "P250", skinName: "Franklin", rarity: "restricted", marketHashName: "P250 | Franklin" },

  // === Five-SeveN ===
  { name: "Five-SeveN | Fairy Tale", category: "weapon", weaponType: "Five-SeveN", skinName: "Fairy Tale", rarity: "classified", marketHashName: "Five-SeveN | Fairy Tale" },
];

async function main() {
  console.log("🌱 Seeding item definitions...");

  for (const def of ITEM_DEFINITIONS) {
    await prisma.itemDefinition.upsert({
      where: { marketHashName: def.marketHashName },
      update: {},
      create: def,
    });
  }

  const count = await prisma.itemDefinition.count();
  console.log(`✅ Seeded ${count} item definitions`);
}

main()
  .catch((e) => {
    console.error("❌ Seed failed:", e);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
