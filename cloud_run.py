import scheduler
import time

def run_once():
    print("--- Cloud Run Started ---")
    
    # 1. Update Config Cache
    scheduler.update_config_cache()
    
    # 2. Run Collection
    print("Running Collection Phase...")
    scheduler.task_collection()
    
    # 3. Run Delivery Check (Force check regardless of exact minute, but check time correctness)
    # Actually, cloud run is hourly. We want to deliver if the time matches "this hour"?
    # Schedulf logic checks "minutes".
    # If GitHub runs at 10:00, and user set 17:00, task_delivery checks current time.
    # It works fine.
    
    print("Running Delivery Phase...")
    # Force delivery for Cloud Run execution (Since GHA schedule controls the time)
    scheduler.task_delivery(force=True)
    
    print("--- Cloud Run Complete ---")

if __name__ == "__main__":
    run_once()
