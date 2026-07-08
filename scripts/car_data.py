"""
Car database for CarRec AI recommendation system.

Generates a structured catalog of 70+ vehicles across brands, types,
price tiers, and energy sources. Supports fairness-aware recommendations
by including both mainstream and niche brands.
"""

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
]

MAINSTREAM_BRANDS = {
    "Toyota", "Honda", "Tesla", "BMW", "Mercedes-Benz", "Audi",
    "Volkswagen", "Ford", "Chevrolet", "Hyundai", "Kia", "Nissan"
}

NICHE_BRANDS = {
    "BYD", "NIO", "Xpeng", "Li Auto", "Polestar", "Rivian",
    "Lucid", "Genesis", "Mini", "Subaru", "Mazda", "Volvo",
    "Porsche", "Lexus", "Buick"
}


def get_catalog():
    return CAR_CATALOG


def get_car_by_id(car_id):
    for car in CAR_CATALOG:
        if car["id"] == car_id:
            return car
    return None


def filter_by_budget(max_budget, catalog=None):
    if catalog is None:
        catalog = CAR_CATALOG
    return [c for c in catalog if c["price_usd"] <= max_budget]


def filter_by_use_case(use_case, catalog=None):
    if catalog is None:
        catalog = CAR_CATALOG
    return [c for c in catalog if use_case in c["use_cases"]]


def get_brand_stats():
    brands = {}
    for car in CAR_CATALOG:
        b = car["brand"]
        if b not in brands:
            brands[b] = {"count": 0, "mainstream": b in MAINSTREAM_BRANDS}
        brands[b]["count"] += 1
    return brands


def save_catalog(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(CAR_CATALOG, f, indent=2)


def load_catalog(path):
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
    output = Path(__file__).parent.parent / "data" / "processed" / "cars.json"
    save_catalog(str(output))
    print(f"Saved {len(CAR_CATALOG)} cars to {output}")
    brands = get_brand_stats()
    mainstream = sum(1 for b in brands.values() if b["mainstream"])
    niche = len(brands) - mainstream
    print(f"Brands: {len(brands)} total ({mainstream} mainstream, {niche} niche)")
