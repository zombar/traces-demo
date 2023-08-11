import os, random, time
import utils as u
import client as c

min_wait = float(os.environ.get("MIN_WAIT_MS", "100")) / 1000
max_wait = float(os.environ.get("MAX_WAIT_MS", "250")) / 1000
log = u.init_logger("demo-client")

providers = [
    "TechnoNova Electronics",
    "AeroGlide Automotive",
    "BioFusion HealthTech",
    "AquaCraft Marine",
    "TerraTech Solutions",
    "CelestialSoft Robotics",
    "QuantumSynth Electronics",
    "UrbanPulse Urbanwear",
    "ZenithNourish Foods",
    "EquiPulse Sports Gear",
    "SwiftWing Aerospace",
    "NovaGlo Beauty Labs",
    "SparkLoom Textiles",
    "Solaris Energy Systems",
    "InfinitySync Tech",
    "TimeWarp Watches",
    "BioBloom AgriTech",
    "DreamWeave Furnishings",
    "LuminaVerse Lighting",
    "AlpineScape Outdoor Gear",
]

items = [
    "NeoWave Smartphones",
    "HyperDrive Electric Cars",
    "BioGlow Skincare Serum",
    "AquaFlow Water Purifiers",
    "TerraSense Smart Garden Sensors",
    "CelestialBots Household Robots",
    "QuantumPulse Gaming Consoles",
    "UrbanFlex Activewear",
    "ZenithBlend Superfood Smoothies",
    "EquiRun Performance Shoes",
    "AeroStream Private Jets",
    "NovaGlam Cosmetics",
    "SparkFusion Fabrics",
    "SolarisSun Solar Panels",
    "InfinityLink VR Headsets",
    "TimeWisp Luxury Watches",
    "BioHarvest Vertical Farms",
    "DreamScape Home Decor",
    "LuminaLux Smart Bulbs",
    "AlpineVenture Camping Gear",
    "NanoGlide Bicycle Innovations",
    "ElectroFlex Fitness Equipment",
    "SkySoar Drones",
    "HydroGlide Watersports Gear",
    "Envirotech Sustainable Packaging",
    "VaporDine Air Purifiers",
    "Photonix Camera Systems",
    "OmniTrax Navigation Devices",
    "AeroFuel Renewable Energy Solutions",
    "CyberHive Data Security Systems",
    "AquaZen Relaxation Devices",
    "BioVita Nutritional Supplements",
    "TerraView Environmental Monitors",
    "NeoSoft Office Ergonomics",
    "CelestialEcho Bluetooth Speakers",
    "QuantumQuest Educational Tablets",
    "UrbanWeave Sustainable Fashion",
    "ZenithMind Meditation Apps",
    "EquiFit Smart Sportswear",
    "NovaRise Morning Essentials",
    "SparkTech Smart Textiles",
    "SolarisCharge Electric Chargers",
    "InfinitySculpt 3D Printers",
    "TimeSync Smart Clocks",
    "BioNest Eco-friendly Homes",
    "DreamWave Sleep Tech",
    "LuminaScape Landscape Lighting",
    "AlpinePeak Mountaineering Equipment",
    "AeroSwift Aeronautic Gear",
    "AquaCruise Luxury Yachts",
]

quantities = [
    -100,
    -75,
    -50,
    -25,
    25,
    50,
    75,
    100,
]

cache = []

while not u.ctx.terminating:
    
    # do a random get 25% of the time
    if len(cache) > 0 and random.randrange(0, 100) <= 25:
        provider_name = random.choice(cache)

        log.info("fetching data for %s" % provider_name)
        c.get_inventory(provider_name)

    # otherwise insert / update something
    else:

        provider_name = random.choice(providers)
        item_name = random.choice(items)
        quantity = random.choices(
            population=quantities,
            weights=(1,2,3,4,5,6,7,8),
            k=1,
        )[0]
        
        if provider_name not in cache:
            cache.append(provider_name)

        log.info("adding data for %s" % provider_name)
        c.update_inventory(
            provider_name=provider_name,
            item_name=item_name,
            quantity=quantity,
        )

    # sleep for a bit
    time.sleep(random.uniform(min_wait, max_wait))