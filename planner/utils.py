import json
from datetime import datetime, timedelta
import math
from pathlib import Path

BASE_SPEED_KMPH = 40

def parse_time(tstr):
    return datetime.strptime(tstr, "%H:%M")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda / 2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_traffic_multiplier(current_time):
    hour = current_time.hour + current_time.minute / 60
    if 7.0 <= hour < 9.0:
        return 1.8
    elif 9.0 <= hour < 11.0:
        return 1.2
    elif 11.0 <= hour < 14.0:
        return 1.0
    elif 14.0 <= hour < 16.0:
        return 1.4
    else:
        return 1.0

def travel_time_minutes(lat1, lon1, lat2, lon2, current_time):
    distance_km = haversine(lat1, lon1, lat2, lon2)
    base_time = distance_km / BASE_SPEED_KMPH * 60
    return base_time * get_traffic_multiplier(current_time)

def optimize_visits(work_start_str, work_end_str):
    BASE_DIR = Path(__file__).resolve().parent.parent
    with open(BASE_DIR / "customers.json") as f:
        customers = json.load(f)

    with open(BASE_DIR / "start-point.json") as f:
        start_point = json.load(f)

    WORK_START = parse_time(work_start_str)
    WORK_END = parse_time(work_end_str)

    for c in customers:
        c["available_from"] = parse_time(c["available_from"])
        c["available_to"] = parse_time(c["available_to"])

    visited = []
    current_time = WORK_START
    current_location = (start_point["Lat"], start_point["Lng"])
    remaining_customers = customers.copy()

    while current_time < WORK_END:
        feasible = []

        for c in remaining_customers:
            travel = travel_time_minutes(current_location[0], current_location[1], c["lat"], c["lng"], current_time)
            arrival_time = current_time + timedelta(minutes=travel)
            wait_time = max(c["available_from"] - arrival_time, timedelta(0))
            start_visit = arrival_time + wait_time
            end_visit = start_visit + timedelta(minutes=c["visit_duration_minutes"])

            if (start_visit >= c["available_from"] and end_visit <= c["available_to"] and end_visit <= WORK_END):
                total_time = travel + wait_time.total_seconds()/60 + c["visit_duration_minutes"]
                feasible.append((c, start_visit, end_visit, total_time))

        if not feasible:
            break

        feasible.sort(key=lambda x: x[0]["visit_value"] / x[3], reverse=True)
        selected, start_visit, end_visit, total_time = feasible[0]

        visited.append({
            "id": selected["id"],
            "start_visit": start_visit.strftime("%H:%M"),
            "end_visit": end_visit.strftime("%H:%M"),
            "visit_value": selected["visit_value"]
        })

        current_time = end_visit
        current_location = (selected["lat"], selected["lng"])
        remaining_customers.remove(selected)

    return visited
