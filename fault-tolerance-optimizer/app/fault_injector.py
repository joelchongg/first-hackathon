# app/fault_injector.py
import random
import threading
import time
import numpy as np
import logging
import os
from datetime import datetime
import psutil
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Any, Optional

class FaultInjector:
    def __init__(self):
        # Core components
        self.active_faults = {}
        self.recovery_actions = []
        self._lock = threading.Lock()
        self.recovery_in_progress = False
        
        # ML components
        self.scaler = StandardScaler()
        self.fault_history = []
        self.recovery_history = []
        self.max_history = 100
        
        # Fault tracking
        self.last_fault_time = {}
        self.fault_success_rate = {}
        
        # Setup logging
        self._setup_logging()
        
        # Initialize fault configurations
        self.fault_types = {
            'cpu_overload': {
                'simulate': self._simulate_cpu_overload,
                'recovery': self._recover_cpu_overload,
                'impact_factor': 1.5,
                'recovery_steps': 5,
                'metrics_affected': ['cpu_usage'],
                'cooldown': 300,  # 5 minutes
                'max_duration': 60,
                'cascade_probability': 0.3
            },
            'memory_leak': {
                'simulate': self._simulate_memory_leak,
                'recovery': self._recover_memory_leak,
                'impact_factor': 1.3,
                'recovery_steps': 4,
                'metrics_affected': ['memory_usage'],
                'cooldown': 400,
                'max_duration': 45,
                'cascade_probability': 0.25
            },
            'disk_fill': {
                'simulate': self._simulate_disk_fill,
                'recovery': self._recover_disk_fill,
                'impact_factor': 1.2,
                'recovery_steps': 3,
                'metrics_affected': ['disk_usage'],
                'cooldown': 500,
                'max_duration': 30,
                'cascade_probability': 0.2
            },
            'io_stress': {
                'simulate': self._simulate_io_stress,
                'recovery': self._recover_io_stress,
                'impact_factor': 1.4,
                'recovery_steps': 4,
                'metrics_affected': ['disk_usage', 'cpu_usage'],
                'cooldown': 350,
                'max_duration': 40,
                'cascade_probability': 0.35
            }
        }

    def _setup_logging(self):
        """Setup logging configuration"""
        try:
            if not os.path.exists('logs'):
                os.makedirs('logs')
                
            logging.basicConfig(
                filename='logs/fault_injector.log',
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger('FaultInjector')
        except Exception as e:
            print(f"Error setting up logging: {e}")

    def inject_fault(self, fault_type: str, duration: Optional[int] = None) -> bool:
        """Inject a system fault with ML-enhanced monitoring"""
        try:
            if fault_type not in self.fault_types:
                self.logger.error(f"Unknown fault type: {fault_type}")
                return False
                
            config = self.fault_types[fault_type]
            
            # Check cooldown period
            if not self._check_cooldown(fault_type):
                return False
                
            # Validate and adjust duration
            if duration is None:
                duration = config['max_duration']
            duration = min(duration, config['max_duration'])
            
            with self._lock:
                # Record fault with ML metrics
                fault_data = {
                    'active': True,
                    'start_time': time.time(),
                    'duration': duration,
                    'recovery_attempted': False,
                    'impact_metrics': {},
                    'ml_features': self._calculate_ml_features(fault_type),
                    'system_state_before': self._capture_system_state()
                }
                
                self.active_faults[fault_type] = fault_data
                self.last_fault_time[fault_type] = time.time()
                
                # Log fault injection
                self.logger.info(
                    f"Injecting fault: {fault_type}, "
                    f"duration: {duration}s, "
                    f"impact_factor: {config['impact_factor']}"
                )
            
            # Start recovery thread
            recovery_thread = threading.Thread(
                target=self._execute_recovery,
                args=(fault_type,),
                daemon=True
            )
            recovery_thread.start()
            
            # Check for cascade effects
            if random.random() < config['cascade_probability']:
                self._trigger_cascade_effects(fault_type)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error injecting fault: {e}")
            return False

    def _check_cooldown(self, fault_type: str) -> bool:
        """Check if fault type is in cooldown period"""
        try:
            if fault_type in self.last_fault_time:
                cooldown = self.fault_types[fault_type]['cooldown']
                time_since_last = time.time() - self.last_fault_time[fault_type]
                return time_since_last >= cooldown
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking cooldown: {e}")
            return False

    def _calculate_ml_features(self, fault_type: str) -> np.ndarray:
        """Calculate ML features for fault analysis"""
        try:
            base_features = {
                'cpu_overload': [1.0, 0.3, 0.1, 0.2],
                'memory_leak': [0.3, 1.0, 0.2, 0.3],
                'disk_fill': [0.1, 0.2, 1.0, 0.3],
                'io_stress': [0.2, 0.3, 0.4, 1.0]
            }
            
            features = base_features.get(fault_type, [0.0, 0.0, 0.0, 0.0])
            return self.scaler.fit_transform(np.array(features).reshape(1, -1))[0]
            
        except Exception as e:
            self.logger.error(f"Error calculating ML features: {e}")
            return np.zeros(4)

    def _capture_system_state(self) -> Dict[str, float]:
        """Capture current system state"""
        try:
            return {
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'timestamp': time.time()
            }
        except Exception as e:
            self.logger.error(f"Error capturing system state: {e}")
            return {}

    def _trigger_cascade_effects(self, primary_fault: str):
        """Trigger cascade effects based on ML analysis"""
        try:
            cascade_candidates = {
                fault_type: config
                for fault_type, config in self.fault_types.items()
                if fault_type != primary_fault
            }
            
            for fault_type, config in cascade_candidates.items():
                if random.random() < config['cascade_probability']:
                    cascade_duration = int(config['max_duration'] * 0.5)
                    self.inject_fault(fault_type, cascade_duration)
                    
                    self.logger.warning(
                        f"Cascade effect triggered: {fault_type} "
                        f"from primary fault: {primary_fault}"
                    )
                    
        except Exception as e:
            self.logger.error(f"Error triggering cascade effects: {e}")

    def _execute_recovery(self, fault_type: str):
        """Execute ML-enhanced recovery process"""
        try:
            self.logger.info(f"Starting recovery for {fault_type}")
            
            config = self.fault_types[fault_type]
            recovery_start = time.time()
            
            # Initialize recovery metrics
            recovery_metrics = {
                'fault_type': fault_type,
                'start_time': recovery_start,
                'steps_completed': 0,
                'improvements': {}
            }
            
            # Execute recovery steps
            for step in range(config['recovery_steps']):
                if not self.active_faults.get(fault_type, {}).get('active', False):
                    break
                    
                success = config['recovery'](step)
                if success:
                    recovery_metrics['steps_completed'] += 1
                
                # Monitor improvement
                current_state = self._capture_system_state()
                recovery_metrics['improvements'][step] = self._calculate_improvement(
                    fault_type, current_state
                )
                
                time.sleep(2)
            
            # Update recovery metrics
            recovery_metrics['duration'] = time.time() - recovery_start
            recovery_metrics['success'] = (
                recovery_metrics['steps_completed'] == config['recovery_steps']
            )
            
            with self._lock:
                if fault_type in self.active_faults:
                    self.active_faults[fault_type]['active'] = False
                    self.active_faults[fault_type]['recovery_metrics'] = recovery_metrics
            
            # Store recovery history
            self.recovery_history.append(recovery_metrics)
            
            # Update success rate
            self._update_success_rate(fault_type, recovery_metrics['success'])
            
            self.logger.info(
                f"Completed recovery for {fault_type}, "
                f"success: {recovery_metrics['success']}"
            )
            
        except Exception as e:
            self.logger.error(f"Recovery error: {e}")

    def _calculate_improvement(self, fault_type: str, current_state: Dict[str, float]) -> float:
        """Calculate improvement after recovery step"""
        try:
            if fault_type not in self.active_faults:
                return 0.0
                
            initial_state = self.active_faults[fault_type]['system_state_before']
            improvements = []
            
            for metric in self.fault_types[fault_type]['metrics_affected']:
                if metric in initial_state and metric in current_state:
                    initial = initial_state[metric]
                    current = current_state[metric]
                    if initial > current:
                        improvement = (initial - current) / initial
                        improvements.append(improvement)
            
            return np.mean(improvements) if improvements else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating improvement: {e}")
            return 0.0

    def _update_success_rate(self, fault_type: str, success: bool):
        """Update fault recovery success rate"""
        try:
            if fault_type not in self.fault_success_rate:
                self.fault_success_rate[fault_type] = {
                    'attempts': 0,
                    'successes': 0
                }
            
            self.fault_success_rate[fault_type]['attempts'] += 1
            if success:
                self.fault_success_rate[fault_type]['successes'] += 1
                
        except Exception as e:
            self.logger.error(f"Error updating success rate: {e}")

    def get_fault_statistics(self) -> Dict[str, Any]:
        """Get comprehensive fault statistics"""
        try:
            return {
                'active_faults': len(self.active_faults),
                'fault_history': len(self.fault_history),
                'success_rates': {
                    fault_type: {
                        'rate': stats['successes'] / stats['attempts']
                        if stats['attempts'] > 0 else 0.0,
                        'attempts': stats['attempts']
                    }
                    for fault_type, stats in self.fault_success_rate.items()
                },
                'current_faults': {
                    fault_type: {
                        'duration': time.time() - info['start_time'],
                        'recovery_attempted': info['recovery_attempted']
                    }
                    for fault_type, info in self.active_faults.items()
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting fault statistics: {e}")
            return {}

    def _simulate_cpu_overload(self) -> bool:
        """Simulate CPU overload"""
        try:
            # Create CPU load
            end_time = time.time() + 5
            while time.time() < end_time:
                _ = [i * i for i in range(10000)]
            return True
        except Exception as e:
            self.logger.error(f"Error simulating CPU overload: {e}")
            return False

    def _simulate_memory_leak(self) -> bool:
        """Simulate memory leak"""
        try:
            # Temporarily allocate memory
            temp_data = [bytearray(1024*1024) for _ in range(10)]
            time.sleep(2)
            del temp_data
            return True
        except Exception as e:
            self.logger.error(f"Error simulating memory leak: {e}")
            return False

    def _simulate_disk_fill(self) -> bool:
        """Simulate disk fill"""
        try:
            # Create temporary file
            temp_file = 'temp_fault_test.tmp'
            with open(temp_file, 'wb') as f:
                f.write(os.urandom(1024*1024))  # 1MB file
            time.sleep(2)
            os.remove(temp_file)
            return True
        except Exception as e:
            self.logger.error(f"Error simulating disk fill: {e}")
            return False

    def _simulate_io_stress(self) -> bool:
        """Simulate I/O stress"""
        try:
            # Create I/O load
            for _ in range(5):
                with open('io_test.tmp', 'wb') as f:
                    f.write(os.urandom(1024*1024))
                os.remove('io_test.tmp')
            return True
        except Exception as e:
            self.logger.error(f"Error simulating I/O stress: {e}")
            return False

    def _recover_cpu_overload(self, step: int) -> bool:
        """Recover from CPU overload"""
        try:
            time.sleep(1)  # Simulate recovery action
            return True
        except Exception as e:
            self.logger.error(f"Error recovering from CPU overload: {e}")
            return False

    def _recover_memory_leak(self, step: int) -> bool:
        """Recover from memory leak"""
        try:
            import gc
            gc.collect()
            return True
        except Exception as e:
            self.logger.error(f"Error recovering from memory leak: {e}")
            return False

    def _recover_disk_fill(self, step: int) -> bool:
        """Recover from disk fill"""
        try:
            time.sleep(1)  # Simulate recovery action
            return True
        except Exception as e:
            self.logger.error(f"Error recovering from disk fill: {e}")
            return False

    def _recover_io_stress(self, step: int) -> bool:
        """Recover from I/O stress"""
        try:
            time.sleep(1)  # Simulate recovery action
            return True
        except Exception as e:
            self.logger.error(f"Error recovering from I/O stress: {e}")
            return False

    def get_active_faults(self) -> Dict[str, bool]:
        """Get information about active faults"""
        with self._lock:
            return {k: v['active'] for k, v in self.active_faults.items()}

    def get_recovery_status(self) -> List[str]:
        """Get detailed recovery status"""
        with self._lock:
            status = []
            for fault_type, info in self.active_faults.items():
                if info['active']:
                    if info['recovery_attempted']:
                        status.append(f"Recovering from {fault_type}")
                    else:
                        status.append(f"Monitoring {fault_type}")
            return status
