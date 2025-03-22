import random
import threading
import time

class FaultInjector:
    def __init__(self):
        self.active_faults = {}
        self.recovery_actions = []
        self.fault_types = {
            'cpu_overload': {
                'simulate': self._simulate_cpu_overload,
                'recovery': self._recover_cpu_overload
            },
            'memory_leak': {
                'simulate': self._simulate_memory_leak,
                'recovery': self._recover_memory_leak
            },
            'disk_fill': {
                'simulate': self._simulate_disk_fill,
                'recovery': self._recover_disk_fill
            }
        }
        self._lock = threading.Lock()
        self.recovery_in_progress = False

    def inject_fault(self, fault_type, duration=30):
        if fault_type in self.fault_types:
            with self._lock:
                self.active_faults[fault_type] = {
                    'active': True,
                    'start_time': time.time(),
                    'duration': duration,
                    'recovery_attempted': False
                }
            
            # Start recovery thread
            recovery_thread = threading.Thread(
                target=self._execute_recovery,
                args=(fault_type,),
                daemon=True
            )
            recovery_thread.start()
            return True
        return False

    def _execute_recovery(self, fault_type):
        try:
            # Initialize recovery actions
            if fault_type == 'cpu_overload':
                self._recover_cpu_overload()
            elif fault_type == 'memory_leak':
                self._recover_memory_leak()
            elif fault_type == 'disk_fill':
                self._recover_disk_fill()
                
            time.sleep(5)  # Allow time for recovery visualization
            
            # Clear fault and recovery actions
            with self._lock:
                if fault_type in self.active_faults:
                    self.active_faults[fault_type]['active'] = False
                self.recovery_actions = []
                
        except Exception as e:
            print(f"Recovery error: {e}")

    def _simulate_cpu_overload(self, metrics):
        metrics['cpu_usage'] = min(95.0, metrics['cpu_usage'] + 45.0)

    def _recover_cpu_overload(self):
        actions = [
            {"step": 1, "action": "Identifying resource-intensive processes", "status": "pending"},
            {"step": 2, "action": "Analyzing CPU usage patterns", "status": "pending"},
            {"step": 3, "action": "Optimizing process priorities", "status": "pending"},
            {"step": 4, "action": "Implementing load balancing", "status": "pending"},
            {"step": 5, "action": "Verifying system stability", "status": "pending"}
        ]
        
        with self._lock:
            self.recovery_actions = actions

        # Simulate the recovery process
        for action in self.recovery_actions:
            with self._lock:
                action["status"] = "in_progress"
            time.sleep(2)  # Simulate work being done
            with self._lock:
                action["status"] = "complete"
            time.sleep(1)  # Pause between actions

    def _simulate_memory_leak(self, metrics):
        metrics['memory_usage'] = min(92.0, metrics['memory_usage'] + 40.0)

    def _recover_memory_leak(self):
        actions = [
            {"step": 1, "action": "Detecting memory leak source", "status": "pending"},
            {"step": 2, "action": "Analyzing memory usage patterns", "status": "pending"},
            {"step": 3, "action": "Implementing memory cleanup", "status": "pending"},
            {"step": 4, "action": "Optimizing memory allocation", "status": "pending"},
            {"step": 5, "action": "Monitoring memory stability", "status": "pending"}
        ]
        
        with self._lock:
            self.recovery_actions = actions

        for action in self.recovery_actions:
            with self._lock:
                action["status"] = "in_progress"
            time.sleep(2)
            with self._lock:
                action["status"] = "complete"
            time.sleep(1)

    def _simulate_disk_fill(self, metrics):
        metrics['disk_usage'] = min(94.0, metrics['disk_usage'] + 35.0)

    def _recover_disk_fill(self):
        actions = [
            {"step": 1, "action": "Scanning disk usage patterns", "status": "pending"},
            {"step": 2, "action": "Identifying large unnecessary files", "status": "pending"},
            {"step": 3, "action": "Implementing disk cleanup", "status": "pending"},
            {"step": 4, "action": "Optimizing storage allocation", "status": "pending"},
            {"step": 5, "action": "Verifying disk space recovery", "status": "pending"}
        ]
        
        with self._lock:
            self.recovery_actions = actions

        for action in self.recovery_actions:
            with self._lock:
                action["status"] = "in_progress"
            time.sleep(2)
            with self._lock:
                action["status"] = "complete"
            time.sleep(1)

    def get_modified_metrics(self, original_metrics):
        modified_metrics = original_metrics.copy()
        
        with self._lock:
            for fault_type, fault_info in self.active_faults.items():
                if fault_info['active']:
                    self.fault_types[fault_type]['simulate'](modified_metrics)
        
        return modified_metrics

    def get_active_faults(self):
        with self._lock:
            return {k: v['active'] for k, v in self.active_faults.items()}

    def get_recovery_actions(self):
        with self._lock:
            return self.recovery_actions

    def get_recovery_status(self):
        with self._lock:
            status = []
            for fault_type, info in self.active_faults.items():
                if info['active']:
                    if self.recovery_actions:
                        status.append(f"AI recovering from {fault_type}")
                    else:
                        status.append(f"AI analyzing {fault_type}")
            return status
