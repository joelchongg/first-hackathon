# app/monitor.py
import psutil
import time
import os
import platform
import logging
from typing import Dict, Any
from collections import deque
from datetime import datetime
import numpy as np

class SystemMonitor:
    def __init__(self):
        """Initialize the system monitor"""
        # Configure logging
        self._setup_logging()
        
        # Initialize monitoring components
        self.metrics_history = deque(maxlen=100)
        self.event_history = deque(maxlen=50)
        self.active_alerts = set()
        
        # Configure thresholds
        self.thresholds = {
            'cpu_critical': 90.0,
            'cpu_warning': 70.0,
            'memory_critical': 90.0,
            'memory_warning': 70.0,
            'disk_critical': 90.0,
            'disk_warning': 80.0
        }
        
        # Initialize monitoring state
        self.is_monitoring = False
        self.last_check_time = None
        self.monitoring_interval = 2  # seconds
        self.baseline_metrics = None
        self.last_metrics = None
        self.metrics_history = deque(maxlen=100)
        
        self.logger.info("SystemMonitor initialized successfully")

    def _setup_logging(self):
        """Setup logging configuration"""
        try:
            if not os.path.exists('logs'):
                os.makedirs('logs')
                
            logging.basicConfig(
                filename='logs/monitor.log',
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger('SystemMonitor')
        except Exception as e:
            print(f"Error setting up logging: {e}")

    def start_monitoring(self):
        """Start system monitoring"""
        try:
            self.is_monitoring = True
            self.last_check_time = time.time()
            self.logger.info("System monitoring started")
            return True
        except Exception as e:
            self.logger.error(f"Error starting monitoring: {e}")
            return False

    def stop_monitoring(self):
        """Stop system monitoring"""
        try:
            self.is_monitoring = False
            self.logger.info("System monitoring stopped")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {e}")
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            metrics = self._collect_metrics()
            
            if metrics:
                # Store metrics in history
                self.metrics_history.append(metrics)
                
                # Check for alerts
                self._check_alerts(metrics)
                
                # Update last check time
                self.last_check_time = time.time()
                
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting metrics: {e}")
            return self._generate_empty_metrics()

    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect system metrics with delta calculations"""
        try:
            # Get current metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Calculate memory details
            memory_total = memory.total
            memory_available = memory.available
            memory_used = memory_total - memory_available
            memory_percent = (memory_used / memory_total) * 100
            
            # Calculate disk details
            disk_total = disk.total
            disk_used = disk.used
            disk_percent = (disk_used / disk_total) * 100
            
            current_metrics = {
                'timestamp': time.time(),
                'cpu': {
                    'usage': float(cpu_percent),
                    'user': float(psutil.cpu_times().user),
                    'system': float(psutil.cpu_times().system)
                },
                'memory': {
                    'usage': float(memory_percent),
                    'total': float(memory_total),
                    'available': float(memory_available),
                    'used': float(memory_used)
                },
                'disk': {
                    'usage': float(disk_percent),
                    'total': float(disk_total),
                    'used': float(disk_used),
                    'free': float(disk.free)
                }
            }
            
            # Calculate deltas if we have previous metrics
            if self.last_metrics:
                current_metrics['deltas'] = {
                    'memory_usage': current_metrics['memory']['usage'] - 
                                  self.last_metrics['memory']['usage'],
                    'disk_usage': current_metrics['disk']['usage'] - 
                                self.last_metrics['disk']['usage']
                }
            else:
                current_metrics['deltas'] = {
                    'memory_usage': 0.0,
                    'disk_usage': 0.0
                }
            
            # Store metrics
            self.last_metrics = current_metrics
            if not self.baseline_metrics:
                self.baseline_metrics = current_metrics.copy()
            
            # Add simplified metrics
            current_metrics.update({
                'cpu_usage': current_metrics['cpu']['usage'],
                'memory_usage': current_metrics['memory']['usage'],
                'disk_usage': current_metrics['disk']['usage']
            })
            
            return current_metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return self._generate_empty_metrics()

    def _check_alerts(self, metrics: Dict[str, Any]):
        """Check metrics against thresholds and generate alerts"""
        try:
            current_alerts = set()
            
            # Check CPU
            if metrics['cpu_usage'] >= self.thresholds['cpu_critical']:
                current_alerts.add(('cpu', 'critical'))
            elif metrics['cpu_usage'] >= self.thresholds['cpu_warning']:
                current_alerts.add(('cpu', 'warning'))
                
            # Check Memory
            if metrics['memory_usage'] >= self.thresholds['memory_critical']:
                current_alerts.add(('memory', 'critical'))
            elif metrics['memory_usage'] >= self.thresholds['memory_warning']:
                current_alerts.add(('memory', 'warning'))
                
            # Check Disk
            if metrics['disk_usage'] >= self.thresholds['disk_critical']:
                current_alerts.add(('disk', 'critical'))
            elif metrics['disk_usage'] >= self.thresholds['disk_warning']:
                current_alerts.add(('disk', 'warning'))
            
            # Log new alerts
            new_alerts = current_alerts - self.active_alerts
            for component, level in new_alerts:
                self._log_alert(component, level, metrics)
            
            # Update active alerts
            self.active_alerts = current_alerts
            
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")

    def _log_alert(self, component: str, level: str, metrics: Dict[str, Any]):
        """Log system alerts"""
        try:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'component': component,
                'level': level,
                'value': metrics.get(f'{component}_usage', 0),
                'threshold': self.thresholds[f'{component}_{level}']
            }
            
            self.event_history.append(alert)
            self.logger.warning(
                f"{level.upper()} alert: {component} usage at "
                f"{alert['value']:.1f}% (threshold: {alert['threshold']}%)"
            )
            
        except Exception as e:
            self.logger.error(f"Error logging alert: {e}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            if not self.metrics_history:
                return self._generate_empty_status()
            
            latest_metrics = self.metrics_history[-1]
            
            return {
                'timestamp': datetime.now().isoformat(),
                'metrics': latest_metrics,
                'alerts': list(self.active_alerts),
                'status': self._determine_status(latest_metrics),
                'trends': self._calculate_trends(),
                'events': list(self.event_history)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return self._generate_empty_status()

    def _determine_status(self, metrics: Dict[str, Any]) -> str:
        """Determine overall system status"""
        try:
            if any(alert[1] == 'critical' for alert in self.active_alerts):
                return 'critical'
            elif any(alert[1] == 'warning' for alert in self.active_alerts):
                return 'warning'
            return 'healthy'
            
        except Exception as e:
            self.logger.error(f"Error determining status: {e}")
            return 'unknown'

    def _calculate_trends(self) -> Dict[str, float]:
        """Calculate system metric trends"""
        try:
            if len(self.metrics_history) < 2:
                return self._generate_empty_trends()
            
            recent_metrics = list(self.metrics_history)[-10:]
            
            trends = {}
            for metric in ['cpu_usage', 'memory_usage', 'disk_usage']:
                values = [m[metric] for m in recent_metrics]
                trends[metric] = float(np.polyfit(range(len(values)), values, 1)[0])
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error calculating trends: {e}")
            return self._generate_empty_trends()

    def _generate_empty_metrics(self) -> Dict[str, Any]:
        """Generate empty metrics structure"""
        return {
            'timestamp': time.time(),
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'disk_usage': 0.0,
            'cpu': {'usage': 0.0, 'user': 0.0, 'system': 0.0, 'frequency': 0.0},
            'memory': {'usage': 0.0, 'available': 0.0, 'total': 0.0, 'swap_used': 0.0},
            'disk': {'usage': 0.0, 'free': 0.0, 'total': 0.0, 'read_bytes': 0.0, 'write_bytes': 0.0},
            'network': {'bytes_sent': 0.0, 'bytes_recv': 0.0, 'packets_sent': 0.0, 'packets_recv': 0.0},
            'system': {'process_count': 0, 'boot_time': 0.0}
        }

    def _generate_empty_status(self) -> Dict[str, Any]:
        """Generate empty status structure"""
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': self._generate_empty_metrics(),
            'alerts': [],
            'status': 'unknown',
            'trends': self._generate_empty_trends(),
            'events': []
        }

    def _generate_empty_trends(self) -> Dict[str, float]:
        """Generate empty trends structure"""
        return {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'disk_usage': 0.0
        }

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring system status"""
        return {
            'is_monitoring': self.is_monitoring,
            'last_check': self.last_check_time,
            'active_alerts': len(self.active_alerts),
            'metrics_collected': len(self.metrics_history),
            'events_logged': len(self.event_history)
        }
