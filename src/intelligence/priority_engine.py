import time
import logging

logger = logging.getLogger(__name__)

class PriorityEngine:
    """The 'Brain' that ranks obstacles by threat level."""

    # Weights for different object classes (1.0 to 10.0)
    HAZARD_WEIGHTS = {
        "person": 10.0,
        "car":    10.0,
        "bicycle": 9.0,
        "stairs":  9.5,
        "bus":     10.0,
        "truck":   10.0,
        "door":    5.0,
        "wall":    5.0,
        "chair":   2.0,
        "table":   2.0,
        "bottle":  1.0,
        "purse":   1.0,
        "handbag": 1.0
    }

    def __init__(self, threshold_high=7.0, threshold_moderate=3.0, alert_cooldown=5.0, static_cooldown=30.0):
        self.threshold_high = threshold_high
        self.threshold_moderate = threshold_moderate
        self.alert_cooldown = alert_cooldown
        self.static_cooldown = static_cooldown
        self.last_alerts = {} # Class -> {'time': timestamp, 'distance': float}

    def calculate_threat_score(self, obj_class: str, distance: float, velocity: float = 0.0) -> float:
        """
        Calculate threat score: (Weight * Velocity_Factor) / Distance.
        Velocity_Factor is > 1.0 if moving toward user, < 1.0 if moving away.
        """
        weight = self.HAZARD_WEIGHTS.get(obj_class.lower(), 1.0)
        
        # Simple velocity factor: 1.0 (static), 1.5 (approaching), 0.5 (receding)
        v_factor = 1.0 + (velocity * 0.5) 
        
        # Avoid division by zero
        score = (weight * v_factor) / max(distance, 0.1)
        return round(score, 2)

    def process_detections(self, detections: list, on_request: bool = False) -> list:
        """
        Process a list of detections and return those that should be announced.
        Detections format: {'class': str, 'distance': float, 'velocity': float}
        """
        to_announce = []
        
        now = time.time()
        
        for det in detections:
            obj_class = det['class']
            dist = det['distance']
            score = self.calculate_threat_score(obj_class, dist, det.get('velocity', 0.0))
            
            # --- Alert Suppression Logic ---
            last_info = self.last_alerts.get(obj_class, {'time': 0, 'distance': -1})
            time_since = now - last_info['time']
            last_dist = last_info['distance']
            
            # Has the object moved significantly closer?
            # MobileNet bounding boxes jitter a lot, causing fake distance jumps.
            # We need a large threshold (e.g. 1.0m) to ignore this jitter.
            got_closer = (last_dist != -1) and (last_dist - dist > 0.8)
            
            if got_closer:
                is_cooldown_active = False  # Override cooldown if danger is approaching
                logger.info(f"Target approached. Dist jumped from {last_dist} to {dist}")
            elif last_dist != -1 and abs(last_dist - dist) < 1.2:
                # If distance fluctuates by less than 1.2m, assume it's just camera jitter.
                is_cooldown_active = time_since < self.static_cooldown  
            else:
                is_cooldown_active = time_since < self.alert_cooldown   # Normal cooldown

            # 1. High Threat (Immediate Alert)
            if score >= self.threshold_high and not is_cooldown_active:
                msg = f"Danger! {obj_class} very close, about {dist} meters."
                to_announce.append({'level': 'CRITICAL', 'msg': msg, 'score': score})
                self.last_alerts[obj_class] = {'time': now, 'distance': dist}
            
            # 2. Moderate Threat (Alert)
            elif score >= self.threshold_moderate and not is_cooldown_active:
                msg = f"{obj_class} ahead, {dist} meters."
                to_announce.append({'level': 'WARNING', 'msg': msg, 'score': score})
                self.last_alerts[obj_class] = {'time': now, 'distance': dist}
            
            # 3. Low Priority (Only on request - No cooldown needed for manual requests)
            elif on_request:
                to_announce.append({'level': 'INFO', 'msg': f"I see a {obj_class}.", 'score': score})

        return to_announce
