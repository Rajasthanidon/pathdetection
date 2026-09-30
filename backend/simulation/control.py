import math
from .config import Config

class Controller:
    @staticmethod
    def pure_pursuit(ego, path, target_speed):
        if not path:
            # Emergency brake if no path
            return -Config.MAX_DECEL, 0.0 # Accel is negative for braking
            
        # Find lookahead point
        lookahead_idx = min(5, len(path)-1)
        target = path[lookahead_idx]
        
        dx = target[0] - ego.x
        dy = target[1] - ego.y
        alpha = math.atan2(dy, dx) - ego.heading
        
        alpha = (alpha + math.pi) % (2 * math.pi) - math.pi
        
        ld = math.hypot(dx, dy)
        
        if ld > 0:
            target_steer = math.atan2(2.0 * Config.WHEELBASE * math.sin(alpha), ld)
        else:
            target_steer = 0.0
            
        # Apply Steering Rate Limit
        max_delta = Config.MAX_STEER_RATE * Config.DT
        steer_diff = target_steer - ego.steer
        
        if steer_diff > max_delta:
            steer = ego.steer + max_delta
        elif steer_diff < -max_delta:
            steer = ego.steer - max_delta
        else:
            steer = target_steer
            
        # Hard cap at max steer limits
        steer = max(-Config.MAX_STEER, min(Config.MAX_STEER, steer))
            
        # Speed control (P controller)
        speed_err = target_speed - ego.speed
        accel = speed_err * 1.5 
        
        return accel, steer
