/**
 * Inventory data for Matthew's Stop and Look Auto Sales.
 *
 * This file is the single source of truth for every vehicle shown on the site.
 * Replace the SAMPLE vehicles below with real stock by running the scraper:
 *
 *     cd scraper && python3 scrape_inventory.py
 *
 * The scraper rewrites this file from the live 313carloans.com inventory.
 * You can also edit vehicles by hand — it's plain data, no build step needed.
 *
 * NOTE: vehicle photos are AI-generated stand-ins (Higgsfield) hotlinked from
 * its CDN — the scraper replaces them with the dealership's real photos.
 *
 * Loaded as a plain <script> (not fetch) so the site also works when opened
 * directly from disk (file://) without a web server.
 */
window.INVENTORY = {
  updated: "2026-07-21",
  dealership: {
    name: "Matthew's Stop and Look Auto Sales",
    legalName: "McQueen Auto, Inc.",
    phone: "313-891-8000",
    phoneHref: "tel:+13138918000",
    address: "8146 E 8 Mile Rd, Detroit, MI 48234",
    mapsUrl: "https://maps.google.com/?q=8146+E+8+Mile+Rd,+Detroit,+MI+48234"
  },
  vehicles: [
    {
      id: "sample-001",
      year: 2019, make: "Chevrolet", model: "Malibu", trim: "LT",
      price: 13995, mileage: 68420,
      bodyStyle: "Sedan", exteriorColor: "Summit White", interiorColor: "Jet Black",
      engine: "1.5L Turbo I4", transmission: "Automatic", drivetrain: "FWD",
      fuel: "Gasoline", mpgCity: 29, mpgHwy: 36,
      vin: "", stock: "A1001",
      description: "Clean one-owner Malibu LT with backup camera, Apple CarPlay / Android Auto, and remote start. Fresh oil change and full inspection.",
      features: ["Backup Camera", "Apple CarPlay", "Remote Start", "Alloy Wheels", "Bluetooth"],
      images: ["https://d8j0ntlcm91z4.cloudfront.net/user_3F5HWbv7Bu2aaFUxJxfa9tx8cxS/hf_20260721_201856_ed53a64d-29d4-472a-a88d-0d62c6bc6244_min.webp"],
      featured: true, sold: false
    },
    {
      id: "sample-002",
      year: 2018, make: "Ford", model: "Escape", trim: "SE",
      price: 12495, mileage: 81230,
      bodyStyle: "SUV", exteriorColor: "Magnetic Gray", interiorColor: "Charcoal",
      engine: "1.5L EcoBoost I4", transmission: "Automatic", drivetrain: "AWD",
      fuel: "Gasoline", mpgCity: 22, mpgHwy: 28,
      vin: "", stock: "A1002",
      description: "AWD Escape SE — perfect for Michigan winters. Heated seats, power liftgate, and new tires all around.",
      features: ["AWD", "Heated Seats", "Power Liftgate", "New Tires", "Keyless Entry"],
      images: ["https://d8j0ntlcm91z4.cloudfront.net/user_3F5HWbv7Bu2aaFUxJxfa9tx8cxS/hf_20260721_201857_651a250b-718a-4939-b48f-1876f41300d3_min.webp"],
      featured: true, sold: false
    },
    {
      id: "sample-003",
      year: 2017, make: "Jeep", model: "Grand Cherokee", trim: "Laredo",
      price: 15995, mileage: 92110,
      bodyStyle: "SUV", exteriorColor: "Granite Crystal", interiorColor: "Black",
      engine: "3.6L V6", transmission: "Automatic", drivetrain: "4WD",
      fuel: "Gasoline", mpgCity: 18, mpgHwy: 25,
      vin: "", stock: "A1003",
      description: "4x4 Grand Cherokee Laredo with tow package, big touchscreen, and a strong V6. Runs and drives excellent.",
      features: ["4x4", "Tow Package", "Touchscreen", "Cruise Control", "Fog Lights"],
      images: ["https://d8j0ntlcm91z4.cloudfront.net/user_3F5HWbv7Bu2aaFUxJxfa9tx8cxS/hf_20260721_201859_22bc1e8b-ac6e-421d-8be1-1191d6b7ded9_min.webp"],
      featured: true, sold: false
    },
    {
      id: "sample-004",
      year: 2016, make: "Chrysler", model: "300", trim: "Limited",
      price: 11995, mileage: 98760,
      bodyStyle: "Sedan", exteriorColor: "Gloss Black", interiorColor: "Linen Beige",
      engine: "3.6L V6", transmission: "Automatic", drivetrain: "RWD",
      fuel: "Gasoline", mpgCity: 19, mpgHwy: 31,
      vin: "", stock: "A1004",
      description: "Detroit classic. Leather, heated seats, premium sound. Sharp black-on-beige combo that turns heads.",
      features: ["Leather Seats", "Heated Seats", "Premium Audio", "Push-Button Start"],
      images: ["https://d8j0ntlcm91z4.cloudfront.net/user_3F5HWbv7Bu2aaFUxJxfa9tx8cxS/hf_20260721_201900_58de559d-3820-404c-9e2b-498c043ddca8_min.webp"],
      featured: false, sold: false
    },
    {
      id: "sample-005",
      year: 2015, make: "Ford", model: "F-150", trim: "XLT SuperCrew",
      price: 17995, mileage: 104500,
      bodyStyle: "Truck", exteriorColor: "Oxford White", interiorColor: "Gray",
      engine: "5.0L V8", transmission: "Automatic", drivetrain: "4WD",
      fuel: "Gasoline", mpgCity: 15, mpgHwy: 21,
      vin: "", stock: "A1005",
      description: "Work-ready F-150 XLT 4x4 with the 5.0 V8. Crew cab seats five, bed liner included, tows with confidence.",
      features: ["4x4", "V8", "Crew Cab", "Bed Liner", "Trailer Hitch"],
      images: ["https://d8j0ntlcm91z4.cloudfront.net/user_3F5HWbv7Bu2aaFUxJxfa9tx8cxS/hf_20260721_201902_daf48ce3-febd-4be0-8930-8902acc0c4b6_min.webp"],
      featured: true, sold: false
    },
    {
      id: "sample-006",
      year: 2018, make: "Chevrolet", model: "Equinox", trim: "LS",
      price: 11495, mileage: 88900,
      bodyStyle: "SUV", exteriorColor: "Silver Ice", interiorColor: "Jet Black",
      engine: "1.5L Turbo I4", transmission: "Automatic", drivetrain: "FWD",
      fuel: "Gasoline", mpgCity: 26, mpgHwy: 32,
      vin: "", stock: "A1006",
      description: "Fuel-efficient Equinox LS with backup camera and touchscreen. Great first car or family runabout.",
      features: ["Backup Camera", "Touchscreen", "Bluetooth", "Steering Wheel Controls"],
      images: ["https://d8j0ntlcm91z4.cloudfront.net/user_3F5HWbv7Bu2aaFUxJxfa9tx8cxS/hf_20260721_201902_e8d748a1-9fdd-469d-8ad2-157c39e710a4_min.webp"],
      featured: false, sold: false
    },
    {
      id: "sample-007",
      year: 2017, make: "Dodge", model: "Charger", trim: "SXT",
      price: 14995, mileage: 76540,
      bodyStyle: "Sedan", exteriorColor: "Pitch Black", interiorColor: "Black",
      engine: "3.6L V6", transmission: "Automatic", drivetrain: "RWD",
      fuel: "Gasoline", mpgCity: 19, mpgHwy: 30,
      vin: "", stock: "A1007",
      description: "Aggressive-looking Charger SXT with sport seats and big-screen Uconnect. Well maintained, ready to roll.",
      features: ["Sport Seats", "Uconnect", "Dual Exhaust", "Alloy Wheels"],
      images: ["https://d8j0ntlcm91z4.cloudfront.net/user_3F5HWbv7Bu2aaFUxJxfa9tx8cxS/hf_20260721_201909_48464353-a067-4ed2-97e9-3f281c5ecc1c_min.webp"],
      featured: false, sold: false
    },
    {
      id: "sample-008",
      year: 2016, make: "GMC", model: "Terrain", trim: "SLE",
      price: 10995, mileage: 95300,
      bodyStyle: "SUV", exteriorColor: "Onyx Black", interiorColor: "Jet Black",
      engine: "2.4L I4", transmission: "Automatic", drivetrain: "FWD",
      fuel: "Gasoline", mpgCity: 21, mpgHwy: 31,
      vin: "", stock: "A1008",
      description: "Roomy Terrain SLE with Pioneer sound and rear camera. Solid, comfortable, and easy on gas.",
      features: ["Pioneer Audio", "Backup Camera", "Roof Rails", "Power Seat"],
      images: ["https://d8j0ntlcm91z4.cloudfront.net/user_3F5HWbv7Bu2aaFUxJxfa9tx8cxS/hf_20260721_201911_277f5395-7ea9-4c61-bdf6-ea0434ef8f21_min.webp"],
      featured: false, sold: false
    },
    {
      id: "sample-009",
      year: 2015, make: "Buick", model: "Enclave", trim: "Leather Group",
      price: 12995, mileage: 101200,
      bodyStyle: "SUV", exteriorColor: "White Diamond", interiorColor: "Ebony",
      engine: "3.6L V6", transmission: "Automatic", drivetrain: "AWD",
      fuel: "Gasoline", mpgCity: 16, mpgHwy: 22,
      vin: "", stock: "A1009",
      description: "Three rows of leather comfort. AWD Enclave with heated seats, remote start, and room for seven.",
      features: ["Third Row", "Leather Seats", "AWD", "Heated Seats", "Remote Start"],
      images: ["https://d8j0ntlcm91z4.cloudfront.net/user_3F5HWbv7Bu2aaFUxJxfa9tx8cxS/hf_20260721_201912_c611ecda-6c32-49f5-a04d-6db37b59c3c0_min.webp"],
      featured: false, sold: false
    },
    {
      id: "sample-010",
      year: 2019, make: "Ford", model: "Fusion", trim: "SE",
      price: 13495, mileage: 71800,
      bodyStyle: "Sedan", exteriorColor: "Velocity Blue", interiorColor: "Ebony",
      engine: "1.5L EcoBoost I4", transmission: "Automatic", drivetrain: "FWD",
      fuel: "Gasoline", mpgCity: 23, mpgHwy: 34,
      vin: "", stock: "A1010",
      description: "Sharp blue Fusion SE with SYNC 3, lane-keep assist, and adaptive cruise. Drives like new.",
      features: ["SYNC 3", "Lane-Keep Assist", "Adaptive Cruise", "Backup Camera"],
      images: ["https://d8j0ntlcm91z4.cloudfront.net/user_3F5HWbv7Bu2aaFUxJxfa9tx8cxS/hf_20260721_201914_a3c8589d-ae7c-4819-9809-8a059bac3afc_min.webp"],
      featured: false, sold: false
    },
    {
      id: "sample-011",
      year: 2014, make: "Chevrolet", model: "Impala", trim: "LT",
      price: 8995, mileage: 112400,
      bodyStyle: "Sedan", exteriorColor: "Champagne Silver", interiorColor: "Jet Black",
      engine: "3.6L V6", transmission: "Automatic", drivetrain: "FWD",
      fuel: "Gasoline", mpgCity: 18, mpgHwy: 28,
      vin: "", stock: "A1011",
      description: "Budget-friendly full-size Impala LT. Smooth V6, cold A/C, big trunk. Cash-friendly price.",
      features: ["V6", "Cold A/C", "Power Windows", "Cruise Control"],
      images: ["https://d8j0ntlcm91z4.cloudfront.net/user_3F5HWbv7Bu2aaFUxJxfa9tx8cxS/hf_20260721_201916_95002857-004f-48b5-8504-2722fdb066b1_min.webp"],
      featured: false, sold: false
    },
    {
      id: "sample-012",
      year: 2017, make: "Dodge", model: "Journey", trim: "SE",
      price: 9995, mileage: 89600,
      bodyStyle: "SUV", exteriorColor: "Granite Pearl", interiorColor: "Black",
      engine: "2.4L I4", transmission: "Automatic", drivetrain: "FWD",
      fuel: "Gasoline", mpgCity: 19, mpgHwy: 25,
      vin: "", stock: "A1012",
      description: "Affordable 7-passenger Journey SE. Flexible seating, hidden storage, and an easy monthly payment.",
      features: ["Third Row", "Hidden Storage", "Keyless Entry", "Bluetooth"],
      images: ["https://d8j0ntlcm91z4.cloudfront.net/user_3F5HWbv7Bu2aaFUxJxfa9tx8cxS/hf_20260721_201916_cc0664c2-143b-4798-81a0-7aa35912dd83_min.webp"],
      featured: false, sold: false
    }
  ]
};
