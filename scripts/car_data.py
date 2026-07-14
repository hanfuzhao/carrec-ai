"""
Car database for CarRec AI recommendation system.

Generates a structured catalog of 70+ vehicles across brands, types,
price tiers, and energy sources. Supports fairness-aware recommendations
by including both mainstream and niche brands.
"""

# AI Attribution: This code was developed with assistance from AI tools
# (TRAE IDE, https://trae.ai). Design and implementation decisions
# are the author's own.

import json
import os
from pathlib import Path


CAR_CATALOG = [
    # Toyota
    {"id": "toyota_camry_2024", "brand": "Toyota", "model": "Camry 2024", "type": "Sedan",
     "price_usd": 27000, "energy": "Hybrid", "seats": 5, "body": "Sedan",
     "use_cases": ["family", "commute", "business"], "highlights": ["reliable", "fuel_efficient", "spacious"],
     "rating": 4.6, "popularity": 0.92, "tags": ["bestseller", "practical"]},
    {"id": "toyota_rav4_2024", "brand": "Toyota", "model": "RAV4 2024", "type": "SUV",
     "price_usd": 30000, "energy": "Hybrid", "seats": 5, "body": "SUV",
     "use_cases": ["family", "outdoor", "commute"], "highlights": ["versatile", "reliable", "cargo_space"],
     "rating": 4.5, "popularity": 0.90, "tags": ["bestseller", "practical"]},
    {"id": "toyota_sienna_2024", "brand": "Toyota", "model": "Sienna 2024", "type": "MPV",
     "price_usd": 38000, "energy": "Hybrid", "seats": 8, "body": "MPV",
     "use_cases": ["family", "road_trip"], "highlights": ["spacious", "fuel_efficient", "family_friendly"],
     "rating": 4.4, "popularity": 0.75, "tags": ["family"]},
    {"id": "toyota_gr_supra_2024", "brand": "Toyota", "model": "GR Supra 2024", "type": "Coupe",
     "price_usd": 46000, "energy": "Gasoline", "seats": 2, "body": "Coupe",
     "use_cases": ["sport", "weekend"], "highlights": ["fast", "sporty", "fun_to_drive"],
     "rating": 4.3, "popularity": 0.45, "tags": ["sport"]},

    # Honda
    {"id": "honda_civic_2024", "brand": "Honda", "model": "Civic 2024", "type": "Sedan",
     "price_usd": 24000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["commute", "family", "city"], "highlights": ["affordable", "reliable", "fuel_efficient"],
     "rating": 4.5, "popularity": 0.88, "tags": ["bestseller", "practical"]},
    {"id": "honda_crv_2024", "brand": "Honda", "model": "CR-V 2024", "type": "SUV",
     "price_usd": 29000, "energy": "Hybrid", "seats": 5, "body": "SUV",
     "use_cases": ["family", "commute", "outdoor"], "highlights": ["spacious", "reliable", "comfortable"],
     "rating": 4.5, "popularity": 0.87, "tags": ["bestseller", "practical"]},
    {"id": "honda_odyssey_2024", "brand": "Honda", "model": "Odyssey 2024", "type": "MPV",
     "price_usd": 39000, "energy": "Gasoline", "seats": 8, "body": "MPV",
     "use_cases": ["family", "road_trip"], "highlights": ["spacious", "family_friendly", "comfortable"],
     "rating": 4.4, "popularity": 0.65, "tags": ["family"]},
    {"id": "honda_accord_2024", "brand": "Honda", "model": "Accord 2024", "type": "Sedan",
     "price_usd": 28000, "energy": "Hybrid", "seats": 5, "body": "Sedan",
     "use_cases": ["family", "business", "commute"], "highlights": ["comfortable", "fuel_efficient", "spacious"],
     "rating": 4.6, "popularity": 0.80, "tags": ["practical"]},

    # Tesla
    {"id": "tesla_model_3_2024", "brand": "Tesla", "model": "Model 3 2024", "type": "Sedan",
     "price_usd": 39000, "energy": "BEV", "seats": 5, "body": "Sedan",
     "use_cases": ["commute", "tech", "eco"], "highlights": ["fast", "tech_loaded", "eco_friendly"],
     "rating": 4.4, "popularity": 0.93, "tags": ["bestseller", "ev", "tech"]},
    {"id": "tesla_model_y_2024", "brand": "Tesla", "model": "Model Y 2024", "type": "SUV",
     "price_usd": 44000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "commute", "tech"], "highlights": ["spacious", "fast", "tech_loaded"],
     "rating": 4.5, "popularity": 0.95, "tags": ["bestseller", "ev", "tech"]},
    {"id": "tesla_model_s_2024", "brand": "Tesla", "model": "Model S 2024", "type": "Sedan",
     "price_usd": 75000, "energy": "BEV", "seats": 5, "body": "Sedan",
     "use_cases": ["luxury", "tech", "sport"], "highlights": ["ultra_fast", "luxurious", "long_range"],
     "rating": 4.7, "popularity": 0.60, "tags": ["luxury", "ev"]},
    {"id": "tesla_cybertruck_2024", "brand": "Tesla", "model": "Cybertruck 2024", "type": "Pickup",
     "price_usd": 80000, "energy": "BEV", "seats": 5, "body": "Pickup",
     "use_cases": ["utility", "offroad", "tech"], "highlights": ["rugged", "fast", "unique_design"],
     "rating": 4.2, "popularity": 0.70, "tags": ["ev", "unique"]},

    # BMW
    {"id": "bmw_3_series_2024", "brand": "BMW", "model": "3 Series 2024", "type": "Sedan",
     "price_usd": 44000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["business", "sport", "luxury"], "highlights": ["sporty", "luxurious", "great_handling"],
     "rating": 4.6, "popularity": 0.72, "tags": ["luxury", "sport"]},
    {"id": "bmw_5_series_2024", "brand": "BMW", "model": "5 Series 2024", "type": "Sedan",
     "price_usd": 55000, "energy": "Hybrid", "seats": 5, "body": "Sedan",
     "use_cases": ["business", "luxury"], "highlights": ["luxurious", "comfortable", "tech_loaded"],
     "rating": 4.7, "popularity": 0.65, "tags": ["luxury"]},
    {"id": "bmw_x5_2024", "brand": "BMW", "model": "X5 2024", "type": "SUV",
     "price_usd": 65000, "energy": "Hybrid", "seats": 5, "body": "SUV",
     "use_cases": ["family", "luxury", "outdoor"], "highlights": ["luxurious", "powerful", "spacious"],
     "rating": 4.6, "popularity": 0.70, "tags": ["luxury"]},
    {"id": "bmw_ix_2024", "brand": "BMW", "model": "iX 2024", "type": "SUV",
     "price_usd": 87000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["luxury", "eco", "tech"], "highlights": ["luxurious", "long_range", "tech_loaded"],
     "rating": 4.5, "popularity": 0.40, "tags": ["luxury", "ev"]},

    # Mercedes-Benz
    {"id": "mercedes_c_class_2024", "brand": "Mercedes-Benz", "model": "C-Class 2024", "type": "Sedan",
     "price_usd": 46000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["business", "luxury"], "highlights": ["luxurious", "comfortable", "elegant"],
     "rating": 4.6, "popularity": 0.70, "tags": ["luxury"]},
    {"id": "mercedes_e_class_2024", "brand": "Mercedes-Benz", "model": "E-Class 2024", "type": "Sedan",
     "price_usd": 58000, "energy": "Hybrid", "seats": 5, "body": "Sedan",
     "use_cases": ["business", "luxury"], "highlights": ["ultra_luxurious", "comfortable", "tech_loaded"],
     "rating": 4.8, "popularity": 0.62, "tags": ["luxury"]},
    {"id": "mercedes_gle_2024", "brand": "Mercedes-Benz", "model": "GLE 2024", "type": "SUV",
     "price_usd": 62000, "energy": "Hybrid", "seats": 5, "body": "SUV",
     "use_cases": ["family", "luxury", "outdoor"], "highlights": ["luxurious", "spacious", "powerful"],
     "rating": 4.6, "popularity": 0.68, "tags": ["luxury"]},
    {"id": "mercedes_eqs_2024", "brand": "Mercedes-Benz", "model": "EQS 2024", "type": "Sedan",
     "price_usd": 105000, "energy": "BEV", "seats": 5, "body": "Sedan",
     "use_cases": ["luxury", "eco", "tech"], "highlights": ["ultra_luxurious", "long_range", "tech_loaded"],
     "rating": 4.7, "popularity": 0.35, "tags": ["luxury", "ev"]},

    # Audi
    {"id": "audi_a4_2024", "brand": "Audi", "model": "A4 2024", "type": "Sedan",
     "price_usd": 41000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["business", "luxury"], "highlights": ["luxurious", "great_handling", "tech_loaded"],
     "rating": 4.5, "popularity": 0.65, "tags": ["luxury"]},
    {"id": "audi_q5_2024", "brand": "Audi", "model": "Q5 2024", "type": "SUV",
     "price_usd": 45000, "energy": "Hybrid", "seats": 5, "body": "SUV",
     "use_cases": ["family", "luxury", "outdoor"], "highlights": ["luxurious", "spacious", "comfortable"],
     "rating": 4.5, "popularity": 0.68, "tags": ["luxury"]},
    {"id": "audi_etron_gt_2024", "brand": "Audi", "model": "e-tron GT 2024", "type": "Coupe",
     "price_usd": 107000, "energy": "BEV", "seats": 4, "body": "Coupe",
     "use_cases": ["luxury", "sport", "eco"], "highlights": ["ultra_fast", "luxurious", "eco_friendly"],
     "rating": 4.6, "popularity": 0.30, "tags": ["luxury", "ev", "sport"]},

    # BYD
    {"id": "byd_han_2024", "brand": "BYD", "model": "Han EV 2024", "type": "Sedan",
     "price_usd": 33000, "energy": "BEV", "seats": 5, "body": "Sedan",
     "use_cases": ["business", "eco", "family"], "highlights": ["luxurious", "long_range", "affordable_ev"],
     "rating": 4.4, "popularity": 0.55, "tags": ["ev", "value"]},
    {"id": "byd_atto3_2024", "brand": "BYD", "model": "Atto 3 2024", "type": "SUV",
     "price_usd": 28000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "commute", "eco"], "highlights": ["affordable_ev", "spacious", "practical"],
     "rating": 4.2, "popularity": 0.50, "tags": ["ev", "value"]},
    {"id": "byd_seal_2024", "brand": "BYD", "model": "Seal 2024", "type": "Sedan",
     "price_usd": 35000, "energy": "BEV", "seats": 5, "body": "Sedan",
     "use_cases": ["sport", "eco", "tech"], "highlights": ["fast", "tech_loaded", "sporty"],
     "rating": 4.3, "popularity": 0.45, "tags": ["ev", "sport"]},

    # NIO
    {"id": "nio_et5_2024", "brand": "NIO", "model": "ET5 2024", "type": "Sedan",
     "price_usd": 38000, "energy": "BEV", "seats": 5, "body": "Sedan",
     "use_cases": ["luxury", "tech", "eco"], "highlights": ["swappable_battery", "tech_loaded", "sporty"],
     "rating": 4.4, "popularity": 0.40, "tags": ["ev", "tech"]},
    {"id": "nio_es6_2024", "brand": "NIO", "model": "ES6 2024", "type": "SUV",
     "price_usd": 42000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "luxury", "eco"], "highlights": ["swappable_battery", "spacious", "luxurious"],
     "rating": 4.3, "popularity": 0.42, "tags": ["ev", "luxury"]},

    # Xpeng
    {"id": "xpeng_p7_2024", "brand": "Xpeng", "model": "P7 2024", "type": "Sedan",
     "price_usd": 35000, "energy": "BEV", "seats": 5, "body": "Sedan",
     "use_cases": ["tech", "sport", "eco"], "highlights": ["autonomous_tech", "fast", "sporty"],
     "rating": 4.3, "popularity": 0.35, "tags": ["ev", "tech"]},
    {"id": "xpeng_g9_2024", "brand": "Xpeng", "model": "G9 2024", "type": "SUV",
     "price_usd": 45000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "tech", "luxury"], "highlights": ["autonomous_tech", "spacious", "fast_charging"],
     "rating": 4.4, "popularity": 0.30, "tags": ["ev", "tech"]},

    # Li Auto
    {"id": "li_auto_l9_2024", "brand": "Li Auto", "model": "L9 2024", "type": "SUV",
     "price_usd": 62000, "energy": "PHEV", "seats": 6, "body": "SUV",
     "use_cases": ["family", "luxury", "road_trip"], "highlights": ["spacious", "luxurious", "no_range_anxiety"],
     "rating": 4.5, "popularity": 0.45, "tags": ["family", "luxury"]},
    {"id": "li_auto_l7_2024", "brand": "Li Auto", "model": "L7 2024", "type": "SUV",
     "price_usd": 48000, "energy": "PHEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "luxury"], "highlights": ["spacious", "comfortable", "no_range_anxiety"],
     "rating": 4.4, "popularity": 0.40, "tags": ["family"]},

    # Volkswagen
    {"id": "vw_golf_2024", "brand": "Volkswagen", "model": "Golf 2024", "type": "Hatchback",
     "price_usd": 23000, "energy": "Gasoline", "seats": 5, "body": "Hatchback",
     "use_cases": ["commute", "family", "city"], "highlights": ["practical", "fun_to_drive", "efficient"],
     "rating": 4.3, "popularity": 0.55, "tags": ["practical"]},
    {"id": "vw_id4_2024", "brand": "Volkswagen", "model": "ID.4 2024", "type": "SUV",
     "price_usd": 39000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "eco", "commute"], "highlights": ["spacious", "eco_friendly", "comfortable"],
     "rating": 4.2, "popularity": 0.45, "tags": ["ev", "practical"]},
    {"id": "vw_tiguan_2024", "brand": "Volkswagen", "model": "Tiguan 2024", "type": "SUV",
     "price_usd": 28000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["family", "commute"], "highlights": ["spacious", "practical", "comfortable"],
     "rating": 4.2, "popularity": 0.50, "tags": ["practical"]},

    # Volvo
    {"id": "volvo_xc60_2024", "brand": "Volvo", "model": "XC60 2024", "type": "SUV",
     "price_usd": 47000, "energy": "Hybrid", "seats": 5, "body": "SUV",
     "use_cases": ["family", "luxury", "safety"], "highlights": ["safe", "luxurious", "scandinavian_design"],
     "rating": 4.5, "popularity": 0.55, "tags": ["safety", "luxury"]},
    {"id": "volvo_xc40_2024", "brand": "Volvo", "model": "XC40 Recharge 2024", "type": "SUV",
     "price_usd": 42000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["city", "eco", "family"], "highlights": ["compact", "safe", "eco_friendly"],
     "rating": 4.3, "popularity": 0.40, "tags": ["ev", "safety"]},
    {"id": "volvo_s90_2024", "brand": "Volvo", "model": "S90 2024", "type": "Sedan",
     "price_usd": 57000, "energy": "Hybrid", "seats": 5, "body": "Sedan",
     "use_cases": ["business", "luxury"], "highlights": ["elegant", "safe", "comfortable"],
     "rating": 4.6, "popularity": 0.35, "tags": ["luxury", "safety"]},

    # Porsche
    {"id": "porsche_911_2024", "brand": "Porsche", "model": "911 2024", "type": "Coupe",
     "price_usd": 115000, "energy": "Gasoline", "seats": 4, "body": "Coupe",
     "use_cases": ["sport", "luxury", "weekend"], "highlights": ["iconic", "ultra_fast", "precise_handling"],
     "rating": 4.9, "popularity": 0.55, "tags": ["sport", "luxury"]},
    {"id": "porsche_taycan_2024", "brand": "Porsche", "model": "Taycan 2024", "type": "Sedan",
     "price_usd": 92000, "energy": "BEV", "seats": 4, "body": "Sedan",
     "use_cases": ["sport", "luxury", "eco"], "highlights": ["ultra_fast", "luxurious", "eco_friendly"],
     "rating": 4.7, "popularity": 0.40, "tags": ["ev", "sport", "luxury"]},
    {"id": "porsche_macan_2024", "brand": "Porsche", "model": "Macan 2024", "type": "SUV",
     "price_usd": 62000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["sport", "luxury", "family"], "highlights": ["sporty", "luxurious", "practical"],
     "rating": 4.6, "popularity": 0.50, "tags": ["sport", "luxury"]},

    # Hyundai
    {"id": "hyundai_sonata_2024", "brand": "Hyundai", "model": "Sonata 2024", "type": "Sedan",
     "price_usd": 25000, "energy": "Hybrid", "seats": 5, "body": "Sedan",
     "use_cases": ["family", "commute"], "highlights": ["affordable", "fuel_efficient", "spacious"],
     "rating": 4.3, "popularity": 0.50, "tags": ["value", "practical"]},
    {"id": "hyundai_tucson_2024", "brand": "Hyundai", "model": "Tucson 2024", "type": "SUV",
     "price_usd": 28000, "energy": "Hybrid", "seats": 5, "body": "SUV",
     "use_cases": ["family", "commute", "outdoor"], "highlights": ["affordable", "spacious", "modern_design"],
     "rating": 4.3, "popularity": 0.55, "tags": ["value", "practical"]},
    {"id": "hyundai_ioniq5_2024", "brand": "Hyundai", "model": "Ioniq 5 2024", "type": "SUV",
     "price_usd": 42000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "eco", "tech"], "highlights": ["fast_charging", "spacious", "unique_design"],
     "rating": 4.5, "popularity": 0.50, "tags": ["ev", "tech"]},

    # Kia
    {"id": "kia_k5_2024", "brand": "Kia", "model": "K5 2024", "type": "Sedan",
     "price_usd": 25000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["family", "commute"], "highlights": ["affordable", "sporty_design", "spacious"],
     "rating": 4.2, "popularity": 0.45, "tags": ["value"]},
    {"id": "kia_sportage_2024", "brand": "Kia", "model": "Sportage 2024", "type": "SUV",
     "price_usd": 27000, "energy": "Hybrid", "seats": 5, "body": "SUV",
     "use_cases": ["family", "commute"], "highlights": ["affordable", "spacious", "modern_design"],
     "rating": 4.3, "popularity": 0.48, "tags": ["value"]},
    {"id": "kia_ev6_2024", "brand": "Kia", "model": "EV6 2024", "type": "SUV",
     "price_usd": 43000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "eco", "tech"], "highlights": ["fast_charging", "sporty", "eco_friendly"],
     "rating": 4.5, "popularity": 0.42, "tags": ["ev", "tech"]},

    # Mazda
    {"id": "mazda_3_2024", "brand": "Mazda", "model": "Mazda3 2024", "type": "Sedan",
     "price_usd": 24000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["commute", "city"], "highlights": ["fun_to_drive", "beautiful_design", "efficient"],
     "rating": 4.4, "popularity": 0.40, "tags": ["value", "design"]},
    {"id": "mazda_cx5_2024", "brand": "Mazda", "model": "CX-5 2024", "type": "SUV",
     "price_usd": 29000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["family", "commute"], "highlights": ["fun_to_drive", "premium_feel", "reliable"],
     "rating": 4.5, "popularity": 0.50, "tags": ["value"]},

    # Subaru
    {"id": "subaru_outback_2024", "brand": "Subaru", "model": "Outback 2024", "type": "Wagon",
     "price_usd": 29000, "energy": "Gasoline", "seats": 5, "body": "Wagon",
     "use_cases": ["outdoor", "family", "offroad"], "highlights": ["awd", "rugged", "spacious"],
     "rating": 4.5, "popularity": 0.45, "tags": ["outdoor", "practical"]},
    {"id": "subaru_forester_2024", "brand": "Subaru", "model": "Forester 2024", "type": "SUV",
     "price_usd": 28000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["family", "outdoor", "offroad"], "highlights": ["awd", "safe", "spacious"],
     "rating": 4.4, "popularity": 0.48, "tags": ["outdoor", "practical"]},

    # Nissan
    {"id": "nissan_altima_2024", "brand": "Nissan", "model": "Altima 2024", "type": "Sedan",
     "price_usd": 26000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["family", "commute"], "highlights": ["affordable", "comfortable", "spacious"],
     "rating": 4.1, "popularity": 0.45, "tags": ["value", "practical"]},
    {"id": "nissan_ariya_2024", "brand": "Nissan", "model": "Ariya 2024", "type": "SUV",
     "price_usd": 41000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "eco", "commute"], "highlights": ["eco_friendly", "spacious", "comfortable"],
     "rating": 4.2, "popularity": 0.30, "tags": ["ev"]},

    # Ford
    {"id": "ford_f150_2024", "brand": "Ford", "model": "F-150 2024", "type": "Pickup",
     "price_usd": 36000, "energy": "Gasoline", "seats": 6, "body": "Pickup",
     "use_cases": ["utility", "work", "offroad"], "highlights": ["powerful", "rugged", "versatile"],
     "rating": 4.5, "popularity": 0.85, "tags": ["bestseller", "utility"]},
    {"id": "ford_mustang_2024", "brand": "Ford", "model": "Mustang 2024", "type": "Coupe",
     "price_usd": 32000, "energy": "Gasoline", "seats": 4, "body": "Coupe",
     "use_cases": ["sport", "weekend"], "highlights": ["iconic", "fast", "fun_to_drive"],
     "rating": 4.4, "popularity": 0.60, "tags": ["sport"]},
    {"id": "ford_mach_e_2024", "brand": "Ford", "model": "Mustang Mach-E 2024", "type": "SUV",
     "price_usd": 40000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "eco", "sport"], "highlights": ["fast", "eco_friendly", "sporty"],
     "rating": 4.3, "popularity": 0.45, "tags": ["ev", "sport"]},

    # Chevrolet
    {"id": "chevy_bolt_2024", "brand": "Chevrolet", "model": "Bolt EV 2024", "type": "Hatchback",
     "price_usd": 27000, "energy": "BEV", "seats": 5, "body": "Hatchback",
     "use_cases": ["commute", "city", "eco"], "highlights": ["affordable_ev", "efficient", "compact"],
     "rating": 4.0, "popularity": 0.40, "tags": ["ev", "value"]},
    {"id": "chevy_tahoe_2024", "brand": "Chevrolet", "model": "Tahoe 2024", "type": "SUV",
     "price_usd": 56000, "energy": "Gasoline", "seats": 8, "body": "SUV",
     "use_cases": ["family", "utility", "tow"], "highlights": ["spacious", "powerful", "tow_capable"],
     "rating": 4.3, "popularity": 0.50, "tags": ["family", "utility"]},

    # Lexus
    {"id": "lexus_rx_2024", "brand": "Lexus", "model": "RX 2024", "type": "SUV",
     "price_usd": 49000, "energy": "Hybrid", "seats": 5, "body": "SUV",
     "use_cases": ["luxury", "family"], "highlights": ["luxurious", "reliable", "quiet"],
     "rating": 4.6, "popularity": 0.55, "tags": ["luxury"]},
    {"id": "lexus_es_2024", "brand": "Lexus", "model": "ES 2024", "type": "Sedan",
     "price_usd": 44000, "energy": "Hybrid", "seats": 5, "body": "Sedan",
     "use_cases": ["luxury", "business"], "highlights": ["luxurious", "comfortable", "quiet"],
     "rating": 4.6, "popularity": 0.50, "tags": ["luxury"]},

    # Genesis
    {"id": "genesis_g80_2024", "brand": "Genesis", "model": "G80 2024", "type": "Sedan",
     "price_usd": 51000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["luxury", "business"], "highlights": ["luxurious", "value_luxury", "elegant"],
     "rating": 4.6, "popularity": 0.25, "tags": ["luxury", "value"]},
    {"id": "genesis_gv70_2024", "brand": "Genesis", "model": "GV70 2024", "type": "SUV",
     "price_usd": 45000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["luxury", "family"], "highlights": ["luxurious", "value_luxury", "sporty"],
     "rating": 4.5, "popularity": 0.22, "tags": ["luxury", "value"]},

    # Polestar
    {"id": "polestar_2_2024", "brand": "Polestar", "model": "Polestar 2 2024", "type": "Sedan",
     "price_usd": 49000, "energy": "BEV", "seats": 5, "body": "Sedan",
     "use_cases": ["eco", "luxury", "tech"], "highlights": ["scandinavian_design", "eco_friendly", "sporty"],
     "rating": 4.3, "popularity": 0.20, "tags": ["ev", "luxury"]},
    {"id": "polestar_3_2024", "brand": "Polestar", "model": "Polestar 3 2024", "type": "SUV",
     "price_usd": 67000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["eco", "luxury", "family"], "highlights": ["luxurious", "eco_friendly", "spacious"],
     "rating": 4.4, "popularity": 0.15, "tags": ["ev", "luxury"]},

    # Rivian
    {"id": "rivian_r1t_2024", "brand": "Rivian", "model": "R1T 2024", "type": "Pickup",
     "price_usd": 71000, "energy": "BEV", "seats": 5, "body": "Pickup",
     "use_cases": ["offroad", "utility", "eco"], "highlights": ["adventure_ready", "eco_friendly", "powerful"],
     "rating": 4.5, "popularity": 0.25, "tags": ["ev", "adventure"]},
    {"id": "rivian_r1s_2024", "brand": "Rivian", "model": "R1S 2024", "type": "SUV",
     "price_usd": 78000, "energy": "BEV", "seats": 7, "body": "SUV",
     "use_cases": ["family", "offroad", "eco"], "highlights": ["adventure_ready", "spacious", "eco_friendly"],
     "rating": 4.5, "popularity": 0.22, "tags": ["ev", "adventure"]},

    # Lucid
    {"id": "lucid_air_2024", "brand": "Lucid", "model": "Air 2024", "type": "Sedan",
     "price_usd": 87000, "energy": "BEV", "seats": 5, "body": "Sedan",
     "use_cases": ["luxury", "eco", "tech"], "highlights": ["ultra_luxurious", "longest_range", "fast"],
     "rating": 4.7, "popularity": 0.18, "tags": ["ev", "luxury"]},

    # Mini
    {"id": "mini_cooper_2024", "brand": "Mini", "model": "Cooper 2024", "type": "Hatchback",
     "price_usd": 25000, "energy": "Gasoline", "seats": 4, "body": "Hatchback",
     "use_cases": ["city", "weekend"], "highlights": ["compact", "fun_to_drive", "iconic_design"],
     "rating": 4.2, "popularity": 0.35, "tags": ["city", "design"]},

    # Mazda MX-5
    {"id": "mazda_mx5_2024", "brand": "Mazda", "model": "MX-5 Miata 2024", "type": "Convertible",
     "price_usd": 29000, "energy": "Gasoline", "seats": 2, "body": "Convertible",
     "use_cases": ["sport", "weekend"], "highlights": ["fun_to_drive", "lightweight", "affordable_sports_car"],
     "rating": 4.7, "popularity": 0.40, "tags": ["sport"]},

    # Buick
    {"id": "buick_enclave_2024", "brand": "Buick", "model": "Enclave 2024", "type": "SUV",
     "price_usd": 45000, "energy": "Gasoline", "seats": 7, "body": "SUV",
     "use_cases": ["family", "luxury"], "highlights": ["spacious", "quiet", "comfortable"],
     "rating": 4.2, "popularity": 0.30, "tags": ["family"]},
    {"id": "buick_encore_2024", "brand": "Buick", "model": "Encore GX 2024", "type": "SUV",
     "price_usd": 26000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["commute", "city"], "highlights": ["compact", "affordable", "quiet"],
     "rating": 4.0, "popularity": 0.28, "tags": ["value"]},
    {"id": "buick_lacrosse_2024", "brand": "Buick", "model": "LaCrosse 2024", "type": "Sedan",
     "price_usd": 38000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["business", "luxury"], "highlights": ["comfortable", "quiet", "spacious"],
     "rating": 4.1, "popularity": 0.22, "tags": ["luxury"]},

    # Toyota additions
    {"id": "toyota_highlander_2024", "brand": "Toyota", "model": "Highlander 2024", "type": "SUV",
     "price_usd": 39000, "energy": "Hybrid", "seats": 8, "body": "SUV",
     "use_cases": ["family", "road_trip"], "highlights": ["spacious", "reliable", "fuel_efficient"],
     "rating": 4.5, "popularity": 0.82, "tags": ["family", "bestseller"]},
    {"id": "toyota_corolla_2024", "brand": "Toyota", "model": "Corolla 2024", "type": "Sedan",
     "price_usd": 22000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["commute", "city"], "highlights": ["affordable", "fuel_efficient", "reliable"],
     "rating": 4.4, "popularity": 0.85, "tags": ["bestseller", "value"]},
    {"id": "toyota_prius_2024", "brand": "Toyota", "model": "Prius 2024", "type": "Hatchback",
     "price_usd": 28000, "energy": "Hybrid", "seats": 5, "body": "Hatchback",
     "use_cases": ["eco", "commute"], "highlights": ["fuel_efficient", "eco_friendly", "practical"],
     "rating": 4.5, "popularity": 0.70, "tags": ["eco", "bestseller"]},
    {"id": "toyota_tundra_2024", "brand": "Toyota", "model": "Tundra 2024", "type": "Pickup",
     "price_usd": 40000, "energy": "Hybrid", "seats": 6, "body": "Pickup",
     "use_cases": ["utility", "offroad", "work"], "highlights": ["powerful", "reliable", "tow_capable"],
     "rating": 4.4, "popularity": 0.60, "tags": ["utility"]},
    {"id": "toyota_bz4x_2024", "brand": "Toyota", "model": "bZ4X 2024", "type": "SUV",
     "price_usd": 42000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "eco", "commute"], "highlights": ["eco_friendly", "spacious", "reliable"],
     "rating": 4.0, "popularity": 0.30, "tags": ["ev"]},

    # Honda additions
    {"id": "honda_hrv_2024", "brand": "Honda", "model": "HR-V 2024", "type": "SUV",
     "price_usd": 25000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["commute", "city"], "highlights": ["compact", "affordable", "practical"],
     "rating": 4.2, "popularity": 0.65, "tags": ["value"]},
    {"id": "honda_passport_2024", "brand": "Honda", "model": "Passport 2024", "type": "SUV",
     "price_usd": 42000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["family", "offroad"], "highlights": ["rugged", "spacious", "powerful"],
     "rating": 4.3, "popularity": 0.50, "tags": ["family"]},
    {"id": "honda_prologue_2024", "brand": "Honda", "model": "Prologue 2024", "type": "SUV",
     "price_usd": 48000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "eco", "commute"], "highlights": ["spacious", "eco_friendly", "comfortable"],
     "rating": 4.2, "popularity": 0.35, "tags": ["ev"]},

    # Tesla additions
    {"id": "tesla_model_x_2024", "brand": "Tesla", "model": "Model X 2024", "type": "SUV",
     "price_usd": 80000, "energy": "BEV", "seats": 7, "body": "SUV",
     "use_cases": ["family", "luxury", "tech"], "highlights": ["falcon_doors", "fast", "tech_loaded"],
     "rating": 4.5, "popularity": 0.50, "tags": ["luxury", "ev"]},

    # BMW additions
    {"id": "bmw_x3_2024", "brand": "BMW", "model": "X3 2024", "type": "SUV",
     "price_usd": 47000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["family", "sport", "luxury"], "highlights": ["sporty", "luxurious", "practical"],
     "rating": 4.5, "popularity": 0.68, "tags": ["luxury"]},
    {"id": "bmw_x7_2024", "brand": "BMW", "model": "X7 2024", "type": "SUV",
     "price_usd": 78000, "energy": "Hybrid", "seats": 7, "body": "SUV",
     "use_cases": ["family", "luxury"], "highlights": ["ultra_luxurious", "spacious", "powerful"],
     "rating": 4.6, "popularity": 0.40, "tags": ["luxury"]},
    {"id": "bmw_7_series_2024", "brand": "BMW", "model": "7 Series 2024", "type": "Sedan",
     "price_usd": 97000, "energy": "Hybrid", "seats": 5, "body": "Sedan",
     "use_cases": ["luxury", "business"], "highlights": ["ultra_luxurious", "tech_loaded", "comfortable"],
     "rating": 4.7, "popularity": 0.35, "tags": ["luxury"]},
    {"id": "bmw_i4_2024", "brand": "BMW", "model": "i4 2024", "type": "Sedan",
     "price_usd": 52000, "energy": "BEV", "seats": 5, "body": "Sedan",
     "use_cases": ["sport", "eco", "luxury"], "highlights": ["fast", "eco_friendly", "sporty"],
     "rating": 4.4, "popularity": 0.42, "tags": ["ev", "sport"]},

    # Mercedes additions
    {"id": "mercedes_glc_2024", "brand": "Mercedes-Benz", "model": "GLC 2024", "type": "SUV",
     "price_usd": 48000, "energy": "Hybrid", "seats": 5, "body": "SUV",
     "use_cases": ["family", "luxury"], "highlights": ["luxurious", "comfortable", "practical"],
     "rating": 4.6, "popularity": 0.65, "tags": ["luxury"]},
    {"id": "mercedes_s_class_2024", "brand": "Mercedes-Benz", "model": "S-Class 2024", "type": "Sedan",
     "price_usd": 115000, "energy": "Hybrid", "seats": 5, "body": "Sedan",
     "use_cases": ["luxury", "business"], "highlights": ["ultra_luxurious", "tech_loaded", "comfortable"],
     "rating": 4.9, "popularity": 0.40, "tags": ["luxury"]},
    {"id": "mercedes_eqe_2024", "brand": "Mercedes-Benz", "model": "EQE 2024", "type": "Sedan",
     "price_usd": 75000, "energy": "BEV", "seats": 5, "body": "Sedan",
     "use_cases": ["luxury", "eco", "business"], "highlights": ["luxurious", "long_range", "tech_loaded"],
     "rating": 4.5, "popularity": 0.30, "tags": ["luxury", "ev"]},
    {"id": "mercedes_g_class_2024", "brand": "Mercedes-Benz", "model": "G-Class 2024", "type": "SUV",
     "price_usd": 140000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["luxury", "offroad"], "highlights": ["iconic", "rugged", "luxurious"],
     "rating": 4.6, "popularity": 0.45, "tags": ["luxury"]},

    # Audi additions
    {"id": "audi_q7_2024", "brand": "Audi", "model": "Q7 2024", "type": "SUV",
     "price_usd": 60000, "energy": "Hybrid", "seats": 7, "body": "SUV",
     "use_cases": ["family", "luxury"], "highlights": ["spacious", "luxurious", "comfortable"],
     "rating": 4.5, "popularity": 0.55, "tags": ["luxury"]},
    {"id": "audi_a6_2024", "brand": "Audi", "model": "A6 2024", "type": "Sedan",
     "price_usd": 56000, "energy": "Hybrid", "seats": 5, "body": "Sedan",
     "use_cases": ["business", "luxury"], "highlights": ["luxurious", "tech_loaded", "comfortable"],
     "rating": 4.6, "popularity": 0.50, "tags": ["luxury"]},
    {"id": "audi_q6_etron_2024", "brand": "Audi", "model": "Q6 e-tron 2024", "type": "SUV",
     "price_usd": 65000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "luxury", "eco"], "highlights": ["luxurious", "long_range", "tech_loaded"],
     "rating": 4.4, "popularity": 0.28, "tags": ["ev", "luxury"]},
    {"id": "audi_rs6_2024", "brand": "Audi", "model": "RS6 Avant 2024", "type": "Wagon",
     "price_usd": 120000, "energy": "Gasoline", "seats": 5, "body": "Wagon",
     "use_cases": ["sport", "family", "luxury"], "highlights": ["ultra_fast", "practical", "sporty"],
     "rating": 4.7, "popularity": 0.25, "tags": ["sport", "luxury"]},

    # Volkswagen additions
    {"id": "vw_atlas_2024", "brand": "Volkswagen", "model": "Atlas 2024", "type": "SUV",
     "price_usd": 37000, "energy": "Gasoline", "seats": 7, "body": "SUV",
     "use_cases": ["family", "road_trip"], "highlights": ["spacious", "practical", "comfortable"],
     "rating": 4.2, "popularity": 0.48, "tags": ["family"]},
    {"id": "vw_id7_2024", "brand": "Volkswagen", "model": "ID.7 2024", "type": "Sedan",
     "price_usd": 50000, "energy": "BEV", "seats": 5, "body": "Sedan",
     "use_cases": ["business", "eco"], "highlights": ["long_range", "spacious", "comfortable"],
     "rating": 4.3, "popularity": 0.25, "tags": ["ev"]},

    # Ford additions
    {"id": "ford_escape_2024", "brand": "Ford", "model": "Escape 2024", "type": "SUV",
     "price_usd": 30000, "energy": "Hybrid", "seats": 5, "body": "SUV",
     "use_cases": ["family", "commute"], "highlights": ["practical", "fuel_efficient", "comfortable"],
     "rating": 4.2, "popularity": 0.60, "tags": ["practical"]},
    {"id": "ford_bronco_2024", "brand": "Ford", "model": "Bronco 2024", "type": "SUV",
     "price_usd": 40000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["offroad", "outdoor"], "highlights": ["rugged", "offroad_capable", "iconic"],
     "rating": 4.4, "popularity": 0.65, "tags": ["offroad"]},
    {"id": "ford_explorer_2024", "brand": "Ford", "model": "Explorer 2024", "type": "SUV",
     "price_usd": 36000, "energy": "Gasoline", "seats": 7, "body": "SUV",
     "use_cases": ["family", "road_trip"], "highlights": ["spacious", "practical", "powerful"],
     "rating": 4.3, "popularity": 0.62, "tags": ["family"]},
    {"id": "ford_lightning_2024", "brand": "Ford", "model": "F-150 Lightning 2024", "type": "Pickup",
     "price_usd": 55000, "energy": "BEV", "seats": 5, "body": "Pickup",
     "use_cases": ["utility", "eco", "work"], "highlights": ["powerful", "eco_friendly", "fast"],
     "rating": 4.4, "popularity": 0.50, "tags": ["ev", "utility"]},

    # Chevrolet additions
    {"id": "chevy_corvette_2024", "brand": "Chevrolet", "model": "Corvette 2024", "type": "Coupe",
     "price_usd": 68000, "energy": "Gasoline", "seats": 2, "body": "Coupe",
     "use_cases": ["sport", "weekend"], "highlights": ["ultra_fast", "iconic", "affordable_supercar"],
     "rating": 4.8, "popularity": 0.65, "tags": ["sport"]},
    {"id": "chevy_equinox_2024", "brand": "Chevrolet", "model": "Equinox 2024", "type": "SUV",
     "price_usd": 28000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["family", "commute"], "highlights": ["affordable", "spacious", "practical"],
     "rating": 4.2, "popularity": 0.60, "tags": ["value"]},
    {"id": "chevy_traverse_2024", "brand": "Chevrolet", "model": "Traverse 2024", "type": "SUV",
     "price_usd": 35000, "energy": "Gasoline", "seats": 8, "body": "SUV",
     "use_cases": ["family", "road_trip"], "highlights": ["spacious", "practical", "comfortable"],
     "rating": 4.2, "popularity": 0.48, "tags": ["family"]},
    {"id": "chevy_malibu_2024", "brand": "Chevrolet", "model": "Malibu 2024", "type": "Sedan",
     "price_usd": 25000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["family", "commute"], "highlights": ["affordable", "comfortable", "spacious"],
     "rating": 4.0, "popularity": 0.45, "tags": ["value"]},

    # Hyundai additions
    {"id": "hyundai_elantra_2024", "brand": "Hyundai", "model": "Elantra 2024", "type": "Sedan",
     "price_usd": 22000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["commute", "family"], "highlights": ["affordable", "fuel_efficient", "spacious"],
     "rating": 4.3, "popularity": 0.58, "tags": ["value"]},
    {"id": "hyundai_palisade_2024", "brand": "Hyundai", "model": "Palisade 2024", "type": "SUV",
     "price_usd": 40000, "energy": "Gasoline", "seats": 8, "body": "SUV",
     "use_cases": ["family", "luxury", "road_trip"], "highlights": ["spacious", "luxurious", "comfortable"],
     "rating": 4.5, "popularity": 0.55, "tags": ["family"]},
    {"id": "hyundai_santafe_2024", "brand": "Hyundai", "model": "Santa Fe 2024", "type": "SUV",
     "price_usd": 35000, "energy": "Hybrid", "seats": 7, "body": "SUV",
     "use_cases": ["family", "outdoor"], "highlights": ["spacious", "practical", "modern_design"],
     "rating": 4.4, "popularity": 0.50, "tags": ["family"]},
    {"id": "hyundai_kona_2024", "brand": "Hyundai", "model": "Kona EV 2024", "type": "SUV",
     "price_usd": 33000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["city", "eco", "commute"], "highlights": ["affordable_ev", "compact", "practical"],
     "rating": 4.2, "popularity": 0.45, "tags": ["ev", "value"]},

    # Kia additions
    {"id": "kia_telluride_2024", "brand": "Kia", "model": "Telluride 2024", "type": "SUV",
     "price_usd": 37000, "energy": "Gasoline", "seats": 8, "body": "SUV",
     "use_cases": ["family", "luxury", "road_trip"], "highlights": ["spacious", "luxurious", "value"],
     "rating": 4.6, "popularity": 0.65, "tags": ["family", "bestseller"]},
    {"id": "kia_seltos_2024", "brand": "Kia", "model": "Seltos 2024", "type": "SUV",
     "price_usd": 24000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["commute", "city"], "highlights": ["affordable", "spacious", "practical"],
     "rating": 4.2, "popularity": 0.50, "tags": ["value"]},
    {"id": "kia_stinger_2024", "brand": "Kia", "model": "Stinger 2024", "type": "Sedan",
     "price_usd": 37000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["sport", "luxury"], "highlights": ["fast", "sporty", "luxurious"],
     "rating": 4.4, "popularity": 0.35, "tags": ["sport"]},

    # Nissan additions
    {"id": "nissan_rogue_2024", "brand": "Nissan", "model": "Rogue 2024", "type": "SUV",
     "price_usd": 29000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["family", "commute"], "highlights": ["spacious", "practical", "comfortable"],
     "rating": 4.3, "popularity": 0.62, "tags": ["family", "bestseller"]},
    {"id": "nissan_sentra_2024", "brand": "Nissan", "model": "Sentra 2024", "type": "Sedan",
     "price_usd": 21000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["commute", "city"], "highlights": ["affordable", "practical", "comfortable"],
     "rating": 4.1, "popularity": 0.50, "tags": ["value"]},
    {"id": "nissan_pathfinder_2024", "brand": "Nissan", "model": "Pathfinder 2024", "type": "SUV",
     "price_usd": 37000, "energy": "Gasoline", "seats": 8, "body": "SUV",
     "use_cases": ["family", "offroad"], "highlights": ["spacious", "rugged", "practical"],
     "rating": 4.2, "popularity": 0.48, "tags": ["family"]},
    {"id": "nissan_z_2024", "brand": "Nissan", "model": "Z 2024", "type": "Coupe",
     "price_usd": 42000, "energy": "Gasoline", "seats": 2, "body": "Coupe",
     "use_cases": ["sport", "weekend"], "highlights": ["iconic", "fast", "fun_to_drive"],
     "rating": 4.5, "popularity": 0.45, "tags": ["sport"]},

    # BYD additions
    {"id": "byd_tang_2024", "brand": "BYD", "model": "Tang EV 2024", "type": "SUV",
     "price_usd": 45000, "energy": "BEV", "seats": 7, "body": "SUV",
     "use_cases": ["family", "luxury", "eco"], "highlights": ["spacious", "luxurious", "long_range"],
     "rating": 4.3, "popularity": 0.45, "tags": ["ev", "family"]},
    {"id": "byd_song_2024", "brand": "BYD", "model": "Song Plus EV 2024", "type": "SUV",
     "price_usd": 28000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "commute", "eco"], "highlights": ["affordable_ev", "spacious", "practical"],
     "rating": 4.1, "popularity": 0.48, "tags": ["ev", "value"]},
    {"id": "byd_dolphin_2024", "brand": "BYD", "model": "Dolphin 2024", "type": "Hatchback",
     "price_usd": 20000, "energy": "BEV", "seats": 5, "body": "Hatchback",
     "use_cases": ["city", "commute", "eco"], "highlights": ["affordable_ev", "compact", "practical"],
     "rating": 4.0, "popularity": 0.40, "tags": ["ev", "value"]},
    {"id": "byd_han_dm_2024", "brand": "BYD", "model": "Han DM-i 2024", "type": "Sedan",
     "price_usd": 30000, "energy": "PHEV", "seats": 5, "body": "Sedan",
     "use_cases": ["family", "business"], "highlights": ["fuel_efficient", "spacious", "luxurious"],
     "rating": 4.2, "popularity": 0.42, "tags": ["value"]},

    # NIO additions
    {"id": "nio_et7_2024", "brand": "NIO", "model": "ET7 2024", "type": "Sedan",
     "price_usd": 58000, "energy": "BEV", "seats": 5, "body": "Sedan",
     "use_cases": ["luxury", "business", "tech"], "highlights": ["luxurious", "long_range", "tech_loaded"],
     "rating": 4.5, "popularity": 0.35, "tags": ["ev", "luxury"]},
    {"id": "nio_es8_2024", "brand": "NIO", "model": "ES8 2024", "type": "SUV",
     "price_usd": 55000, "energy": "BEV", "seats": 7, "body": "SUV",
     "use_cases": ["family", "luxury", "eco"], "highlights": ["spacious", "luxurious", "swappable_battery"],
     "rating": 4.4, "popularity": 0.32, "tags": ["ev", "family"]},
    {"id": "nio_ec6_2024", "brand": "NIO", "model": "EC6 2024", "type": "SUV",
     "price_usd": 46000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["sport", "luxury", "eco"], "highlights": ["sporty", "fast", "luxurious"],
     "rating": 4.3, "popularity": 0.28, "tags": ["ev", "sport"]},

    # Xpeng additions
    {"id": "xpeng_p5_2024", "brand": "Xpeng", "model": "P5 2024", "type": "Sedan",
     "price_usd": 25000, "energy": "BEV", "seats": 5, "body": "Sedan",
     "use_cases": ["family", "commute", "tech"], "highlights": ["affordable_ev", "tech_loaded", "spacious"],
     "rating": 4.1, "popularity": 0.38, "tags": ["ev", "value"]},
    {"id": "xpeng_g6_2024", "brand": "Xpeng", "model": "G6 2024", "type": "SUV",
     "price_usd": 30000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "eco", "tech"], "highlights": ["fast_charging", "spacious", "tech_loaded"],
     "rating": 4.2, "popularity": 0.35, "tags": ["ev"]},

    # Li Auto additions
    {"id": "li_auto_l8_2024", "brand": "Li Auto", "model": "L8 2024", "type": "SUV",
     "price_usd": 55000, "energy": "PHEV", "seats": 6, "body": "SUV",
     "use_cases": ["family", "luxury", "road_trip"], "highlights": ["spacious", "luxurious", "no_range_anxiety"],
     "rating": 4.5, "popularity": 0.42, "tags": ["family"]},
    {"id": "li_auto_l6_2024", "brand": "Li Auto", "model": "L6 2024", "type": "SUV",
     "price_usd": 38000, "energy": "PHEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "commute"], "highlights": ["affordable", "spacious", "no_range_anxiety"],
     "rating": 4.3, "popularity": 0.38, "tags": ["family", "value"]},

    # Volvo additions
    {"id": "volvo_ex30_2024", "brand": "Volvo", "model": "EX30 2024", "type": "SUV",
     "price_usd": 35000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["city", "eco", "commute"], "highlights": ["compact", "eco_friendly", "safe"],
     "rating": 4.2, "popularity": 0.32, "tags": ["ev"]},
    {"id": "volvo_ex90_2024", "brand": "Volvo", "model": "EX90 2024", "type": "SUV",
     "price_usd": 78000, "energy": "BEV", "seats": 7, "body": "SUV",
     "use_cases": ["family", "luxury", "eco"], "highlights": ["spacious", "safe", "luxurious"],
     "rating": 4.5, "popularity": 0.28, "tags": ["ev", "luxury"]},
    {"id": "volvo_v60_2024", "brand": "Volvo", "model": "V60 2024", "type": "Wagon",
     "price_usd": 46000, "energy": "Hybrid", "seats": 5, "body": "Wagon",
     "use_cases": ["family", "outdoor"], "highlights": ["practical", "safe", "spacious"],
     "rating": 4.4, "popularity": 0.30, "tags": ["practical"]},

    # Porsche additions
    {"id": "porsche_cayenne_2024", "brand": "Porsche", "model": "Cayenne 2024", "type": "SUV",
     "price_usd": 85000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["luxury", "sport", "family"], "highlights": ["sporty", "luxurious", "powerful"],
     "rating": 4.7, "popularity": 0.55, "tags": ["luxury", "sport"]},
    {"id": "porsche_panamera_2024", "brand": "Porsche", "model": "Panamera 2024", "type": "Sedan",
     "price_usd": 95000, "energy": "Hybrid", "seats": 4, "body": "Sedan",
     "use_cases": ["luxury", "sport", "business"], "highlights": ["ultra_fast", "luxurious", "sporty"],
     "rating": 4.7, "popularity": 0.40, "tags": ["luxury", "sport"]},
    {"id": "porsche_718_2024", "brand": "Porsche", "model": "718 Cayman 2024", "type": "Coupe",
     "price_usd": 68000, "energy": "Gasoline", "seats": 2, "body": "Coupe",
     "use_cases": ["sport", "weekend"], "highlights": ["precise_handling", "sporty", "fun_to_drive"],
     "rating": 4.7, "popularity": 0.35, "tags": ["sport"]},
    {"id": "porsche_taycan_cross_2024", "brand": "Porsche", "model": "Taycan Cross Turismo 2024", "type": "Wagon",
     "price_usd": 100000, "energy": "BEV", "seats": 4, "body": "Wagon",
     "use_cases": ["sport", "luxury", "eco"], "highlights": ["ultra_fast", "practical", "eco_friendly"],
     "rating": 4.6, "popularity": 0.22, "tags": ["ev", "sport"]},

    # Mazda additions
    {"id": "mazda_cx30_2024", "brand": "Mazda", "model": "CX-30 2024", "type": "SUV",
     "price_usd": 25000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["commute", "city"], "highlights": ["compact", "fun_to_drive", "premium_feel"],
     "rating": 4.3, "popularity": 0.45, "tags": ["value"]},
    {"id": "mazda_cx9_2024", "brand": "Mazda", "model": "CX-9 2024", "type": "SUV",
     "price_usd": 38000, "energy": "Gasoline", "seats": 7, "body": "SUV",
     "use_cases": ["family", "luxury"], "highlights": ["spacious", "premium_feel", "comfortable"],
     "rating": 4.4, "popularity": 0.42, "tags": ["family"]},
    {"id": "mazda_mx30_2024", "brand": "Mazda", "model": "MX-30 2024", "type": "SUV",
     "price_usd": 35000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["city", "eco"], "highlights": ["eco_friendly", "compact", "unique_design"],
     "rating": 3.9, "popularity": 0.18, "tags": ["ev"]},

    # Subaru additions
    {"id": "subaru_crosstrek_2024", "brand": "Subaru", "model": "Crosstrek 2024", "type": "SUV",
     "price_usd": 25000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["outdoor", "city", "commute"], "highlights": ["awd", "compact", "rugged"],
     "rating": 4.4, "popularity": 0.50, "tags": ["outdoor", "value"]},
    {"id": "subaru_wrx_2024", "brand": "Subaru", "model": "WRX 2024", "type": "Sedan",
     "price_usd": 32000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["sport", "weekend"], "highlights": ["fast", "awd", "sporty"],
     "rating": 4.4, "popularity": 0.45, "tags": ["sport"]},
    {"id": "subaru_ascent_2024", "brand": "Subaru", "model": "Ascent 2024", "type": "SUV",
     "price_usd": 35000, "energy": "Gasoline", "seats": 8, "body": "SUV",
     "use_cases": ["family", "outdoor"], "highlights": ["spacious", "awd", "safe"],
     "rating": 4.3, "popularity": 0.42, "tags": ["family"]},

    # Lexus additions
    {"id": "lexus_nx_2024", "brand": "Lexus", "model": "NX 2024", "type": "SUV",
     "price_usd": 42000, "energy": "Hybrid", "seats": 5, "body": "SUV",
     "use_cases": ["luxury", "family"], "highlights": ["luxurious", "reliable", "fuel_efficient"],
     "rating": 4.5, "popularity": 0.55, "tags": ["luxury"]},
    {"id": "lexus_lx_2024", "brand": "Lexus", "model": "LX 2024", "type": "SUV",
     "price_usd": 90000, "energy": "Gasoline", "seats": 7, "body": "SUV",
     "use_cases": ["luxury", "offroad", "family"], "highlights": ["ultra_luxurious", "rugged", "powerful"],
     "rating": 4.6, "popularity": 0.35, "tags": ["luxury"]},
    {"id": "lexus_is_2024", "brand": "Lexus", "model": "IS 2024", "type": "Sedan",
     "price_usd": 42000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["sport", "luxury"], "highlights": ["sporty", "luxurious", "reliable"],
     "rating": 4.4, "popularity": 0.40, "tags": ["luxury", "sport"]},
    {"id": "lexus_rz_2024", "brand": "Lexus", "model": "RZ 2024", "type": "SUV",
     "price_usd": 50000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["luxury", "eco", "family"], "highlights": ["luxurious", "eco_friendly", "comfortable"],
     "rating": 4.2, "popularity": 0.25, "tags": ["ev", "luxury"]},

    # Genesis additions
    {"id": "genesis_gv80_2024", "brand": "Genesis", "model": "GV80 2024", "type": "SUV",
     "price_usd": 65000, "energy": "Gasoline", "seats": 7, "body": "SUV",
     "use_cases": ["luxury", "family"], "highlights": ["luxurious", "spacious", "value_luxury"],
     "rating": 4.6, "popularity": 0.30, "tags": ["luxury"]},
    {"id": "genesis_g90_2024", "brand": "Genesis", "model": "G90 2024", "type": "Sedan",
     "price_usd": 90000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["luxury", "business"], "highlights": ["ultra_luxurious", "spacious", "comfortable"],
     "rating": 4.7, "popularity": 0.20, "tags": ["luxury"]},
    {"id": "genesis_electrified_g80_2024", "brand": "Genesis", "model": "Electrified G80 2024", "type": "Sedan",
     "price_usd": 80000, "energy": "BEV", "seats": 5, "body": "Sedan",
     "use_cases": ["luxury", "eco", "business"], "highlights": ["luxurious", "eco_friendly", "spacious"],
     "rating": 4.5, "popularity": 0.18, "tags": ["ev", "luxury"]},

    # Polestar addition
    {"id": "polestar_4_2024", "brand": "Polestar", "model": "Polestar 4 2024", "type": "SUV",
     "price_usd": 55000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["eco", "luxury", "tech"], "highlights": ["fast_charging", "sporty", "minimalist"],
     "rating": 4.3, "popularity": 0.18, "tags": ["ev", "luxury"]},

    # Rivian addition
    {"id": "rivian_r2_2024", "brand": "Rivian", "model": "R2 2024", "type": "SUV",
     "price_usd": 47000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "offroad", "eco"], "highlights": ["affordable_ev", "adventure_ready", "spacious"],
     "rating": 4.4, "popularity": 0.28, "tags": ["ev"]},

    # Lucid addition
    {"id": "lucid_gravity_2024", "brand": "Lucid", "model": "Gravity 2024", "type": "SUV",
     "price_usd": 80000, "energy": "BEV", "seats": 7, "body": "SUV",
     "use_cases": ["luxury", "family", "eco"], "highlights": ["spacious", "longest_range", "luxurious"],
     "rating": 4.6, "popularity": 0.20, "tags": ["ev", "luxury"]},

    # Mini additions
    {"id": "mini_countryman_2024", "brand": "Mini", "model": "Countryman 2024", "type": "SUV",
     "price_usd": 32000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["city", "family"], "highlights": ["spacious", "fun_to_drive", "iconic_design"],
     "rating": 4.2, "popularity": 0.30, "tags": ["city"]},
    {"id": "mini_electric_2024", "brand": "Mini", "model": "Cooper SE 2024", "type": "Hatchback",
     "price_usd": 30000, "energy": "BEV", "seats": 4, "body": "Hatchback",
     "use_cases": ["city", "eco"], "highlights": ["compact", "eco_friendly", "fun_to_drive"],
     "rating": 4.1, "popularity": 0.28, "tags": ["ev", "city"]},

    # Acura (new mainstream)
    {"id": "acura_tlx_2024", "brand": "Acura", "model": "TLX 2024", "type": "Sedan",
     "price_usd": 41000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["sport", "luxury", "commute"], "highlights": ["sporty", "luxurious", "reliable"],
     "rating": 4.4, "popularity": 0.45, "tags": ["luxury", "sport"]},
    {"id": "acura_mdx_2024", "brand": "Acura", "model": "MDX 2024", "type": "SUV",
     "price_usd": 52000, "energy": "Gasoline", "seats": 7, "body": "SUV",
     "use_cases": ["family", "luxury"], "highlights": ["spacious", "luxurious", "practical"],
     "rating": 4.4, "popularity": 0.50, "tags": ["family", "luxury"]},
    {"id": "acura_rdx_2024", "brand": "Acura", "model": "RDX 2024", "type": "SUV",
     "price_usd": 41000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["family", "luxury", "commute"], "highlights": ["luxurious", "practical", "comfortable"],
     "rating": 4.3, "popularity": 0.48, "tags": ["luxury"]},

    # Infiniti (new mainstream)
    {"id": "infiniti_q50_2024", "brand": "Infiniti", "model": "Q50 2024", "type": "Sedan",
     "price_usd": 43000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["sport", "luxury"], "highlights": ["sporty", "luxurious", "powerful"],
     "rating": 4.2, "popularity": 0.35, "tags": ["luxury"]},
    {"id": "infiniti_qx60_2024", "brand": "Infiniti", "model": "QX60 2024", "type": "SUV",
     "price_usd": 50000, "energy": "Gasoline", "seats": 7, "body": "SUV",
     "use_cases": ["family", "luxury"], "highlights": ["spacious", "luxurious", "comfortable"],
     "rating": 4.3, "popularity": 0.40, "tags": ["family", "luxury"]},

    # Lincoln (new mainstream)
    {"id": "lincoln_navigator_2024", "brand": "Lincoln", "model": "Navigator 2024", "type": "SUV",
     "price_usd": 80000, "energy": "Gasoline", "seats": 8, "body": "SUV",
     "use_cases": ["family", "luxury"], "highlights": ["ultra_luxurious", "spacious", "powerful"],
     "rating": 4.5, "popularity": 0.40, "tags": ["luxury", "family"]},
    {"id": "lincoln_aviator_2024", "brand": "Lincoln", "model": "Aviator 2024", "type": "SUV",
     "price_usd": 55000, "energy": "PHEV", "seats": 7, "body": "SUV",
     "use_cases": ["family", "luxury", "eco"], "highlights": ["luxurious", "spacious", "eco_friendly"],
     "rating": 4.4, "popularity": 0.35, "tags": ["luxury"]},

    # Cadillac (new mainstream)
    {"id": "cadillac_escalade_2024", "brand": "Cadillac", "model": "Escalade 2024", "type": "SUV",
     "price_usd": 86000, "energy": "Gasoline", "seats": 8, "body": "SUV",
     "use_cases": ["luxury", "family"], "highlights": ["ultra_luxurious", "spacious", "iconic"],
     "rating": 4.6, "popularity": 0.55, "tags": ["luxury"]},
    {"id": "cadillac_ct5_2024", "brand": "Cadillac", "model": "CT5 2024", "type": "Sedan",
     "price_usd": 40000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["sport", "luxury", "business"], "highlights": ["sporty", "luxurious", "tech_loaded"],
     "rating": 4.3, "popularity": 0.38, "tags": ["luxury"]},
    {"id": "cadillac_lyriq_2024", "brand": "Cadillac", "model": "Lyriq 2024", "type": "SUV",
     "price_usd": 58000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["luxury", "eco", "family"], "highlights": ["luxurious", "eco_friendly", "tech_loaded"],
     "rating": 4.4, "popularity": 0.35, "tags": ["ev", "luxury"]},

    # Land Rover (new niche)
    {"id": "landrover_rangerover_2024", "brand": "Land Rover", "model": "Range Rover 2024", "type": "SUV",
     "price_usd": 105000, "energy": "Hybrid", "seats": 5, "body": "SUV",
     "use_cases": ["luxury", "offroad"], "highlights": ["ultra_luxurious", "rugged", "iconic"],
     "rating": 4.6, "popularity": 0.50, "tags": ["luxury"]},
    {"id": "landrover_defender_2024", "brand": "Land Rover", "model": "Defender 2024", "type": "SUV",
     "price_usd": 55000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["offroad", "outdoor", "luxury"], "highlights": ["rugged", "offroad_capable", "iconic"],
     "rating": 4.5, "popularity": 0.55, "tags": ["offroad"]},
    {"id": "landrover_discovery_2024", "brand": "Land Rover", "model": "Discovery 2024", "type": "SUV",
     "price_usd": 60000, "energy": "Gasoline", "seats": 7, "body": "SUV",
     "use_cases": ["family", "offroad", "luxury"], "highlights": ["spacious", "rugged", "luxurious"],
     "rating": 4.3, "popularity": 0.40, "tags": ["family", "offroad"]},

    # Jaguar (new niche)
    {"id": "jaguar_fpace_2024", "brand": "Jaguar", "model": "F-Pace 2024", "type": "SUV",
     "price_usd": 52000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["sport", "luxury", "family"], "highlights": ["sporty", "luxurious", "great_handling"],
     "rating": 4.4, "popularity": 0.35, "tags": ["luxury", "sport"]},
    {"id": "jaguar_ipace_2024", "brand": "Jaguar", "model": "I-Pace 2024", "type": "SUV",
     "price_usd": 70000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["eco", "luxury", "sport"], "highlights": ["eco_friendly", "sporty", "luxurious"],
     "rating": 4.3, "popularity": 0.22, "tags": ["ev", "luxury"]},
    {"id": "jaguar_xf_2024", "brand": "Jaguar", "model": "XF 2024", "type": "Sedan",
     "price_usd": 48000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["business", "luxury"], "highlights": ["elegant", "luxurious", "comfortable"],
     "rating": 4.2, "popularity": 0.25, "tags": ["luxury"]},

    # Ferrari (new niche)
    {"id": "ferrari_roma_2024", "brand": "Ferrari", "model": "Roma 2024", "type": "Coupe",
     "price_usd": 250000, "energy": "Gasoline", "seats": 4, "body": "Coupe",
     "use_cases": ["sport", "luxury", "weekend"], "highlights": ["ultra_fast", "iconic", "ultra_luxurious"],
     "rating": 4.9, "popularity": 0.45, "tags": ["sport", "luxury"]},
    {"id": "ferrari_sf90_2024", "brand": "Ferrari", "model": "SF90 2024", "type": "Coupe",
     "price_usd": 500000, "energy": "PHEV", "seats": 2, "body": "Coupe",
     "use_cases": ["sport", "luxury"], "highlights": ["ultra_fast", "hybrid_power", "track_ready"],
     "rating": 4.9, "popularity": 0.40, "tags": ["sport", "luxury"]},
    {"id": "ferrari_296_2024", "brand": "Ferrari", "model": "296 GTB 2024", "type": "Coupe",
     "price_usd": 300000, "energy": "PHEV", "seats": 2, "body": "Coupe",
     "use_cases": ["sport", "weekend"], "highlights": ["ultra_fast", "hybrid_power", "precise_handling"],
     "rating": 4.9, "popularity": 0.35, "tags": ["sport"]},

    # Lamborghini (new niche)
    {"id": "lamborghini_huracan_2024", "brand": "Lamborghini", "model": "Huracan 2024", "type": "Coupe",
     "price_usd": 250000, "energy": "Gasoline", "seats": 2, "body": "Coupe",
     "use_cases": ["sport", "luxury", "weekend"], "highlights": ["ultra_fast", "iconic", "exotic"],
     "rating": 4.8, "popularity": 0.45, "tags": ["sport", "luxury"]},
    {"id": "lamborghini_urus_2024", "brand": "Lamborghini", "model": "Urus 2024", "type": "SUV",
     "price_usd": 230000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["sport", "luxury", "family"], "highlights": ["ultra_fast", "exotic", "spacious"],
     "rating": 4.7, "popularity": 0.50, "tags": ["sport", "luxury"]},
    {"id": "lamborghini_revuelto_2024", "brand": "Lamborghini", "model": "Revuelto 2024", "type": "Coupe",
     "price_usd": 600000, "energy": "PHEV", "seats": 2, "body": "Coupe",
     "use_cases": ["sport", "luxury"], "highlights": ["ultra_fast", "hybrid_power", "exotic"],
     "rating": 4.9, "popularity": 0.40, "tags": ["sport", "luxury"]},

    # McLaren (new niche)
    {"id": "mclaren_750s_2024", "brand": "McLaren", "model": "750S 2024", "type": "Coupe",
     "price_usd": 320000, "energy": "Gasoline", "seats": 2, "body": "Coupe",
     "use_cases": ["sport", "weekend"], "highlights": ["ultra_fast", "lightweight", "track_ready"],
     "rating": 4.8, "popularity": 0.30, "tags": ["sport"]},
    {"id": "mclaren_artura_2024", "brand": "McLaren", "model": "Artura 2024", "type": "Coupe",
     "price_usd": 230000, "energy": "PHEV", "seats": 2, "body": "Coupe",
     "use_cases": ["sport", "eco", "weekend"], "highlights": ["ultra_fast", "hybrid_power", "lightweight"],
     "rating": 4.7, "popularity": 0.28, "tags": ["sport"]},

    # Aston Martin (new niche)
    {"id": "astonmartin_db12_2024", "brand": "Aston Martin", "model": "DB12 2024", "type": "Coupe",
     "price_usd": 250000, "energy": "Gasoline", "seats": 4, "body": "Coupe",
     "use_cases": ["sport", "luxury", "weekend"], "highlights": ["ultra_luxurious", "ultra_fast", "elegant"],
     "rating": 4.8, "popularity": 0.35, "tags": ["sport", "luxury"]},
    {"id": "astonmartin_vantage_2024", "brand": "Aston Martin", "model": "Vantage 2024", "type": "Coupe",
     "price_usd": 190000, "energy": "Gasoline", "seats": 2, "body": "Coupe",
     "use_cases": ["sport", "weekend"], "highlights": ["ultra_fast", "sporty", "iconic"],
     "rating": 4.7, "popularity": 0.30, "tags": ["sport"]},
    {"id": "astonmartin_dbx_2024", "brand": "Aston Martin", "model": "DBX 2024", "type": "SUV",
     "price_usd": 200000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["luxury", "sport", "family"], "highlights": ["ultra_luxurious", "sporty", "spacious"],
     "rating": 4.6, "popularity": 0.35, "tags": ["luxury", "sport"]},

    # Maserati (new niche)
    {"id": "maserati_grecale_2024", "brand": "Maserati", "model": "Grecale 2024", "type": "SUV",
     "price_usd": 65000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["luxury", "sport", "family"], "highlights": ["luxurious", "sporty", "italian_design"],
     "rating": 4.4, "popularity": 0.30, "tags": ["luxury"]},
    {"id": "maserati_levante_2024", "brand": "Maserati", "model": "Levante 2024", "type": "SUV",
     "price_usd": 85000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["luxury", "sport"], "highlights": ["luxurious", "sporty", "powerful"],
     "rating": 4.5, "popularity": 0.32, "tags": ["luxury"]},
    {"id": "maserati_mc20_2024", "brand": "Maserati", "model": "MC20 2024", "type": "Coupe",
     "price_usd": 230000, "energy": "Gasoline", "seats": 2, "body": "Coupe",
     "use_cases": ["sport", "luxury"], "highlights": ["ultra_fast", "exotic", "ultra_luxurious"],
     "rating": 4.8, "popularity": 0.25, "tags": ["sport", "luxury"]},

    # Bentley (new niche)
    {"id": "bentley_bentayga_2024", "brand": "Bentley", "model": "Bentayga 2024", "type": "SUV",
     "price_usd": 200000, "energy": "Hybrid", "seats": 5, "body": "SUV",
     "use_cases": ["luxury", "family"], "highlights": ["ultra_luxurious", "spacious", "powerful"],
     "rating": 4.7, "popularity": 0.35, "tags": ["luxury"]},
    {"id": "bentley_continental_2024", "brand": "Bentley", "model": "Continental GT 2024", "type": "Coupe",
     "price_usd": 250000, "energy": "Gasoline", "seats": 4, "body": "Coupe",
     "use_cases": ["luxury", "sport"], "highlights": ["ultra_luxurious", "ultra_fast", "elegant"],
     "rating": 4.8, "popularity": 0.40, "tags": ["luxury", "sport"]},

    # Rolls-Royce (new niche)
    {"id": "rollsroyce_phantom_2024", "brand": "Rolls-Royce", "model": "Phantom 2024", "type": "Sedan",
     "price_usd": 500000, "energy": "Gasoline", "seats": 5, "body": "Sedan",
     "use_cases": ["luxury", "business"], "highlights": ["ultra_luxurious", "iconic", "handcrafted"],
     "rating": 4.9, "popularity": 0.35, "tags": ["luxury"]},
    {"id": "rollsroyce_cullinan_2024", "brand": "Rolls-Royce", "model": "Cullinan 2024", "type": "SUV",
     "price_usd": 400000, "energy": "Gasoline", "seats": 5, "body": "SUV",
     "use_cases": ["luxury", "family", "offroad"], "highlights": ["ultra_luxurious", "spacious", "powerful"],
     "rating": 4.8, "popularity": 0.40, "tags": ["luxury"]},

    # VinFast (new niche)
    {"id": "vinfast_vf8_2024", "brand": "VinFast", "model": "VF8 2024", "type": "SUV",
     "price_usd": 43000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "eco", "commute"], "highlights": ["affordable_ev", "spacious", "practical"],
     "rating": 4.0, "popularity": 0.20, "tags": ["ev", "value"]},
    {"id": "vinfast_vf9_2024", "brand": "VinFast", "model": "VF9 2024", "type": "SUV",
     "price_usd": 55000, "energy": "BEV", "seats": 7, "body": "SUV",
     "use_cases": ["family", "eco", "luxury"], "highlights": ["spacious", "eco_friendly", "luxurious"],
     "rating": 4.1, "popularity": 0.18, "tags": ["ev", "family"]},

    # Fisker (new niche)
    {"id": "fisker_ocean_2024", "brand": "Fisker", "model": "Ocean 2024", "type": "SUV",
     "price_usd": 45000, "energy": "BEV", "seats": 5, "body": "SUV",
     "use_cases": ["family", "eco", "luxury"], "highlights": ["eco_friendly", "spacious", "unique_design"],
     "rating": 4.0, "popularity": 0.18, "tags": ["ev"]},

    # Chevrolet Corvette Z06 (high-end sport)
    {"id": "chevy_corvette_z06_2024", "brand": "Chevrolet", "model": "Corvette Z06 2024", "type": "Coupe",
     "price_usd": 110000, "energy": "Gasoline", "seats": 2, "body": "Coupe",
     "use_cases": ["sport", "weekend"], "highlights": ["ultra_fast", "track_ready", "exotic"],
     "rating": 4.9, "popularity": 0.45, "tags": ["sport"]},

    # Ford Mustang GTD (high-end sport)
    {"id": "ford_mustang_gtd_2024", "brand": "Ford", "model": "Mustang GTD 2024", "type": "Coupe",
     "price_usd": 80000, "energy": "Gasoline", "seats": 2, "body": "Coupe",
     "use_cases": ["sport", "weekend"], "highlights": ["ultra_fast", "track_ready", "iconic"],
     "rating": 4.7, "popularity": 0.40, "tags": ["sport"]},

    # Toyota Crown (luxury sedan)
    {"id": "toyota_crown_2024", "brand": "Toyota", "model": "Crown 2024", "type": "Sedan",
     "price_usd": 41000, "energy": "Hybrid", "seats": 5, "body": "Sedan",
     "use_cases": ["luxury", "family", "business"], "highlights": ["luxurious", "comfortable", "fuel_efficient"],
     "rating": 4.4, "popularity": 0.45, "tags": ["luxury"]},

    # Honda Civic Type R (hot hatch)
    {"id": "honda_civic_typer_2024", "brand": "Honda", "model": "Civic Type R 2024", "type": "Hatchback",
     "price_usd": 44000, "energy": "Gasoline", "seats": 5, "body": "Hatchback",
     "use_cases": ["sport", "weekend"], "highlights": ["fast", "track_ready", "fun_to_drive"],
     "rating": 4.6, "popularity": 0.45, "tags": ["sport"]},
]

MAINSTREAM_BRANDS = {
    "Toyota", "Honda", "Tesla", "BMW", "Mercedes-Benz", "Audi",
    "Volkswagen", "Ford", "Chevrolet", "Hyundai", "Kia", "Nissan",
    "Acura", "Infiniti", "Lincoln", "Cadillac"
}

NICHE_BRANDS = {
    "BYD", "NIO", "Xpeng", "Li Auto", "Polestar", "Rivian",
    "Lucid", "Genesis", "Mini", "Subaru", "Mazda", "Volvo",
    "Porsche", "Lexus", "Buick",
    "Land Rover", "Jaguar", "Ferrari", "Lamborghini", "McLaren",
    "Aston Martin", "Maserati", "Bentley", "Rolls-Royce",
    "VinFast", "Fisker"
}


def get_catalog():
    """Return the full car catalog."""
    return CAR_CATALOG


def get_car_by_id(car_id):
    """Find a car by its unique id. Returns None if not found."""
    for car in CAR_CATALOG:
        if car["id"] == car_id:
            return car
    return None


def filter_by_budget(max_budget, catalog=None):
    """Return cars at or below the given budget from catalog (defaults to full catalog)."""
    if catalog is None:
        catalog = CAR_CATALOG
    return [c for c in catalog if c["price_usd"] <= max_budget]


def filter_by_use_case(use_case, catalog=None):
    """Return cars matching the given use case from catalog (defaults to full catalog)."""
    if catalog is None:
        catalog = CAR_CATALOG
    return [c for c in catalog if use_case in c["use_cases"]]


def get_brand_stats():
    """Return per-brand counts and mainstream/niche classification."""
    brands = {}
    for car in CAR_CATALOG:
        b = car["brand"]
        if b not in brands:
            brands[b] = {"count": 0, "mainstream": b in MAINSTREAM_BRANDS}
        brands[b]["count"] += 1
    return brands


def save_catalog(path):
    """Write the catalog to a JSON file, creating directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(CAR_CATALOG, f, indent=2)


if __name__ == "__main__":
    output = Path(__file__).parent.parent / "data" / "processed" / "cars.json"
    save_catalog(str(output))
    print(f"Saved {len(CAR_CATALOG)} cars to {output}")
    brands = get_brand_stats()
    mainstream = sum(1 for b in brands.values() if b["mainstream"])
    niche = len(brands) - mainstream
    print(f"Brands: {len(brands)} total ({mainstream} mainstream, {niche} niche)")
