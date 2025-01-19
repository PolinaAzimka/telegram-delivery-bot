
# Tariffs and formulas for calculation
FIRST_KG_COST = 3000  # Yen
ADDITIONAL_HALF_KG_COST = 1000  # Yen per 0.5 kg
VOLUME_WEIGHT_DIVISOR = 5000  # Calculation for volume weight

def calculate_delivery_cost(weight_kg):
    if weight_kg <= 1:
        return FIRST_KG_COST
    else:
        additional_weight = (weight_kg - 1) * 2  # Since cost is for each 0.5 kg
        return FIRST_KG_COST + (additional_weight * ADDITIONAL_HALF_KG_COST)
