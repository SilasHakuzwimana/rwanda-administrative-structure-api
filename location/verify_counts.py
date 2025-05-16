from location.models import Province, District, Sector, Cell, Village

# Official expected totals
expected = {
    "Provinces": 5,
    "Districts": 30,
    "Sectors": 416,
    "Cells": 2148,
    "Villages": 14837
}

# Actual database counts
actual = {
    "Provinces": Province.objects.count(),
    "Districts": District.objects.count(),
    "Sectors": Sector.objects.count(),
    "Cells": Cell.objects.count(),
    "Villages": Village.objects.count()
}

print("\n📊 Rwanda Administrative Units Status")
print("-" * 50)

for level in expected:
    found = actual[level]
    required = expected[level]
    status = "✅ OK" if found == required else f"❌ Missing {required - found}"
    print(f"{level:<10}: {found:>5} / {required:<5} → {status}")

print("-" * 50)
print(f"Total: {sum(actual.values()):<5} / {sum(expected.values()):<5} → {'✅ OK' if sum(actual.values()) == sum(expected.values()) else '❌ Mismatch'}")
print("-" * 50)
print("Please check the above counts and ensure they match the expected values.")