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
      images: ["assets/placeholder-sedan.svg"],
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
      images: ["assets/placeholder-suv.svg"],
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
      images: ["assets/placeholder-suv.svg"],
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
      images: ["assets/placeholder-sedan.svg"],
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
      images: ["assets/placeholder-truck.svg"],
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
      images: ["assets/placeholder-suv.svg"],
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
      images: ["assets/placeholder-sedan.svg"],
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
      images: ["assets/placeholder-suv.svg"],
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
      images: ["assets/placeholder-suv.svg"],
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
      images: ["assets/placeholder-sedan.svg"],
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
      images: ["assets/placeholder-sedan.svg"],
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
      images: ["assets/placeholder-suv.svg"],
      featured: false, sold: false
    }
  ]
};
