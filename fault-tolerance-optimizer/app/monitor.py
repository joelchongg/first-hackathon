import random
import numpy as np
from datetime import datetime
from .fault_injector import FaultInjector

class SystemMonitor:
    def __init__(self):
        self.fault_injector = FaultInjector()
        self.time = 0

    def collect_metrics(self):
        """Collect basic metrics"""
        self.time += 1
        
        # Generate base metrics (ensure they're floats)
        metrics = {
            'cpu_usage': float(min(98.0, max(20.0, 50.0 + 30.0 * np.sin(self.time / 10.0)))),
            'memory_usage': float(min(95.0, max(30.0, 60.0 + self.time % 20))),
            'disk_usage': float(min(90.0, max(40.0, 50.0 + random.uniform(-5.0, self.time % 15))))
        }
        
        # Apply any active faults
        return self.fault_injector.get_modified_metrics(metrics)

    def get_detailed_metrics(self):
        """Collect detailed system metrics"""
        try:
            basic_metrics = self.collect_metrics()
            
            # Add additional metrics (keeping numeric values)
            detailed_metrics = {
                'cpu_usage': basic_metrics['cpu_usage'],
                'memory_usage': basic_metrics['memory_usage'],
                'disk_usage': basic_metrics['disk_usage'],
                'process_count': float(random.randint(100, 300)),
                'network_traffic': float(random.randint(1000, 5000)),
                'uptime_hours': float(random.randint(1, 24))
            }
            
            return detailed_metrics
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }

    def inject_fault(self, fault_type, duration=30):
        """Interface to inject faults"""
        return self.fault_injector.inject_fault(fault_type, duration)

    def get_active_faults(self):
        """Get currently active faults"""
        return self.fault_injector.get_active_faults()
